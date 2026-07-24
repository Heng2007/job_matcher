"""SQLite access layer for the job intelligence database.

Responsible for: opening a connection to the SQLite file, creating the schema
from db/schema.sql on first run, upserting postings, and providing the query
helpers the pipeline, analysis and app modules read through. All SQL lives
here; no other module should open the database directly.

Inputs: the database path from config; posting records produced by
pipeline/combine.py (title, description, source, external_id, company, url,
fetched_at); labels from ml/label_llm.py and hand-labeled CSVs; skill
assignments from analysis/skills_taxonomy.py; model run metrics from ml/train.py.

Outputs: a populated db/jobintel.sqlite; rows returned as plain dicts or
DataFrames for callers; row counts for upsert operations (inserted vs skipped).

How I'll know it works: tests/test_database.py passes — running the same
upsert twice leaves the row count unchanged, and a fresh database file is
created with all five tables when none exists.
"""
