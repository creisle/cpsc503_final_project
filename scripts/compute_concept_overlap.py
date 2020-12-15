import argparse
import os
import re
import sys
from glob import glob
from typing import Dict, Set

import numpy as np
import pandas as pd
import seaborn as sns
import spacy
from matplotlib import pyplot as plt
from scipy.cluster.hierarchy import dendrogram
from scipy.sparse import csr_matrix
from sklearn.cluster import DBSCAN, AgglomerativeClustering
from sklearn.metrics import pairwise_distances


def relative_file(*paths):
    return os.path.join(os.path.dirname(__file__), *paths)


def read_csv(filepath):
    print('reading:', filepath)
    return pd.read_csv(filepath)


MIN_TEXT_SIZE = 250  # 250
MAX_TEXT_SIZE = 25000
MIN_ARTICLES_PER_CONCEPT = 2
MIN_ARTICLES_PER_JOURNAL = 30  # 30


parser = argparse.ArgumentParser()
parser.add_argument(
    '--input_file',
    help='csv file with annotations data',
    default=relative_file('../data/pmc_articles.scibert_annotations.csv'),
)
parser.add_argument(
    '--sizes',
    help='csv file with text sizes',
    default=relative_file('../data/pmc_articles.text_size.csv'),
)
parser.add_argument(
    '--output',
    help='path the the directory to output plots to',
    default=relative_file('../results/scibert'),
)
parser.add_argument(
    '--max_jobs', default=1, help='maximum number of processes to consume in parallel', type=int
)
args = parser.parse_args()


sns.set_style('whitegrid')


def savefig(ax, plot_name):
    plot_path = os.path.join(args.output, plot_name)
    print('writing:', plot_path)
    try:
        ax.figure.savefig(plot_path, bbox_inches='tight')
    except AttributeError:
        ax.savefig(plot_path, bbox_inches='tight')
    plt.close()


df = read_csv(args.input_file)
# TODO: REMOVE THIS
# df = df[df.token_type == 'Method']
print(f'data size: {df.shape[0]}')
# filter by text size
text_sizes_df = read_csv(args.sizes)
text_sizes_df = text_sizes_df[
    (text_sizes_df.text_size >= MIN_TEXT_SIZE) & (text_sizes_df.text_size <= MAX_TEXT_SIZE)
]
df = df[~df.token_lemma.isnull()]
df = df.merge(text_sizes_df, on=['PMCID'])

# filter by min articles per journal
journal_counts = (
    df.groupby('section')
    .agg({'PMCID': 'nunique'})
    .reset_index()
    .rename(columns={'PMCID': 'journal_article_count'})
)
df = df.merge(journal_counts, on=['section'])
print(f'data size (text size filtered): {df.shape[0]}')
df = df[df.journal_article_count >= MIN_ARTICLES_PER_JOURNAL]
print(f'data size (filtered on journal has >= {MIN_ARTICLES_PER_JOURNAL} articles): {df.shape[0]}')

TOTAL_ARTICLES = df.PMCID.nunique()
# embed the concepts as a vocab vector
token_lemmas = (
    df.groupby(['token_lemma'])
    .agg({'PMCID': 'nunique'})
    .reset_index()
    .rename(columns={'PMCID': 'freq'})
)
token_lemmas['percent_of_articles'] = token_lemmas.freq / TOTAL_ARTICLES
print(token_lemmas.sort_values(['percent_of_articles'], ascending=False))

# plot the annotations by number of articles they are found in
ax = sns.displot(data=token_lemmas.freq)
ax.set(yscale='log')
savefig(ax, 'pmc.concepts_freq.dist.png')

# plot concepts vs text length
temp_df = (
    df.groupby(['PMCID', 'text_size'])
    .agg({'token_lemma': 'nunique'})
    .reset_index()
    .rename(columns={'token_lemma': 'concepts', 'text_size': 'text size (characters)'})
)
ax = sns.relplot(kind='scatter', data=temp_df, y='concepts', x='text size (characters)')
ax.set(yscale='log', xscale='log')
savefig(ax, 'pmc.concepts_by_text_size.png')

