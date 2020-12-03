import argparse
from glob import glob

import pandas as pd

parser = argparse.ArgumentParser()
parser.add_argument(
    '--input_files_pattern',
    help='the glob pattern for the input csv files to be merged',
    required=True,
)
parser.add_argument(
    '--output_file', help='the name of the file to output the merge as', required=True
)
args = parser.parse_args()

merge_df = None

for input_file in glob(args.input_files_pattern):
    print('reading:', input_file)
    df = pd.read_csv(input_file)
    if merge_df is None:
        merge_df = df
    else:
        merge_df = pd.concat([merge_df, df])

print('writing:', args.output_file)
merge_df.to_csv(args.output_file, index=False)
