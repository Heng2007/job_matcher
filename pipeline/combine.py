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
