import sys
from HTSeq import GFF_Reader
import os
import click
import pandas as pd
from omstools.utils.config import CLICK_CONTEXT_SETTINGS
from omstools.utils.config import gtf_tools
try:
    import envoy
except ImportError:
    import subprocess


CURRENT_DIR = os.getcwd()
VARS = dir()


GTF_ATTR = (
    'transcript_id',
    'gene_id',
    'transcript_type',
    'gene_type',
    'gene_name',
)


def oms_lncRNA_feelnc(mrna, lncrna, dis=5000):
    '''
    run FEElnc_classifier.pl to get lncRNA position relative to mRNA
    in order to classify them.
    '''
    cmd_line = 'FEELnc_classifier.pl -i {lnc} -a {m} -w {d} -m {d}'.format(
        lnc=lncrna, m=mrna, d=dis
    )
    if 'envoy' in VARS:
        r = envoy.run(cmd_line)
        output = r.std_out
    else:
        cmd_list = cmd_line.split()
        p = subprocess.Popen(cmd_list,
                             universal_newlines=True,
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             bufsize=0,
                             cwd=CURRENT_DIR)
        output = p.communicate()[0]
    return output


def oms_lncRNA_classify(feelnc_prd, lnc_gtf, method='Luo'):
    '''
    add lncRNA class to FEElnc_classifier.pl output
    '''
    feelnc_df = pd.read_table(feelnc_prd, index_col=2)
    feelnc_best_df = feelnc_df[feelnc_df.isBest == 1]
    feelnc_best_df = feelnc_best_df.loc[:, feelnc_best_df.columns[1:]]
    lnc_class_df = pd.DataFrame([], columns=feelnc_best_df.columns)
    lnc_class_list = list()
    for eachline in GFF_Reader(lnc_gtf):
        tr_id = eachline.attr['transcript_id']
        gene_id = eachline.attr['gene_id']
        if tr_id in lnc_class_df.index:
            continue
        if tr_id in feelnc_best_df.index:
            if method == 'Luo':
                dirt, ltype, dis, subtype, loc = feelnc_best_df.loc[tr_id][3:]
                lnc_class = get_luo_code(dirt, subtype, loc)
                lnc_class_list.append(lnc_class)
                lnc_class_df.loc[tr_id] = feelnc_best_df.loc[tr_id]
            else:
                sys.exit('undefined classification method.')
        else:
            class_detail = ['--' for each in lnc_class_df.columns]
            class_detail[0] = gene_id
            lnc_class_list.append('lincRNA')
            lnc_class_df.loc[tr_id] = class_detail
    lnc_class_df.loc[:, 'classification'] = lnc_class_list
    lnc_class_df.index.name = feelnc_best_df.index.name
    return lnc_class_df


def oms_add_lncRNA_type(lncrna, tucp, lnc_class_df, output):
    merged_gtf = '{o}.tmp'.format(o=output)
    gtf_tools['func_merge_sort_gtf_files']([lncrna, tucp], merged_gtf)
    gene_dict = dict()
    with open(merged_gtf) as gtf_inf:
        for gene, tr_objs in gtf_tools['func_parse_gtf'](gtf_inf, GTF_ATTR):
            tr_type_set = set()
            for each_tr in tr_objs:
                tr_id = each_tr.attrs["transcript_id"]
                if tr_id in lnc_class_df.index:
                    tr_type = lnc_class_df.loc[tr_id, 'classification']
                else:
                    tr_type = 'TUCP'
                each_tr.attrs['transcript_biotype'] = tr_type
                tr_type_set.add(tr_type)
            gene_type = gtf_tools['func_get_gene_type'](tr_type_set)
            for each_tr in tr_objs:
                each_tr.attrs['gene_biotype'] = gene_type
                gene_dict.setdefault(gene, []).append(each_tr)
    with open(output, 'w') as output_inf:
        for gene in gene_dict:
            for tr_obj in gene_dict[gene]:
                tr_features = tr_obj.to_gtf_features()
                for each_feature in tr_features:
                    output_inf.write('{l_out}\n'.format(
                        l_out=str(each_feature)))
    os.remove(merged_gtf)


def get_luo_code(*fee_loc):

    genic_dict = {
        'antisense': 'X',
        'sense': 'S',
        'overlapping': 'P',
        'nested': 'I',
        'containing': 'O',
        'divergent': 'H',
        'convergent': 'T',
        'same_strand': '',
        'downstream': 'D',
        'upstream': 'U',
        'intronic': 'I',
        'exonic': 'E',
    }

    code = [genic_dict[each] for each in fee_loc]
    code = ''.join(code)

    modify_dict = {
        'XHU': 'XH',
        'XTD': 'XT',
    }

    return modify_dict.get(code, code)


@click.command(context_settings=CLICK_CONTEXT_SETTINGS)
@click.option(
    '-m',
    '--mrna',
    type=click.Path(dir_okay=False, exists=True),
    help='mRNA gtf file.',
    required=True
)
@click.option(
    '-l',
    '--lncrna',
    type=click.Path(dir_okay=False, exists=True),
    help='lncRNA gtf file.',
    required=True
)
@click.option(
    '-t',
    '--tucp',
    type=click.Path(dir_okay=False),
    help='TUCP gtf file.',
    default='',
)
@click.option(
    '-d',
    '--distance',
    type=click.INT,
    help='Size of the window around the lncRNA to compute classification.',
    default=5000
)
@click.option(
    '-o',
    '--out_dir',
    type=click.Path(file_okay=False),
    default=CURRENT_DIR,
    help='Directory to store classification output.'
)
def main(mrna, lncrna, tucp, out_dir, distance):
    '''classify lncRNA according to it's position relative to mRNA
    '''
    # check result existence
    lnc_class_out = os.path.join(out_dir, 'lncRNA.classification.txt')
    lnc_class_gtf = os.path.join(out_dir, 'lncRNA.classification.gtf')
    if os.path.exists(lnc_class_out):
        click.echo('oms_lncRNA_classify will not run, output exists!',
                   color='orange')
    else:
        # run FEELnc_classifier
        feelnc_out = os.path.join(out_dir, 'feelnc.classification.txt')
        if not os.path.exists(feelnc_out):
            click.echo('run FEELnc_classifier.', color='blue')
            output = oms_lncRNA_feelnc(mrna, lncrna, distance)
            with open(feelnc_out, 'w') as out_inf:
                out_inf.write(output)
        else:
            click.echo('FEELnc_classifier will not run, output exists!',
                       color='orange')
        # run lncRNA classify
        click.echo('run oms_lncRNA_classify!', color='blue')
        lnc_class_df = oms_lncRNA_classify(feelnc_out, lncrna)
        lnc_class_df.to_csv(lnc_class_out, sep='\t')
        oms_add_lncRNA_type(lncrna, tucp, lnc_class_df, lnc_class_gtf)


if __name__ == '__main__':
    main()
