from glob import glob
import os


batches = []
articles = []
batch_articles = {}

for batch in glob('data/pmc_articles/*'):
    if os.path.isdir(batch):
        for article in glob(os.path.join(batch, '*.xml')):
            batches.append(article.split('/')[-2])
            articles.append(re.sub(r'\.n?xml$', '', article.split('/')[-1]))
            batch_articles.setdefault(batches[-1], []).append(article)
print('found', len(batches), 'articles')


rule all:
    input: expand('data/pmc_articles/{batch_id}.readability_scores.csv', batch_id=batches)


def get_batch_article(wildcards):
    return [a for a in batch_articles[wildcards.batch_id] if wildcards.article_id in a]

rule convert_nxml_to_text:
    input: get_batch_article
    output: 'data/pmc_articles/{batch_id}/{article_id}.xml.txt'
    shell: 'python scripts/bioc_converter.py --in_file {input} --out_file {output}'


def get_batch_text(wildcards):
    return [re.sub(r'\.n?xml$', '.xml.txt',a) for a in batch_articles[wildcards.batch_id]]

rule compute_text_stats:
    input: get_batch_text
    output: 'data/pmc_articles/{batch_id}.readability_scores.csv'
    shell: 'python scripts/compute_readability_scores.py'
        + ' --text_glob data/pmc_articles/{wildcards.batch_id}/*.xml.txt'
        + ' --output_file {output}'
