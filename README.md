# cpsc503_final_project

## Data Sources

- [NCBI PMC Journal List](https://www.ncbi.nlm.nih.gov/pmc/journals/?format=csv)

## Getting Started

Create a virtual environment using python 3.6 or higher

```bash
python -m venv venv
source venv/bin/activate
pip install -U setuptools pip
```

Install dependencies from the requirements.txt file

```bash
pip install -r requirements.txt
```

Run the scripts. Most scripts should give a help menu if passed the `-h` flag

for example

```bash
python scripts/compute_readability_scores.py -h
```

## Analysis

The analysis pipeline is split into 2 stages: metadata collection and stats computation.

### Metadata collection

Proir to running the metadata collection. A mySQL instance of the [pubmed knowledge graph](https://www.nature.com/articles/s41597-020-0543-2#Sec11)
[database dump](http://er.tacc.utexas.edu/datasets/ped) should be up and running so it can
be pulled from.

```bash
gunzip < pubmed19.sql.gz | mysql -h <HOSTNAME> pubmed_kg -p
```

The metadata can be generated with the following

```bash
source venv/bin/activate
snakemake -s metadata.snakefile --jobs 1
```

### Text Conversion and Statistics

The PMC xml files should be uncompressed in a file with the following structure: `*/*.xml`. The
top-level directory can then be symlinked under the data directory relative to this repository.

```bash
cd data
ln -s /path/to/folder/above/xml/folders pmc_articles
```

Whereas the text conversion and downstream analysis can be done with the second pipeline file

```bash
source venv/bin/activate
snakemake -s text_stats.snakefile --jobs 10
```

This will create text files for each NXML file as well as complete stamp files in the
following pattern

| File                   | Path                                                          |
| ---------------------- | ------------------------------------------------------------- |
| complete stamp         | data/pmc_articles/{batch_id}/NXML_TXT.COMPLETE                |
| log file               | data/pmc_articles/{batch_id}.readability_scores.snakemake.txt |
| readability scores csv | data/pmc_articles/{batch_id}.readability_scores.csv           |
| text file conversion   | data/pmc_articles/{batch_id}/{article_id}.nxml.txt            |
| log file               | data/pmc_articles/{batch_id}.nxml_to_txt.snakemake.txt        |
