import argparse
import os

import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt
from scipy import stats

MIN_TEXT_SIZE = 250
MAX_TEXT_SIZE = 25000


def relative_file(*paths):
    return os.path.join(os.path.dirname(__file__), *paths)


def read_csv(filename):
    print('reading:', filename)
    return pd.read_csv(filename)


parser = argparse.ArgumentParser()
parser.add_argument(
    '--readability_scores',
    help='path to the csv file containing the readability scores output',
    default=relative_file('../data/pmc_articles.all_readability_scores.csv'),
)
parser.add_argument('--output', default=relative_file('../results/pmc_plots'))
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
parser.add_argument(
    '--pubtypes',
    help='path to the metadata file which defines the publication types',
    default=relative_file('../data/pmc_metadata.entrez.csv'),
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


df = read_csv(args.readability_scores)
df['PMCID'] = df.filename.str.split('.').str[0]
country_df = read_csv(args.country)
df = df.merge(country_df, on=['PMCID'], how='inner')
df['is_english'] = df.country.isin({'US', 'UK', 'Canada', 'Australia'})
size_df = read_csv(args.size)
size_df = size_df[(size_df.text_size >= MIN_TEXT_SIZE) & (size_df.text_size <= MAX_TEXT_SIZE)]
df = df.merge(size_df, how='inner', on=['PMCID'])

# table: scores eng vs not

ttest_scores = []
for measure in sorted(df.measure.unique()):
    eng_df = df[(df.measure == measure) & (df.is_english == True)]
    other_df = df[(df.measure == measure) & (df.is_english == False)]
    ttest = stats.ttest_ind(eng_df.score, other_df.score, equal_var=False)
    ttest_scores.append((measure, ttest.statistic, ttest.pvalue))

ttest_df = pd.DataFrame(ttest_scores, columns=['measure', 'ttest_statistic', 'ttest_pvalue'])
table = (
    df.merge(ttest_df, on=['measure'])
    .groupby(['measure', 'is_english'])
    .agg({'score': ['mean', 'median', 'std'], 'PMCID': 'nunique'})
    .reset_index()
)
print(table.to_csv(index=False))

# plot scores eng vs not
g = sns.FacetGrid(df, col="measure", col_wrap=3)
g.map_dataframe(sns.boxenplot, x="is_english", y="score", palette='tab10')
g.set(yscale='log')
savefig(g, 'pmc.textstat.eng.boxplot.png')

# plot scores vs country
g = sns.FacetGrid(df, col="measure", col_wrap=3)
g.map_dataframe(sns.boxenplot, x="score", y="country", palette='tab10')
g.set(xscale='log')
savefig(g, 'pmc.textstat.country.boxplot.png')

# plot scores vs text size
g = sns.FacetGrid(df, col="measure", col_wrap=3)
g.map_dataframe(sns.boxenplot, x="text_size", y="score", hue='is_english', palette='tab10')
g.set(xscale='log')
savefig(g, f'pmc.textstat.text_size.scatter.png')