# plot the number of concepts per article
temp_df = (
    df.groupby(['PMCID'])
    .agg({'token_lemma': 'nunique'})
    .reset_index()
    .rename(columns={'token_lemma': 'concepts'})
)
temp_df = (
    temp_df.groupby(['concepts'])
    .agg({'PMCID': 'nunique'})
    .reset_index()
    .rename(columns={'PMCID': 'articles'})
)
ax = sns.relplot(kind='line', data=temp_df, x='concepts', y='articles')
ax.set(yscale='log', xscale='log')
savefig(ax, 'pmc.concepts_per_article.png')


# plot the annotations by type of tokens that are generated per article
temp_df = (
    df.groupby(['token_type', 'PMCID'])
    .agg({'token_lemma': 'count'})
    .reset_index()
    .rename(columns={'token_lemma': 'freq', 'token_type': 'concept type'})
)
ax = sns.boxenplot(data=temp_df, x='concept type', y='freq')
ax.set(yscale='log')
savefig(ax, 'pmc.concepts.type_per_article.png')

total_vocab_size = token_lemmas.shape[0]

# drop low frequency concepts
df['concept'] = df.token_type + df.token_lemma
concepts_count_df = (
    df.groupby('concept')
    .agg({'PMCID': 'nunique'})
    .reset_index()
    .rename(columns={'PMCID': 'concept_articles_count'})
)
df = df.merge(concepts_count_df, on=['concept'], how='inner')
df = df[df.concept_articles_count >= MIN_ARTICLES_PER_CONCEPT]
print(f'data size (dropped low freq concepts): {df.shape[0]}')

concepts_per_article = (
    df.groupby(['PMCID'])
    .agg({'concept': 'count'})
    .reset_index()
    .rename(columns={'concept': 'article_concept_count'})
)
print(concepts_per_article.sort_values('article_concept_count', ascending=False))
# now drop any articles that do not share concepts with other articles
print('concepts', df['concept'].nunique())
print('articles', TOTAL_ARTICLES)


concept_list = sorted(df.concept.unique())
concept_mapping = {c: i for i, c in enumerate(concept_list)}

article_concepts = (
    df.groupby(['PMCID'])
    .agg({'concept': lambda concepts: [concept_mapping[c] for c in concepts]})
    .reset_index()
    .sort_values('PMCID')
)

article_list = article_concepts.PMCID.tolist()
article_mapping = {p: i for i, p in enumerate(article_list)}
print(
    'generated concept mapping for',
    len(concept_mapping),
    'concepts and',
    len(article_mapping),
    'articles',
)

embeddings = np.zeros((len(article_mapping), len(concept_mapping)))
for i, concept_indices in enumerate(article_concepts.concept.tolist()):
    embeddings[i][concept_indices] = 1

total_concepts = len(concept_mapping)


def article_distance(x, y):
    return total_concepts - x.dot(y)


model = AgglomerativeClustering(
    linkage='average',
    affinity='precomputed',
    distance_threshold=total_concepts - 1,
    n_clusters=None,
)
print('computing the distance matrix')
distance_matrix = pairwise_distances(embeddings, metric=article_distance, n_jobs=args.max_jobs)
print('computing clusters')
model.fit(distance_matrix)

assert model.labels_.size == len(article_list)
clusters_df = pd.DataFrame(
    np.array([np.array(article_list), model.labels_]).transpose(), columns=['PMCID', 'cluster']
)
settings_suffix = (
    f't{MIN_TEXT_SIZE}_{MAX_TEXT_SIZE}.c{MIN_ARTICLES_PER_CONCEPT}.j{MIN_ARTICLES_PER_JOURNAL}'
)
output_clusters_file = os.path.join(
    args.output, f'pmc.concepts.cluster_labels.{settings_suffix}.csv'
)
print('writing:', output_clusters_file)
clusters_df.to_csv(output_clusters_file, index=False)

clusters_df = clusters_df.merge(df, on=['PMCID'])
print(
    'writing:',
    os.path.join(
        args.output,
        f'pmc.concepts.cluster_journal_groups.{settings_suffix}.csv',
    ),
)
clusters_df.groupby(['cluster', 'section']).agg({'PMCID': 'count'}).reset_index().rename(
    {'PMCID': 'freq'}
).sort_values('cluster').to_csv(
    os.path.join(args.output, f'pmc.concepts.cluster_journal_groups.{settings_suffix}.csv'),
    index=False,
)
