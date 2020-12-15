"""
Plot Annotation Overlap Data
"""
import argparse
import os
import re

import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt


def relative_file(name):
    return os.path.join(os.path.dirname(__file__), name)


parser = argparse.ArgumentParser()
parser.add_argument(
    '--input_file',
    help='path to output GCDC csv file results from calculating the LDA coherence scores',
    default=relative_file('../data/pmc_articles.scibert_annotations.csv'),
)
parser.add_argument(
    '--output',
    help='path to output directory to put the png files',
    default=relative_file('../results/pmc_plots'),
)
args = parser.parse_args()

print('reading:', args.input_file)
df = pd.read_csv(args.input_file)

shared_concepts = (
    df.groupby(['token_lemma'])
    .agg({'token_freq': 'sum', 'PMCID': 'nunique'})
    .reset_index()
    .sort_values(['PMCID'], ascending=False)
)
print(shared_concepts)
print('total concepts', shared_concepts.shape[0])
