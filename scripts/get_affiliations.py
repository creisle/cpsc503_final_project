import argparse
import os
import re
from typing import Dict

import pandas as pd
import pymysql
from sqlalchemy import create_engine


def relative_file(*paths):
    return os.path.join(os.path.dirname(__file__), *paths)


parser = argparse.ArgumentParser()
parser.add_argument('--mysql_host', default='mysql01')
parser.add_argument('--mysql_db_name', default='pubmed_kg')
parser.add_argument('--mysql_user', default=os.environ['USER'])
parser.add_argument(
    '--mysql_password', default=os.environ['PASS'], required=not (os.environ.get('PASS', ''))
)
parser.add_argument('--input_file', default=relative_file('../data/pubmed/PMC-ids.csv'))
parser.add_argument(
    '--output_file', default=relative_file('../data/pmc_metadata.affiliations.all.csv')
)
args = parser.parse_args()

metadata_df = pd.read_csv(args.input_file)
metadata_df = metadata_df[~metadata_df.PMID.isnull()]
db_connection = create_engine(
    f'mysql+pymysql://{args.mysql_user}:{args.mysql_password}@{args.mysql_host}/{args.mysql_db_name}?charset=utf8'
)

affiliations_df = pd.read_csv(args.output_file) if os.path.exists(args.output_file) else None

review_ids = sorted(set(metadata_df.PMID.unique()) - set(affiliations_df.PMID.unique()))
chunk_size = 25000
chunk_index = 0
print(
    f'found {affiliations_df.shape[0]} existing entries. Loading {len(review_ids)} remaining entries'
)
while chunk_index < len(review_ids):
    # Create a new record
    pmid_chunk = ', '.join(str(i) for i in review_ids[chunk_index : chunk_index + chunk_size])
    sql = f'''
    SELECT DISTINCT PMID,
        Affiliation
    FROM A13_AffiliationList
    WHERE
        Au_Order = 1
        AND Affiliation_Order = 1
        AND PMID IN ({pmid_chunk})
    '''

    print(
        'fetching metadata for',
        chunk_index,
        'to',
        chunk_index + chunk_size,
        'of',
        len(review_ids),
    )
    df = pd.read_sql(sql, con=db_connection)
    print('found', df.shape[0], 'metadata entries')
    if affiliations_df is None:
        affiliations_df = df
    else:
        affiliations_df = pd.concat([affiliations_df, df])
    chunk_index += chunk_size
    print('re-writing:', args.output_file)
    affiliations_df.to_csv(args.output_file, index=False)
