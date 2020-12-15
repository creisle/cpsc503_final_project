import argparse
import os
import re
import time

import pandas
import requests

PUBMED_PUBTYPES = [
    "Adaptive Clinical Trial",
    "Address",
    "Autobiography",
    "Bibliography",
    "Biography",
    "Case Reports",
    "Classical Article",
    "Clinical Conference",
    "Clinical Study",
    "Clinical Trial",
    "Clinical Trial, Phase I",
    "Clinical Trial, Phase II",
    "Clinical Trial, Phase III",
    "Clinical Trial, Phase IV",
    "Clinical Trial Protocol",
    "Clinical Trial, Veterinary",
    "Collected Works",
    "Comparative Study",
    "Congress",
    "Consensus Development Conference",
    "Consensus Development Conference, NIH",
    "Controlled Clinical Trial",
    "Dataset",
    "Dictionary",
    "Directory",
    "Duplicate Publication",
    "Editorial",
    "Electronic Supplementary Materials",
    "English Abstract",
    "Equivalence Trial",
    "Evaluation Study",
    "Expression of Concern",
    "Festschrift",
    "Government Publication",
    "Guideline",
    "Historical Article",
    "Interactive Tutorial",
    "Interview",
    "Introductory Journal Article",
    "Journal Article",
    "Lecture",
    "Legal Case",
    "Legislation",
    "Letter",
    "Meta-Analysis",
    "Multicenter Study",
    "News",
    "Newspaper Article",
    "Observational Study",
    "Observational Study, Veterinary",
    "Overall",
    "Patient Education Handout",
    "Periodical Index",
    "Personal Narrative",
    "Portrait",
    "Practice Guideline",
    "Preprint",
    "Pragmatic Clinical Trial",
    "Publication Components",
    "Publication Formats",
    "Published Erratum",
    "Randomized Controlled Trial",
    "Research Support, American Recovery and Reinvestment Act",
    "Research Support, N.I.H., Extramural",
    "Research Support, N.I.H., Intramural",
    "Research Support, Non-U.S. Gov't Research Support, U.S. Gov't, Non-P.H.S.",
    "Research Support, U.S. Gov't, P.H.S.",
    "Retracted Publication",
    "Retraction of Publication",
    "Review",
    "Scientific Integrity Review",
    "Study Characteristics",
    "Support of Research",
    "Systematic Review",
    "Technical Report",
    "Twin Study",
    "Validation Study",
    "Video-Audio Media",
    "Webcast",
]


def relative_file(*paths):
    return os.path.join(os.path.dirname(__file__), *paths)


def fetch_review_articles_list(search_field='lang', search_term='eng'):
    """
    Use the Pubmed API to fetch a list of PMIDs that correspond to review articles

    https://pubmed.ncbi.nlm.nih.gov/help/#publication-types
    """
    base_url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi'
    results = []
    total_records = None
    max_retries = 3
    consec_errors = 0
    clean_search_term = re.sub(r'[\'":;\.\s]+', '', search_term)
    output_file = relative_file(f'../data/entrez/esearch.{search_field}.{clean_search_term}.csv')
    if os.path.exists(output_file):
        print('reading:', output_file)
        return pandas.read_csv(output_file, dtype={'PMID': 'str', search_field: 'str'})

    while total_records is None or len(results) < total_records:
        print(
            f'requesting: {base_url}?term={search_term}[{search_field}] from {len(results)} of {total_records or "?"}'
        )
        resp = None
        try:
            resp = requests.get(
                base_url,
                params={
                    'retmode': 'json',
                    'db': 'pubmed',
                    'term': f'{search_term}[{search_field}]',
                    'retmax': 100000,
                    'retstart': len(results),  # paginate
                },
            )
            resp.raise_for_status()
            resp = resp.json()
            if total_records is None:
                total_records = int(resp['esearchresult']['count'])
            results.extend(resp['esearchresult']['idlist'])
            consec_errors = 0
        except Exception as err:
            consec_errors += 1
            if consec_errors > max_retries:
                print(resp)
                raise err
            # sleep for connection resets
            time.sleep(2)
            continue
    df = pandas.DataFrame(results, columns=['PMID'])
    df[search_field] = search_term
    df.to_csv(output_file, index=False)
    return df


parser = argparse.ArgumentParser()
parser.add_argument(
    '--input_file',
    help='path to the csv file mapping PMID to PMCID. Download here: https://ftp.ncbi.nlm.nih.gov/pub/pmc/PMC-ids.csv.gz',
    default=relative_file('../data/pubmed/PMC-ids.csv'),
)
parser.add_argument(
    '--output_file',
    help='path the the CSV output file',
    default=relative_file('../data/pmc_metadata.entrez.csv'),
)
args = parser.parse_args()


print('reading:', args.input_file)
pmc_df = pandas.read_csv(
    args.input_file,
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

reviews_df = None
for pubtype in PUBMED_PUBTYPES:
    df = fetch_review_articles_list('pubtype', pubtype)
    if reviews_df is None:
        reviews_df = df
    else:
        reviews_df = pandas.concat([reviews_df, df])


pmc_df = pmc_df.merge(fetch_review_articles_list('lang', 'eng'), on=['PMID'], how='left')
pmc_df = pmc_df.merge(reviews_df, on=['PMID'], how='left')
pmc_df['lang'] = pmc_df.lang.fillna('')
pmc_df['pubtype'] = pmc_df.pubtype.fillna('')
pmc_df = (
    pmc_df.groupby(['PMCID'])
    .agg(
        {
            'lang': lambda types: ';'.join(sorted(set(types))),
            'pubtype': lambda types: ';'.join(sorted(set(types))),
        }
    )
    .reset_index()
)

print(pmc_df)
print('writing:', args.output_file)
pmc_df[['PMCID', 'lang', 'pubtype']].to_csv(args.output_file, index=False)
