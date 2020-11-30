import argparse
import os
import re
from typing import List

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

accepted_tags = [
    'conclusions',
    'conclusion',
    'discussion',
    'introduction',
    'abstract',
]

excluded_tags = [
    'electronic supplementary material',
    'supplementary material',
    'supplement',
    'methods',
    'materials',
    'materials and methods',
    'results',
    'discussion and results',
    'results and discussion',
]

section_header_max_tokens = 3

nxml = bconv.load(args.in_file, fmt=args.format, mode="collection")

sections: List[List[str]] = []
headers: List[str] = []

for document in nxml:
    for section in document:
        header_tokens = section[0].text.strip().split(' ')
        if len(header_tokens) > section_header_max_tokens and sections:
            # stay in last section
            sections[-1].extend([s.text for s in section])
        else:
            # start new section
            sections.append([s.text for s in section])
            headers.append(' '.join(header_tokens).lower())

# check required tags are present
if not any([h in headers for h in ['conclusions', 'discussion', 'conclusion']]):
    raise ValueError(f'missing a required discussion/conclusions section ({headers})')

if 'abstract' not in headers:
    raise ValueError(f'missing abstract ({headers})')

if 'introduction' not in headers:
    raise ValueError(f'missing introduction ({headers})')

with open(args.out_file, 'w') as fh:
    fh.write(''.join(sections[0]) + '\n\n')  # title
    for header, section in list(zip(headers, sections))[1:]:
        if header in accepted_tags:
            fh.write(''.join(section))
        elif header in excluded_tags:
            continue
        else:
            raise NotImplementedError(f'unexpected header value ({header})')
    fh.write('\n')
