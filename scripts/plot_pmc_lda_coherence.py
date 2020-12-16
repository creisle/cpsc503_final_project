import argparse
import os
import re

import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt
from scipy import stats

MIN_TEXT_SIZE = 1000
MAX_TEXT_SIZE = 100000


def relative_file(*paths):
    return os.path.join(os.path.dirname(__file__), *paths)


def read_csv(filename):
    print('reading:', filename)
    return pd.read_csv(filename)


parser = argparse.ArgumentParser()
parser.add_argument(
    '--output', help='path the the output directory', default=relative_file('../results')
)
parser.add_argument(
    '--countries',
    help='path the the country metadata',
    default=relative_file('../data/pmc_metadata.affiliations.countries.csv'),
)
parser.add_argument(
    '--size',
    help='path the the text size metadata',
    default=relative_file('../data/pmc_articles.text_size.csv'),
)
parser.add_argument(
    '--pubtype',
    help='path the the publication type metadata',
    default=relative_file('../data/pmc_metadata.entrez.csv'),
)
parser.add_argument(
    '--scores',
    help='path the the LDA scores data',
    default=relative_file('../data/pmc_articles.lda_coherence.csv'),
)
args = parser.parse_args()
sns.set_style('whitegrid')


def savefig(ax, plot_name):
    plot_name = os.path.join(args.output, plot_name)
    print('writing:', plot_name)
    try:
        ax.figure.savefig(plot_name, bbox_inches='tight')
    except AttributeError:
        ax.savefig(plot_name, bbox_inches='tight')
    plt.close()


loc_df = read_csv(args.countries)[['PMCID', 'country']]
pubtype_df = read_csv(args.pubtype)
pubtype_df = pubtype_df[pubtype_df.lang == 'eng']
text_size_df = read_csv(args.size)

df = read_csv(args.scores)
df['PMCID'] = df.filename.str.split('.').str[0]
df = df.merge(loc_df, on=['PMCID'], how='inner')
df = df.merge(pubtype_df, on=['PMCID'], how='inner')
df = df.merge(text_size_df.copy(), on=['PMCID'], how='inner')
df['is_english'] = df.country.isin({'US', 'UK', 'Canada', 'Australia'})
df['short_text'] = df.text_size < MIN_TEXT_SIZE
df['text_size_bin'] = df['text_size'].apply(lambda x: round(x, -2))

ax = sns.relplot(kind='scatter', data=df, x='text_size', y='score', hue='is_english')

plt.axvline(MIN_TEXT_SIZE)
plt.axvline(MAX_TEXT_SIZE)
ax.set(xscale='log')
savefig(ax, 'pmc.lda_coherence.text_size.scatter.png')

# now drop low text size
df = df[(df.text_size >= MIN_TEXT_SIZE) & (df.text_size <= MAX_TEXT_SIZE)].copy()
print(df[(df.score == 1) & (df.text_size >= 1000)])


# create stats for sheets output
ttest = stats.ttest_ind(df[df.is_english].text_size, df[~df.is_english].text_size, equal_var=False)
ttest_scores = [('text_size', ttest.statistic, ttest.pvalue)]
ttest = stats.ttest_ind(df[df.is_english].score, df[~df.is_english].score, equal_var=False)
ttest_scores.append(('lda_coherence', ttest.statistic, ttest.pvalue))
ttest_scores = pd.DataFrame(ttest_scores, columns=['measure', 'ttest_statistic', 'ttest_pvalue'])
ttest_df = (
    df.groupby(['is_english'])
    .agg(
        {
            'score': ['mean', 'median', 'std'],
            'PMCID': 'nunique',
        }
    )
    .reset_index()
)
ttest_df.columns = [col[1] if len(col) > 1 else ''.join(col) for col in ttest_df.columns.values]
ttest_df['measure'] = 'lda_coherence'
temp_df = (
    df.groupby(['is_english'])
    .agg(
        {
            'text_size': ['mean', 'median', 'std'],
            'PMCID': 'nunique',
        }
    )
    .reset_index()
)
temp_df.columns = [col[1] if len(col) > 1 else ''.join(col) for col in temp_df.columns.values]
temp_df['measure'] = 'text_size'
ttest_df = pd.concat([ttest_df, temp_df])
ttest_df = ttest_df.merge(ttest_scores, on=['measure'])

print(ttest_df)

ax = sns.catplot(kind='box', data=df, y='score', x='is_english')
savefig(ax, 'pmc.lda_coherence.score.boxplot.png')

ax = sns.displot(data=df, x='score', hue='is_english', multiple='stack')
savefig(ax, 'pmc.lda_coherence.eng.hist.png')

ax = sns.boxenplot(data=df, x='score', y='country')
savefig(ax, 'pmc.lda_coherence.country.boxplot.png')

ax = sns.boxenplot(data=df, x='text_size', y='country')
ax.set(xscale='log')
savefig(ax, 'pmc.text_size.country.boxplot.png')

high_freq_pubtypes = df.groupby(['pubtype']).agg({'PMCID': 'count'}).reset_index()
high_freq_pubtypes = set(high_freq_pubtypes[high_freq_pubtypes.PMCID >= 1000].pubtype.unique())
ax = sns.boxenplot(data=df[df.pubtype.isin(high_freq_pubtypes)], x='score', y='pubtype')
savefig(ax, 'pmc.lda_coherence.pubtype.boxplot.png')

ax = sns.boxenplot(data=df[df.pubtype.isin(high_freq_pubtypes)], x='text_size', y='pubtype')
ax.set(xscale='log')
savefig(ax, 'pmc.text_size.pubtype.boxplot.png')

print(df[df.score == 1])
journal_counts_df = (
    df.groupby(['section'])
    .agg({'PMCID': 'nunique'})
    .reset_index()
    .rename(columns={'PMCID': 'total_article_count'})
)
outliers_df = (
    df[df.score == 1]
    .groupby(['section'])
    .agg({'score': 'mean', 'text_size': 'mean', 'PMCID': 'nunique'})
    .reset_index()
    .rename(
        columns={
            'score': 'score_mean',
            'text_size': 'text_size_mean',
            'PMCID': 'article_outlier_count',
        }
    )
    .merge(journal_counts_df, on=['section'])
)
outliers_df['percent_outliers'] = (
    outliers_df.article_outlier_count / outliers_df.total_article_count
)
print(outliers_df.sort_values(['percent_outliers'], ascending=False))
outliers_file = os.path.join(args.output, 'pmc.lda_coherence.outliers.csv')
print('writing:', outliers_file)
outliers_df.to_csv(outliers_file, index=False)
ax = sns.displot(data=df, x='score', hue='is_english', multiple='stack')
savefig(ax, 'pmc.lda_coherence.hist.png')
