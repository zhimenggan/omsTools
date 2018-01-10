from __future__ import print_function
import click
import os


CPU = 4
BASH_HEADER = '#!/bin/bash'


def slurm_launch(script, cpu):
    os.system('omsrunone.sh {s} {c}'.format(
        s=script, c=cpu))


def pfam_cmd(fasta, cpu, out):
    return 'pfam_scan.pl -fasta {f} -cpu {c} > {o}'.format(
        f=fasta, c=cpu, o=out)


def add_content(fp, *args):
    with open(fp, 'w') as file_inf:
        for eachline in args:
            file_inf.write('{line}\n'.format(line=eachline))


def save_make_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)


@click.command()
@click.argument('split_dir')
@click.argument('pfam_dir')
def main(split_dir, pfam_dir):
    split_dir = os.path.abspath(split_dir)
    pfam_dir = os.path.abspath(pfam_dir)
    script_dir = os.path.join(split_dir, 'script')
    map(save_make_dir, [script_dir, pfam_dir])
    split_files = os.listdir(split_dir)
    for each_file in split_files:
        each_file_path = os.path.join(split_dir, each_file)
        if not os.path.isfile(each_file_path):
            continue
        each_pfam_out = os.path.join(
            pfam_dir, '{f}.pfamA'.format(f=each_file))
        each_script = os.path.join(
            script_dir, '{f}.sh'.format(f=each_file))
        each_cmd = pfam_cmd(each_file_path, CPU, each_pfam_out)
        add_content(each_script, BASH_HEADER, each_cmd)
        slurm_launch(each_script, CPU)


if __name__ == '__main__':
    main()
