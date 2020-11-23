import argparse
import os

import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt


def relative_file(*paths):
    os.path.join(os.path.dirname(__file__), *paths)


parser = argparse.ArgumentParser()
parser.add_argument(
    'readability_scores',
    help='path to the tsv file containing the readability scores output',
    default=relative_file('../results/textstat.results.tsv')),
)
args = parser.parse_args()

df = pd.read_csv(args.output_file, sep='\t')


def plot_gunning_fog(df, filename):
    curr_df = df[df.measure == 'gunning_fog']
    markers = [
        (17, 18, 'College graduate'),
        (16, 17, 'College senior'),
        (15, 16, 'College junior'),
        (14, 15, 'College sophomore'),
        (13, 14, 'College freshman'),
        (12, 13, 'High school senior'),
        (11, 12, 'High school junior'),
        (10, 11, 'High school sophomore'),
        (9, 10, 'High school freshman'),
        (8, 9, 'Eighth grade'),
        (7, 8, 'Seventh grade'),
        (6, 7, 'Sixth grade'),
    ]

    plt.figure()
    # sns.set_style('whitegrid')
    colors = sns.color_palette("Paired", len(markers) + 1)
    ax = sns.boxenplot(data=curr_df, y='score', hue='section')
    ax.set_ylim((5, None))
    _, xmax = ax.get_xlim()
    for (m_start, m_end, m_label), color in zip(markers, colors):
        plt.axhspan(m_start, m_end, color=color, alpha=0.5, zorder=0)
        plt.text(
            xmax,
            (m_start + m_end) / 2,
            f'- {m_label}',
            verticalalignment='center',
            fontsize='small',
        )

    ax.figure.savefig(filename, bbox_inches='tight')
    plt.close()


df = pd.read_csv(args.output_file, sep='\t')

for measure, score_min, score_max in [
    ('flesch_reading_ease', 0, 100),
    ('flesch_kincaid_grade', 0, 100),
    ('gunning_fog', 5, None),
    ('automated_readability_index', 5, None),
    ('coleman_liau_index', 5, None),
]:
    print(measure)
    if measure == 'gunning_fog':
        plot_gunning_fog(df, f'results/textstat.results.{measure}.png')
        continue
    fig = plt.figure()
    sns.set_style('whitegrid')
    curr_df = df[df.measure == measure]
    ax = sns.boxenplot(data=curr_df, y='score', hue='section')
    ax.set_ylim((score_min, score_max))
    ax.figure.savefig(f'results/textstat.results.{measure}.png')
    plt.close()
