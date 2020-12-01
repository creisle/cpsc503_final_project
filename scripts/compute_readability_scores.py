"""
outputs csv file with the following columns: 'section', 'filename', 'measure', 'score'
"""
import argparse
import glob
import os

import pandas as pd
import textstat

# ORKG-NLP OA-STM data
stats = []


def relative_file(*paths):
    return os.path.join(os.path.dirname(__file__), *paths)


parser = argparse.ArgumentParser()
parser.add_argument(
    '--text_glob',
    help='glob pattern to use in finding text files. MUST be quoted to avoid expanding beforehand',
    default=relative_file('../data/orkg-nlp/STEM-ECR-v1.0/scientific-entity-annotations/*/*.txt'),
)
parser.add_argument(
    '--output_file',
    help='path the the TSV output file',
    default=relative_file('../results/textstat.results.tsv'),
)
args = parser.parse_args()


input_files = glob.glob(args.text_glob)
if not input_files:
    raise FileNotFoundError(f'pattern must have at least one input file: {args.text_glob}')
for filename in input_files:
    section = filename.split('/')[-2]
    basename = filename.split('/')[-1]
    print(f'reading: {filename}')
    content = ''
    with open(filename, 'r') as fh:
        content = fh.read()

    stats.append([section, basename, 'flesch_reading_ease', textstat.flesch_reading_ease(content)])
    stats.append(
        [section, basename, 'flesch_kincaid_grade', textstat.flesch_kincaid_grade(content)]
    )
    stats.append([section, basename, 'gunning_fog', textstat.gunning_fog(content)])
    stats.append(
        [
            section,
            basename,
            'automated_readability_index',
            textstat.automated_readability_index(content),
        ]
    )
    stats.append([section, basename, 'coleman_liau_index', textstat.coleman_liau_index(content)])

df = pd.DataFrame(
    stats,
    columns=['section', 'filename', 'measure', 'score'],
)

with open(args.output_file, 'w') as fh:
    fh.write(df.to_csv(index=False))
