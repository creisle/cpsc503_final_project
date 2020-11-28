import argparse
import os

import pandas
import requests


def relative_file(*paths):
    return os.path.join(os.path.dirname(__file__), *paths)


def fetch_review_articles_list():
    """
    Use the Pubmed API to fetch a list of PMIDs that correspond to review articles

    https://pubmed.ncbi.nlm.nih.gov/help/#publication-types
    """
    base_url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi'
    results = []
    total_records = None
    while total_records is None or len(results) < total_records:
        print('requesting:', base_url, 'from', len(results), 'of', total_records or '?')
        resp = requests.get(
            base_url,
            params={
                'retmode': 'json',
                'db': 'pubmed',
                'term': 'Review[Publication Type]',
                'retmax': 100000,
                'retstart': len(results),  # paginate
            },
        ).json()
        if total_records is None:
            total_records = int(resp['esearchresult']['count'])
        results.extend(resp['esearchresult']['idlist'])
    df = pandas.DataFrame(results, columns=['PMID'])
    df['pubtype'] = 'review'
    return df


parser = argparse.ArgumentParser()
parser.add_argument(
    '--pmc_pubmed_mapping',
    help='path to the csv file mapping PMID to PMCID. Download here: https://ftp.ncbi.nlm.nih.gov/pub/pmc/PMC-ids.csv.gz',
    default=relative_file('../data/pubmed/PMC-ids.csv'),
)
parser.add_argument(
    '--output_file',
    help='path the the CSV output file',
    default=relative_file('../data/pmc_metadata.csv'),
)
args = parser.parse_args()


print('reading:', args.pmc_pubmed_mapping)
pmc_df = pandas.read_csv(
    args.pmc_pubmed_mapping,
    dtype={
        'Journal Title': 'string',
        'ISSN': 'string',
        'eISSN': 'string',
        'Year': 'string',
        'Volume': 'string',
        'Issue': 'string',
        'Page': 'string',
        'DOI': 'string',
        'PMCID': 'string',
        'PMID': 'string',
        'Manuscript Id': 'string',
        'Release Date': 'string',
    },
)
pmc_df = pmc_df[~pandas.isnull(pmc_df.PMID)]
pmc_df = pmc_df[~pandas.isnull(pmc_df.PMCID)]

reviews_df = fetch_review_articles_list()
print('there are', reviews_df.shape[0], 'review articles in pubmed')
pmc_df = pmc_df.merge(reviews_df, how='left', on=['PMID'])
print('there are', pmc_df[pmc_df.pubtype == 'review'].shape[0], 'review articles in PMC')


print('writing:', args.output_file)
pmc_df[['PMID', 'PMCID', 'pubtype', 'Journal Title', 'Year']].to_csv(args.output_file, index=False)
