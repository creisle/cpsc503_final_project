from glob import glob
import os


rule all:
    input: 'data/pmc_metadata.affiliations.countries.csv'
    # input: expand('data/pmc_articles/{batch_id}/{article_id}.txt', zip, batch_id=batches, article_id=articles)

rule download_pmid_mapping:
    output: 'data/pubmed/PMC-ids.csv'
    shell: '''
        mkdir -p data/pubmed;
        cd data/pubmed;
        wget https://ftp.ncbi.nlm.nih.gov/pub/pmc/PMC-ids.csv.gz;
        gunzip PMC-ids.csv.gz
    '''

rule get_article_review_stats:
    input: rules.download_pmid_mapping.output
    output: 'data/pmc_metadata.csv'
    shell: 'python scripts/get_article_review_stats.py --input_file {input} --output_file {output}'


rule get_affiliations:
    input: rules.get_article_review_stats.output
    output: 'data/pmc_metadata.affiliations.csv'
    shell: 'python scripts/get_affiliations.py --input_file {input} --output_file {output}'


rule get_countries:
    input: rules.get_affiliations.output,
        rules.get_article_review_stats.output
    output: 'data/pmc_metadata.affiliations.countries.csv'
    shell: 'python scripts/get_countries_from_affiliations.py'
        + ' --affiliations_file {input[0]}'
        + ' --metadata_file {input[1]}'
        + ' --output_file {output}'
