import argparse
import os

import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt


def relative_file(*paths):
    return os.path.join(os.path.dirname(__file__), *paths)


def read_csv(filename):
    print('reading:', filename)
    return pd.read_csv(filename)


parser = argparse.ArgumentParser()
parser.add_argument(
    '--input_file',
    help='path to input file containing the journal grouped clusters',
    default=relative_file(
        '../results/scibert/pmc.concepts.cluster_journal_groups.t250_25000.c2.j30.csv'
    ),
)
parser.add_argument(
    '--annotations',
    help='path to input file containing the individual annotations',
    default=relative_file('../data/pmc_articles.scibert_annotations.csv'),
)
parser.add_argument(
    '--output',
    help='path to output directory to put the png files',
    default=relative_file('../results/scibert'),
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
df = df.merge(
    (
        df[['cluster', 'PMCID']]
        .groupby(['cluster'])
        .agg({'PMCID': 'sum'})
        .reset_index()
        .rename(columns={'PMCID': 'articles per cluster'})
    ),
    on=['cluster'],
)
df = df.merge(
    (
        df[['cluster', 'section']]
        .groupby(['cluster'])
        .agg({'section': 'nunique'})
        .reset_index()
        .rename(columns={'section': 'journals per cluster'})
    ),
    on=['cluster'],
)
# drop clusters of 1
df = df[df['articles per cluster'] > 1]
df['single journal fraction'] = df.PMCID / df['articles per cluster']

print(df.sort_values(['articles per cluster']))

fig_df = (
    df[['articles per cluster', 'cluster', 'single journal fraction']]
    .sort_values(['single journal fraction'], ascending=False)
    .drop_duplicates(['cluster'], keep='first')
)
fig_df['single journal fraction'] = fig_df['single journal fraction'].apply(lambda x: round(x, 1))
fig = sns.histplot(
    data=fig_df,
    x='articles per cluster',
    multiple='stack',
    hue='single journal fraction',
    kde=False,
    stat='count',
    log_scale=(True, True),
)
# fig.set(xscale='log', yscale='log')
savefig(fig, 'pmc.concepts.articles-per-cluster.png')

fig_df = (
    df[['cluster', 'single journal fraction']]
    .sort_values(['single journal fraction'], ascending=False)
    .drop_duplicates(['cluster'], keep='first')
)
fig = sns.distplot(fig_df['single journal fraction'], kde=False)
savefig(fig, 'pmc.concepts.journal-fraction-per-cluster.png')

fig = sns.distplot(df['journals per cluster'], kde=False)
fig.set(yscale='log')
savefig(fig, 'pmc.concepts.journal-count-per-cluster.png')

fig_df = (
    df.groupby(['section'])
    .agg({'cluster': 'nunique'})
    .reset_index()
    .rename(columns={'cluster': 'clusters per journal', 'section': 'journal'})
)
fig = sns.distplot(fig_df['clusters per journal'], kde=False)
fig.set(yscale='log')
savefig(fig, 'pmc.concepts.cluster-count-per-journal.png')

concepts_df = read_csv(args.annotations)
concepts_df['concept'] = concepts_df.token_type + '|' + concepts_df.token_lemma
concepts_df = (
    concepts_df.groupby(['token_type', 'token_lemma'])
    .agg({'PMCID': 'nunique'})
    .reset_index()
    .rename(columns={'PMCID': 'articles per concept'})
)
print(concepts_df)
fig = sns.histplot(
    data=concepts_df,
    x='articles per concept',
    hue='token_type',
    multiple='stack',
    stat='count',
    kde=False,
    log_scale=(True, True),
)
savefig(fig, 'pmc.concepts.histogram.by-type.png')
