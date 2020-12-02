from glob import glob
import os
import random


batches = []

SAMPLE_SIZE = os.environ.get('SAMPLE_SIZE')
SAMPLE_SIZE = int(SAMPLE_SIZE) if SAMPLE_SIZE else None
if SAMPLE_SIZE:
    print(f'sub-sampling XML folders to a max of last {SAMPLE_SIZE} articles per folder')

for batch in glob('data/pmc_articles/*'):
    if os.path.isdir(batch):
        batch_id = batch.split('/')[-1]
        batches.append(batch_id)

        if glob(os.path.join(batch, '*.nxml')):
            batches.append(batch_id)

        # if SAMPLE_SIZE and SAMPLE_SIZE < len(articles):
        #     articles = articles[len(articles) - SAMPLE_SIZE - 1:]

        # for article in articles:
        #     batch_articles.setdefault(batch_id, []).append(article)
print('found', len(batches), 'batches')



rule all:
    input: expand('data/pmc_articles/{batch_id}.readability_scores.csv', batch_id=batches)

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



# rule compute_tacco_scores:
#     input: 'data/pmc_articles/{batch_id}'
#     output: 'data/pmc_articles/{batch_id}.tacco2.csv'
#     shell: 'TODO'
