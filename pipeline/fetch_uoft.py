"""Normalize my UofT work-study xlsx export into the raw-CSV column contract.

Responsible for: turning the 17-column CLNx export
(data/raw/uoft_workstudy_summer2025.csv) into the same six-column shape the
Greenhouse and Kaggle fetchers already produce, so combine.py can read all
three files the same way. This is not a fetcher — there is no API and no
scraping; it is a one-time normalizer over a file I downloaded myself.

Inputs: config.UOFT_INPUT_DATA (the raw export, columns: ID, Title,
Num. Posts, Description, Qualifications, Position Type, Work Study Stream,
Accessibility, Campus Location, Division, Department, Department Overview,
Supervisor, Supervisor Title, Weekly Hours, Application Documents,
Application Deadline).

Outputs: config.UOFT_OUTPUT_DATA with exactly external_id, company, title,
description, url, fetched_at. combine.py is what tags these rows with
source='uoft'.

The four decisions this file has to make, and why:

1. description — Description alone is NOT enough. The skills I need for
   Phase 7's regex extractor ("Python", "R", "SQL") live in Qualifications,
   a separate column. Join Description + Qualifications (Department Overview
   optional) into one text field, or the extractor finds nothing.
2. company — there is no employer column. Every posting is UofT. Use the
   hiring unit (Department, or Division for the faculty-level name) so the
   "which company has the most postings" query in Week 2 is still meaningful.
3. url — the export has none and CLNx postings are behind a login, so there
   is nothing valid to link to. Leave it empty rather than inventing a URL;
   the schema allows a NULL url.
4. Num. Posts — 1 to 4 openings per row. Keep one row per posting; do not
   explode, or the UNIQUE(source, external_id, title) constraint collapses
   the copies at ingestion anyway.

Also: no column is ever null in this export, but 32 rows repeat
Title+Department, and 6 descriptions contain stray HTML tags — both are
combine.py's job, not this file's.

How I'll know it works: the output has 837 rows and exactly the same six
columns as kaggle.csv, external_id is unique, no description is shorter than
200 characters, and combine.py loads it without a rename.
"""
# 'external_id', 'company', 'title', 'description', 'url', 'fetched_at'

import pandas as pd
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
import config

uoft = pd.read_csv(config.UOFT_INPUT_DATA)



uoft["description"] = uoft['Description'] + "\n" + uoft['Qualifications']
uoft.drop(columns=["Description", "Qualifications"], inplace=True)



uoft["company"] = uoft['Division'] + ", " + uoft['Department']

uoft.drop(columns=["Division", "Department"], inplace=True)

uoft.rename(columns={"ID": "external_id", "Title": "title"}, inplace=True)

uoft["url"] = None
uoft["fetched_at"] = pd.Timestamp.now()


uoft = uoft[["external_id", "company", "title", "description", "url", "fetched_at"]]

uoft.to_csv(config.UOFT_OUTPUT_DATA, index=False)