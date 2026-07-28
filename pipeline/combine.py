"""Normalize and merge raw posting CSVs into one clean dataset.

Responsible for: taking everything in data/raw (Greenhouse, Kaggle, my UofT
work-study xlsx) and turning it into a single table with consistent columns;
stripping HTML out of descriptions; dropping duplicates; and filtering out
postings too short to classify.

Inputs: all raw CSV/xlsx files in data/raw.

Outputs: one combined CSV in data/processed with columns title, description,
source, url (plus external_id, company, fetched_at carried through), HTML
removed from description, duplicates dropped, and every remaining row longer
than 200 characters.

How I'll know it works: tests/test_combine.py passes — HTML tags are gone from
descriptions, a posting appearing twice survives only once, and rows under 200
characters are absent from the output.
"""
#    a. load all three raw files,
#    b. rename columns so every source has exactly: title, description, source, url,
#    c. strip HTML tags from descriptions (the Greenhouse ones),
#    d. drop rows whose description is shorter than ~200 characters,
#    e. drop duplicates (same title + same company),
#    f. save `data/processed/all_postings.csv`.

import pandas as pd
import sys
from bs4 import BeautifulSoup
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
import config


greenhouse = pd.read_csv(config.GREENHOUSE_OUTPUT_DATA)
kaggle = pd.read_csv(config.KAGGLE_OUTPUT_DATA)
uoft = pd.read_csv(config.UOFT_OUTPUT_DATA)

greenhouse["source"] = config.SOURCES[0]
kaggle["source"] = config.SOURCES[1]
uoft["source"] = config.SOURCES[2]


for i in range(len(greenhouse)):
    greenhouse.loc[i, "description"] = BeautifulSoup(greenhouse.loc[i, "description"], 
                                                       "html.parser").get_text(" ")


print(greenhouse["description"].iloc[1])