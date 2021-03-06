# omsTools

### A Tool Box for NGS analysis
[![Build Status](https://travis-ci.org/bioShaun/omsTools.svg?branch=master)](https://travis-ci.org/bioShaun/omsTools)

-----

omsTools is a collection of scripts for NGS (mainly for RNAseq) analysis.

Currently it includes following scripts:

Name | Function |
--------------------| ----------------------------------------|
oms_lncRNA_classify |Classify lncRNA according to its relative location to mRNA|
oms_gtf_split| Split gtf file according to its field or attribute|
oms_transcript_feature|Extract basic information of gene/transcript/exon/intron from gtf file|
oms_gtf2bed|Convert gtf to bed12 and bed6(including tss, exon and intron feature)|
oms_kill|Kill job by job name in linux|

## Installation

A number of scripts will be added to omsTools not long. My suggestion is to install omsTools in a virtual environment, so that you could keep up with the updating.

Create a venv folder and activate the environment.

```bash
cd /path/to/your/environment/
mkdir om004_venv
virtualenv om004_venv
. om004_venv/bin/activate
```


Download source code.
```bash
cd /path/to/your/download/
git clone https://github.com/bioShaun/omsTools.git
```

Install omsTools.
```bash
cd /path/to/your/download/omsTools
pip install -e .
```

Update omsTools.
```bash
# remember to activate your virtual environment first.
cd /path/to/your/download/omsTools
git pull origin master
pip install -e .
```

## Usage

After installation, run `omstools` to find out all the available tools and their description. Input following command will output the usage of the specific script you need.

```bash
name_of_script -h
```
 
## Acknowledgement

- Two import modules in this project gtf and transcript are from AssemblyLine by mkiyer
