import argparse
import os
import re
from typing import Dict

import pandas as pd
import pymysql
from sqlalchemy import create_engine


def relative_file(*paths):
    return os.path.join(os.path.dirname(__file__), *paths)


def clean_affiliation(affiliation):
    affiliation = affiliation.strip()
    affiliation = re.sub(r'\.$', '', affiliation)
    affiliation = re.sub(r'\s*\d+(\-\d+)?\s*$', '', affiliation)
    affiliation = re.sub(r'\.$', '', affiliation)
    return affiliation.strip()


def parse_country(aff):
    for country in countries:
        for alias in countries[country]:
            try:
                if aff.endswith(alias) and (
                    len(alias) == len(aff) or aff[-1 * len(alias) - 1] == ' '
                ):
                    return country
            except IndexError:
                pass
    return ''


parser = argparse.ArgumentParser()
parser.add_argument('--metadata_file', default=relative_file('../data/pmc_metadata.csv'))
parser.add_argument(
    '--affiliations_file', default=relative_file('../data/pmc_metadata.affiliations.csv')
)
parser.add_argument(
    '--output_file', default=relative_file('../data/pmc_metadata.affiliations.countries.csv')
)
args = parser.parse_args()


df = pd.read_csv(args.affiliations_file)
metadata_df = pd.read_csv(args.metadata_file)

countries = {
    'US': [
        'Alabama, Birmingham',
        'Austin',
        'Baltimore, Maryland',
        'Baltimore',
        'Berkeley',
        'Bethesda, Maryland',
        'Bethesda, Md',
        'Bethesda, MD',
        'Boston, Massachusetts',
        'Boston',
        'CA',
        'California, Davis',
        'California, Irvine',
        'California',
        'Chicago, IL',
        'Connecticut',
        'Dallas',
        'Durham, NC',
        'Fairbanks',
        'Houston, TX',
        'Houston',
        'Illinois, Chicago',
        'Illinois, Urbana',
        'Iowa City',
        'Jackson',
        'Los Angeles',
        'Massachusetts, Amherst',
        'Michigan, Ann Arbor',
        'Minneapolis',
        'New Haven, CT',
        'New Jersey',
        'New York, Buffalo',
        'New York',
        'North Carolina',
        'NY',
        'Oklahoma City',
        'Pennsylvania',
        'Philadelphia, PA',
        'Philadelphia',
        'Portland',
        'San Francisco',
        'Seattle',
        'South Carolina, Charleston',
        'Tennessee',
        'Texas',
        'U.S.A',
        'U.S',
        'UCLA School of Medicine',
        'United States',
        'Virginia, Richmond',
        'Washington, Seattle',
        'Wisconsin, Madison',
        'Wisconsin, Milwaukee',
        'Washington, D.C',
        'Kansas City',
        'Boston, MA',
        'Detroit, Michigan',
        'Omaha',
        'Charlottesville',
        'Baltimore, MD',
        'Chicago',
        'Florida, Tampa',
        'Illinois',
        'Ohio',
        'Toledo',
        'Pasadena',
        'Detroit, MI',
        'Denver',
        'Little Rock',
        'Washington, DC',
        'Georgia',
        'Santa Barbara',
        'Michigan',
        'Bloomington',
        'Raleigh',
        'Detroit',
        'Honolulu',
        'Memphis',
        'California, Santa Cruz',
        'Tampa',
        'Kentucky',
        'St. Louis',
        'Indianapolis',
        'California, Santa Cruz',
        'Washington',
        'Salt Lake City',
        'Tucson',
        'Atlanta, GA',
        'New Orleans',
        'Cleveland, OH',
        'St. Louis, MO',
        'Burlington',
        'Maryland',
        'Florida',
        'Minnesota',
        'Massachusetts',
        'San Diego',
        'Indianapolis, IN',
        'Indiana',
        'Pittsburgh, PA',
        'Knoxville',
        'Stony Brook',
        'San Antonio',
        'Ann Arbor',
        'Augusta',
        'California, Oakland',
        'New Haven, Conn',
        'Colorado, Boulder',
    ],
    'UK': [
        'Cambridge',
        'England',
        'Great Britain',
        'London',
        'Scotland',
        'U.K',
        'UK',
        'United Kingdom',
    ],
    'Canada': ['Canada', 'Vancouver', 'Toronto, ON', 'Quebec'],
    'Europe': [
        'Germany',
        'Deutschland',
        'Netherlands',
        'Italy',
        'Sweden',
        'Norway',
        'Austria',
        'Wien',
        'Athens',
        'Glasgow',
        'Finland',
        'Liverpool',
        'Bristol Royal Infirmary',
        'France',
        'Czechoslovakia',
        'Modena',
        'Belgium',
        'Sapienza',
        'Denmark',
        'Lansing',
        'Moscow',
        'Spain',
        'Prague',
        'Ireland',
        'Torino',
        'Düsseldorf',
        'Switzerland',
        'Heidelberg',
        'Suisse',
        'Paris',
        'Poland',
        'Copenhagen',
        'Columbus',
        'Greece',
    ],
    'Australia': ['Australia', 'New Zealand', 'Canberra', 'Australia, Nedlands'],
    'Asia': [
        'Hong Kong',
        'Saudi Arabia',
        'Japan',
        'Israel',
        'Beijing',
        'Singapore',
        'China',
        'India',
        'Gesundheit, Mannheim',
        'Erlangen-Nürnberg',
        'Kuala Lumpur',
        'Thailand',
    ],
    'South America': ['Brazil', 'Argentina', 'México', 'Mexico', 'Chile, Santiago', 'Brasil'],
    'Africa': ['Nigeria'],
}

df['short_aff'] = df.Affiliation.str.slice(-15)
df['aff'] = df.Affiliation.apply(clean_affiliation)
df['country'] = df.aff.apply(parse_country)


hist: Dict[str, int] = {}
for full_aff in df[df.country == ''].aff:
    aff = full_aff[-25:]
    hist[aff] = hist.get(aff, 0) + 1

for aff, freq in sorted(hist.items(), key=lambda x: (x[1], x[0]), reverse=True)[:50]:
    print(freq, aff)

print(sum(hist.values()))
print(len(hist))
df = df.merge(metadata_df, how='outer', on=['PMID'])
df[['PMID', 'PMCID', 'pubtype', 'Journal Title', 'Year', 'country', 'Affiliation']].to_csv(
    args.output_file, index=False
)
