import argparse
import os
import re

import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt

MIN_TEXT_SIZE = 1000
MAX_TEXT_SIZE = 100000


def relative_file(*paths):
    return os.path.join(os.path.dirname(__file__), *paths)


def read_csv(filename):
    print('reading:', filename)
    return pd.read_csv(filename)


parser = argparse.ArgumentParser()

parser.add_argument(
    '--country',
    help='path to the metadata file which defines the country groupings',
    default=relative_file('../data/pmc_metadata.affiliations.countries.csv'),
)
parser.add_argument(
    '--size',
    help='path to the metadata file which defines the text sizes',
    default=relative_file('../data/pmc_articles.text_size.csv'),
)
parser.add_argument('--output', default=relative_file('../results/pmc_plots'))

args = parser.parse_args()


def savefig(ax, plot_name):
    plot_path = os.path.join(args.output, plot_name)
    print('writing:', plot_path)
    try:
        ax.figure.savefig(plot_path, bbox_inches='tight')
    except AttributeError:
        ax.savefig(plot_path, bbox_inches='tight')
    plt.close()


df = read_csv(args.size)
sns.set_style('whitegrid')
fig_df = (
    df.groupby('text_size')
    .agg({'PMCID': 'count'})
    .reset_index()
    .rename(columns={'PMCID': 'freq'})
    .sort_values('freq', ascending=False)
)
ax = sns.lineplot(data=fig_df, x='text_size', y='freq')
ax.set_yscale('log')
ax.set_xscale('log')

plt.axvline(MIN_TEXT_SIZE)
plt.axvline(MAX_TEXT_SIZE)
savefig(ax, 'pmc.text_size.lineplot.png')

country_df = read_csv(args.country)
df = df.merge(country_df, on=['PMCID'], how='left')
df['country'] = df.country.replace('Australia', 'AUS')
df['country'] = df.country.replace('Canada', 'CAN')
df['country'] = df.country.replace('South America', 'SA')
df['country'] = df.country.replace('Europe', 'EU')
df = df.rename(columns={'country': 'region'})
ax = sns.catplot(kind='count', data=df, x='region')
ax.set(yscale='log')

savefig(ax, 'pmc.country.histogram.png')
