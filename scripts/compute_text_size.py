import glob

import pandas as pd

lengths = []

for filename in glob.glob('data/pmc_articles/*/*.nxml.txt'):
    article_id = filename.split('/')[-1].split('.')[0]
    with open(filename, 'r') as fh:
        lengths.append((article_id, len(fh.read())))

df = pd.DataFrame(lengths, columns=['PMCID', 'text_size'])

df.to_csv('data/pmc_articles.text_size.csv', index=False)
