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
import sys 
from pathlib import Path
import pandas as pd
import sqlite3
sys.path.append(str(Path(__file__).resolve().parent.parent))
import config


conn = sqlite3.connect(config.DB_PATH)


def create_schema(conn: sqlite3.Connection):
    """create the database schema from db/schema.sql"""
    with open(config.SCHEMA_PATH, "r") as f:
        conn.executescript(f.read())

def upsert_postings(conn: sqlite3.Connection):
    """Upsert observations from cleaned csv to table postings"""
    df = pd.read_csv(config.PROCESSED_OUTPUT_DATA)
    cur = conn.cursor()

    cur.executemany("INSERT OR IGNORE INTO postings(external_id, source, company, title, description, url, fetched_at)"
                 "VALUES(?,?,?,?,?,?,?)"
                 , df[["external_id", "source", "company", "title", "description", "url", "fetched_at"]].itertuples(False, None))
    conn.commit()

    return cur.rowcount, len(df) - cur.rowcount 

def insert_skills(conn: sqlite3.Connection, rows):
    """Insert (name, tier) pairs into the skills table.

    skills.name is UNIQUE, so re-running inserts nothing the second time.
    Returns (inserted, ignored) the same way upsert_postings does.
    """
    rows = list(rows)
    cur = conn.cursor()

    cur.executemany("INSERT OR IGNORE INTO skills(name, tier)"
                    "VALUES(?,?)"
                    , rows)
    conn.commit()

    return cur.rowcount, len(rows) - cur.rowcount

def row_count(conn:sqlite3.Connection):
    """Return number of post that lives in the table - posting"""
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM postings")
    return cur.fetchall()[0][0]





create_schema(conn)
print(upsert_postings(conn))


