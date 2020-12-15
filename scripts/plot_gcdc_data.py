"""
Plot LDA coherence vs GCDC expert and non-expert scoring of coherence
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
    default=relative_file('../data/gcdc.lda_coherence.csv'),
)
parser.add_argument(
    '--output',
    help='path to output directory to put the png files',
    default=relative_file('../results/gcdc_plots'),
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


print('reading:', args.input_file)
df = pd.read_csv(args.input_file)
df['group'] = df.filename.apply(lambda f: re.sub(r'_(test|train).csv$', '', f))
print(df)

# plot label agreement
df['label_difference'] = df['labelM'] - df['labelA']
labels_df = (
    df.groupby(['label_difference', 'group'])
    .agg({'text_id': 'count'})
    .reset_index()
    .rename(columns={'text_id': 'freq'})
)
ax = sns.barplot(data=labels_df, x='label_difference', y='freq', hue='group')
savefig(ax, 'gcdc.labels_agreement_annotators_vs_experts.png')

# plot lda vs annotated label
labela_df = df[['group', 'text_id', 'labelA', 'score']].rename(columns={'labelA': 'label'})
labela_df['label_type'] = 'A'
labelm_df = df[['group', 'text_id', 'labelM', 'score']].rename(columns={'labelM': 'label'})
labelm_df['label_type'] = 'M'
scores_df = pd.concat([labela_df, labelm_df])
ax = sns.violinplot(data=scores_df, x='label', y='score', hue='label_type')
savefig(ax, 'gcdc.lda_vs_annotator_label.png')

# plot the text sizes
df = (
    df.groupby('text_size')
    .agg({'text_id': 'count'})
    .reset_index()
    .rename(columns={'text_id': 'freq'})
    .sort_values('freq', ascending=False)
)
ax = sns.lineplot(data=df, x='text_size', y='freq')
savefig(ax, 'gcdc.text_size.lineplot.png')
