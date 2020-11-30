from glob import glob
import os


batches = []
articles = []
batch_articles = {}

for batch in glob('data/pmc_articles/*'):
    if os.path.isdir(batch):
        for article in glob(os.path.join(batch, '*.xml')):
            batches.append(article.split('/')[-2])
            articles.append(re.sub(r'\.xml$', '', article.split('/')[-1]))
            batch_articles.setdefault(batches[-1], []).append(articles[-1])
print('found', len(batches), 'articles')


rule all:
    input: expand('data/pmc_articles/{batch_id}.readability_scores.csv', batch_id=batches)

rule convert_nxml_to_text:
    input: 'data/pmc_articles/{batch_id}/{article_id}.xml'
    output: 'data/pmc_articles/{batch_id}/{article_id}.xml.txt'
    shell: 'python scripts/bloc_converter.py --in_file {input} --out_file {output}'


def get_batch_articles(wildcards):
    return batch_articles[wildcards.batch_id]

rule compute_text_stats:
    input: get_batch_articles
    output: 'data/pmc_articles/{batch_id}.readability_scores.csv'
    shell: 'python scripts/compute_readability_scores'
        + ' --text_glob data/pmc_articles/{wildcards.batch_id}/*.xml.txt'
        + ' --output_file {output}'
