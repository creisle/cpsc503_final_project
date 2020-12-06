from glob import glob
import os
import random


batches = []

DATA_DIR= 'data/pmc_articles'
batches_file = 'batches.txt'

# NOTE: This is to avoid having to use conda. Could probably replace with a conda env eventually if preferred
# This is unnecessary if your cluster head node is running the same OS version as the worker nodes
PYTHON_ENV = os.path.join(os.getcwd(), 'venv/bin/activate')
if not os.path.exists(PYTHON_ENV):
    print(f'can\'t find {PYTHON_ENV}')
    PYTHON_ENV = ''
else:
    PYTHON_ENV = f'source {PYTHON_ENV}; which python; '


# This improves performance by avoiding globbing 15k directories each time
if os.path.exists(batches_file):
    print('reading:', batches_file)
    with open(batches_file, 'r') as fh:
        batches = [p.strip() for p in fh.readlines() if p.strip()]
else:
    print('gathering batches')
    for batch in glob(f'{DATA_DIR}/*'):
        if os.path.isdir(batch):
            batch_id = batch.split('/')[-1]

            if os.path.exists(os.path.join(batch, 'NXML_TXT.COMPLETE') )or glob(os.path.join(batch, '*.nxml')):
                batches.append(batch_id)
    print('writing:', batches_file)
    with open(batches_file, 'w') as fh:
        fh.write('\n'.join(batches))
print('found', len(batches), 'batches')
batches = sorted(batches)

# SNAKE MAKE rules below

rule all:
    input: expand('data/pmc_articles/{batch_id}.lda_coherence.csv', batch_id=batches)

rule convert_nxml_to_text:
    resources:
        cpus=1,
        mem_mb=7900,
        time_limit='2-0',
        log_dir='slurm_logs'
    output: 'data/pmc_articles/{batch_id}/NXML_TXT.COMPLETE'
    log: 'data/pmc_articles/{batch_id}.nxml_to_txt.snakemake.txt'
    shell: PYTHON_ENV + ' python scripts/convert_nxml_to_txt.py '
        + ' --in_dir "data/pmc_articles/{wildcards.batch_id}"'
        + ' --stamp NXML_TXT.COMPLETE'
        + ' &> "{log}"'

rule compute_text_stats:
    resources:
        cpus=1,
        mem_mb=7900,
        time_limit='2-0',
        log_dir='slurm_logs'
    input: rules.convert_nxml_to_text.output
    output: 'data/pmc_articles/{batch_id}.readability_scores.csv'
    log: 'data/pmc_articles/{batch_id}.readability_scores.snakemake.txt'
    shell: PYTHON_ENV + ' python scripts/compute_readability_scores.py'
        + ' --text_glob "data/pmc_articles/{wildcards.batch_id}/*.nxml.txt"'
        + ' --output_file "{output}" &> "{log}"'

rule merge_text_stats:
    resources:
        cpus=1,
        mem_mb=7900,
        time_limit='2-0',
        log_dir='slurm_logs'
    input: expand('data/pmc_articles/{batch_id}.readability_scores.csv', batch_id=batches)
    output: 'data/pmc_articles.all_readability_scores.csv'
    log: 'data/pmc_articles.snakemake.merge_text_stats.log'
    shell: PYTHON_ENV + ' python scripts/merge_csv_files.py'
        + ' --input_files_pattern "data/pmc_articles/*.readability_scores.csv"'
        + ' --output_file {output} &> {log}'

rule compute_lda_coherence:
    resources:
        cpus=1,
        mem_mb=7900,
        time_limit='2-0',
        log_dir='slurm_logs'
    input: rules.convert_nxml_to_text.output
    output: 'data/pmc_articles/{batch_id}.lda_coherence.csv'
    log: 'data/pmc_articles/{batch_id}.lda_coherence.snakemake.txt'
    shell: PYTHON_ENV + ' python scripts/lda_calc.py'
        + ' --input_files_pattern "data/pmc_articles/{wildcards.batch_id}/*.nxml.txt"'
        + ' --out_file "{output}" &> "{log}"'

rule compute_gcdc_lda_coherence:
    output: 'data/gcdc.lda_coherence.csv'
    log: 'logs/gcdc.lda_coherence.snakemake.txt'
    shell: PYTHON_ENV + 'python scripts/lda_calc.py'
        + ' --input_files_pattern "data/GCDC_rerelease/*csv"'
        + ' --gcdc'
        + ' --out_file {output}'
        + ' &> {log}'
