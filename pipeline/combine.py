"""Normalize and merge raw posting CSVs into one clean dataset.

Responsible for: taking the three normalized raw CSVs (greenhouse.csv,
kaggle.csv, uoft.csv) and turning them into a single table; stripping HTML out
of descriptions; dropping duplicates; and filtering out postings too short to
classify.

Nothing here renames columns. All three producers already write the same six
columns, so the only column missing is `source` — the one fact the raw files
cannot carry, because each fetcher writes its own file and the source lives in
the filename until the frames are concatenated. Tag each frame from
config.SOURCES, then concat with ignore_index=True so the three 0-based indexes
do not overlap.

Inputs: config.GREENHOUSE_OUTPUT_DATA, config.KAGGLE_OUTPUT_DATA and
config.UOFT_OUTPUT_DATA — the OUTPUT paths, never the INPUT ones. The UofT
export is normalized by pipeline/fetch_uoft.py before it gets here.

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




combined = pd.concat([greenhouse, kaggle, uoft],ignore_index = True)

for i in range(len(combined)):
    combined.loc[i, "description"] = BeautifulSoup(combined.loc[i, "description"], 
                                                   "html.parser").get_text("\n"+ " ")

combined.drop_duplicates(subset=["title", "company"], inplace=True)
combined = combined[combined["description"].str.len() > config.MIN_DESCRIPTION_LENGTH]
combined.dropna(subset=["title", "description"], inplace=True)
combined.to_csv(config.PROCESSED_DATA_DIR + "/all_postings.csv", index=False)




