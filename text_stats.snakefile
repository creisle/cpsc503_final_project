from glob import glob
import os
import random


batches = []

DATA_DIR= 'data/pmc_articles'
batches_file = 'batches.txt'

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



rule all:
    input: 'data/pmc_articles.all_readability_scores.csv'

rule convert_nxml_to_text:
    output: 'data/pmc_articles/{batch_id}/NXML_TXT.COMPLETE'
    shell: 'python scripts/convert_nxml_to_txt.py '
        + ' --in_dir "data/pmc_articles/{wildcards.batch_id}"'
        + ' --stamp NXML_TXT.COMPLETE'
        + ' &> "data/pmc_articles/{wildcards.batch_id}.nxml_to_txt.snakemake.txt"'

rule compute_text_stats:
    input: 'data/pmc_articles/{batch_id}/NXML_TXT.COMPLETE'
    output: 'data/pmc_articles/{batch_id}.readability_scores.csv'
    shell: 'python scripts/compute_readability_scores.py'
        + ' --text_glob "data/pmc_articles/{wildcards.batch_id}/*.nxml.txt"'
        + ' --output_file "{output}" &> "data/pmc_articles/{wildcards.batch_id}.readability_scores.snakemake.txt"'

rule merge_text_stats:
    input: expand('data/pmc_articles/{batch_id}.readability_scores.csv', batch_id=batches)
    output: 'data/pmc_articles.all_readability_scores.csv'
    log: 'data/pmc_articles.snakemake.merge_text_stats.log'
    shell: 'python scripts/merge_csv_files.py'
        + ' --input_files_pattern "data/pmc_articles/*.readability_scores.csv"'
        + ' --output_file {output} &> {log}'

# rule compute_tacco_scores:
#     input: 'data/pmc_articles/{batch_id}'
#     output: 'data/pmc_articles/{batch_id}.tacco2.csv'
#     shell: 'TODO'
