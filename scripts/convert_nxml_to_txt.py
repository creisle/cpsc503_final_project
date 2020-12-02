import argparse
import glob
import os

import bconv

parser = argparse.ArgumentParser()
parser.add_argument(
    '--in_dir',
    help='the input PMC NXML file',
    default="data/pmc_articles/3_Biotech/PMC4829572.nxml",
)
parser.add_argument(
    '--stamp',
    help='the name of the complete stamp to add to the directory',
    default="NXML_TXT.COMPLETE",
)

args = parser.parse_args()

if not os.path.exists(args.in_dir) or not os.path.isdir(args.in_dir):
    raise FileNotFoundError(args.in_dir)

for in_file in glob.glob(os.path.join(args.in_dir, '*.nxml')):
    out_file = f'{in_file}.txt'
    if not os.path.exists(out_file):
        nxml = bconv.load(in_file, fmt='nxml', mode="collection")
        print('writing:', out_file)
        bconv.dump(nxml, out_file, fmt='txt')

with open(os.path.join(args.in_dir, args.stamp), 'w') as fh:
    fh.write('')
