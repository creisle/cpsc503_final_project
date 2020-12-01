import argparse
import os

import bconv

parser = argparse.ArgumentParser()
parser.add_argument(
    '--in_file',
    help='the input PMC NXML file',
    default="data/pmc_articles/3_Biotech/PMC4829572.nxml",
)
parser.add_argument(
    '--out_file',
    help='the output txt file',
    default="data/pmc_articles/3_Biotech/PMC4829572.nxml.txt",
)

args = parser.parse_args()

if not os.path.exists(args.in_file):
    raise FileNotFoundError(args.in_file)


nxml = bconv.load(args.in_file, fmt='nxml', mode="collection")
bconv.dump(nxml, args.out_file, fmt='txt')
