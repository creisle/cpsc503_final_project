import argparse
import os
import re

import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt

MIN_TEXT_SIZE = 250
MAX_TEXT_SIZE = 25000

df = pd.read_csv('data/pmc_articles.text_size.csv')

sns.set_style('whitegrid')
df = (
    df.groupby('text_size')
    .agg({'PMCID': 'count'})
    .reset_index()
    .rename(columns={'PMCID': 'freq'})
    .sort_values('freq', ascending=False)
)
plt.figure()
ax = sns.lineplot(data=df, x='text_size', y='freq')
# ax.set(xscale='log', xlim=(1, 100000))
ax.set_yscale('log')
ax.set_xscale('log')
plt.axvline(MIN_TEXT_SIZE)
plt.axvline(MAX_TEXT_SIZE)
ax.figure.savefig('results/pmc.text_size.lineplot.png')
plt.close()

print('total', df.freq.sum())
print('selected', df[(df.text_size >= MIN_TEXT_SIZE) & (df.text_size <= MAX_TEXT_SIZE)].freq.sum())
