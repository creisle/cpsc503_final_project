from glob import glob
import os
import random


batches = []

DATA_DIR = 'data/pmc_articles'
batches_file = 'batches.txt'

# NOTE: This is to avoid having to use conda. Could probably replace with a conda env eventually if preferred
# This is unnecessary if your cluster head node is running the same OS version as the worker nodes
PYTHON_ENV = os.path.join(os.getcwd(), 'venv/bin/activate')
if not os.path.exists(PYTHON_ENV):
    print(f'can\'t find {PYTHON_ENV}')
    PYTHON_ENV = ''
else:
    PYTHON_ENV = f'source {PYTHON_ENV}; which python; '


print('gathering batches')
for batch in glob(f'{DATA_DIR}/*/SCIBERT_ANNOTATIONS.COMPLETE'):
    batch_id = batch.split('/')[-2]
    batches.append(batch_id)

print('found', len(batches), 'batches')
batches = sorted(batches)

# SNAKE MAKE rules below

rule all:
    input: 'data/pmc_articles.scibert_annotations.csv'


rule collect_annotations:
    resources:
        cpus=1,
        mem_mb=7900,
        time_limit='2-0',
        log_dir='slurm_logs'
    input: 'data/pmc_articles/{batch_id}/SCIBERT_ANNOTATIONS.COMPLETE'
    output: 'data/pmc_articles/{batch_id}.scibert_annotations.csv'
    log: 'data/pmc_articles/{batch_id}.scibert_annotations.snakemake.txt'
    shell: PYTHON_ENV + 'python scripts/collect_annotations.py'
        + ' --input_dir "data/pmc_articles/{wildcards.batch_id}"'
        + ' --output_file "{output}" &> "{log}"'


rule merge_annotations:
    resources:
        cpus=1,
        mem_mb=7900,
        time_limit='2-0',
        log_dir='slurm_logs'
    input: expand('data/pmc_articles/{batch_id}.scibert_annotations.csv', batch_id=batches)
    output: 'data/pmc_articles.scibert_annotations.csv'
    log: 'data/pmc_articles.snakemake.merge_scibert_annotations.log'
    shell: PYTHON_ENV + ' python scripts/merge_csv_files.py'
        + ' --input_files_pattern "data/pmc_articles/*.scibert_annotations.csv"'
        + ' --output_file {output} &> {log}'
