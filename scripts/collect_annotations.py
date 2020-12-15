import argparse
import os
import re
import sys
from glob import glob

import pandas as pd
import seaborn as sns
import spacy
from matplotlib import pyplot as plt

nlp = spacy.load(
    'en_core_web_md'
)  # Use the same model they use for post-processing in the scibert/concepts code


def relative_file(*paths):
    return os.path.join(os.path.dirname(__file__), *paths)


def simplify_text(text):
    return ' '.join(
        [
            t.lemma_
            for t in nlp(text)
            if (not t.is_stop or t.is_upper) and not t.like_num and not t.pos_ == 'PUNCT'
        ]
    )


def read_ann_file(filename):
    print('reading:', filename)
    rows = []
    with open(filename, 'r') as fh:
        for line in fh.readlines():
            m = re.match(r'(T\d+)\s+(\w+)\s+\d+\s+\d+\s+(.*)$', line)
            rows.append((m.group(1), m.group(2), m.group(3)))
    return pd.DataFrame(rows, columns=['token_id', 'token_type', 'token_text'])


parser = argparse.ArgumentParser()
parser.add_argument(
    '--input_dir', help='directory containing the .nxml.txt.ann files', required=True
)
parser.add_argument('--output_file', help='path the the CSV output file', required=True)
args = parser.parse_args()
input_files = glob(f'{args.input_dir}/*.nxml.txt.ann')

print(f'found {len(input_files)} annotation files')
results_df = pd.DataFrame(
    [], columns=['PMCID', 'section', 'token_type', 'token_lemma', 'token_freq']
)
processed = set()

if os.path.exists(args.output_file):
    print('reading:', args.output_file)
    results_df = pd.read_csv(args.output_file)
    processed.update(results_df.PMCID.unique())


for annotations_file in input_files:
    article_id = os.path.basename(annotations_file).split('.')[0]
    section = os.path.basename(os.path.dirname(annotations_file))
    try:
        df = read_ann_file(annotations_file)
        df['PMCID'] = article_id
        df['section'] = section
        df['token_lemma'] = df.token_text.apply(simplify_text)

        df = (
            df.groupby(['PMCID', 'section', 'token_type', 'token_lemma'])
            .agg({'token_id': 'count'})
            .reset_index()
            .rename(columns={'token_id': 'token_freq'})
        )

        results_df = pd.concat([results_df, df])
    except Exception as err:
        print(err, file=sys.stderr)

print('writing:', args.output_file)
results_df.to_csv(args.output_file, index=False)
