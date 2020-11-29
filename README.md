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

## Getting Data

There is a `get_data.sh` script which has bash commands to download some of the required data. It
can be run as follows

```bash
bash scripts/get_data.sh
```

This will create the `data/pubmed` directory and download the PMC to PMID ID mapping
