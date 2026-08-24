"""Consolidate every label into one file, collapsing the old 8 classes into 5.

Responsible for: merging the two hand-labeled spreadsheets with the machine
labels, mapping the retired category names onto the current
config.CATEGORIES, and writing a single table that Week 4 can train from.

The three sources are read, never written. They are the audit trail: the xlsx
sheets are what I labeled by hand, and llm_labels.csv is what Claude Code
returned. Re-running this script rebuilds the merged view from them, so a
change to a category name costs one rerun rather than a re-label.

Inputs: config.HAND_LABELED_DONE, config.HAND_LABEL_TOPUP_DONE (hand labels,
still in the 8-class vocabulary) and config.LLM_LABELED_DATA (machine labels,
same vocabulary); MERGE below for the 8 -> 5 mapping.

Outputs: config.FINAL_LABELS_DATA with external_id, category, label_source
('hand' | 'llm') -- the same shape as the labels table in db/schema.sql.

How I'll know it works: one row per posting in the postings table, no
duplicates, every category in config.CATEGORIES, and the per-class counts
match the hand + llm subtotals printed at the end.
"""

import sqlite3
import sys
from pathlib import Path

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parent.parent))

import config

# Retired class -> current class. Anything not listed here is unchanged.
MERGE = {
    "Machine learning": "Machine learning / AI",
    "NLP / LLM": "Machine learning / AI",
    "Data engineering": "Data engineering / analytics",
    "Data analyst": "Data engineering / analytics",
    "Quant / finance": "Not relevant",
}


def read_hand(path: str) -> pd.DataFrame:
    df = pd.read_excel(path)[["external_id", "category"]]
    df["external_id"] = df["external_id"].astype(str)
    df["category"] = df["category"].astype(str).str.strip()
    return df


hand = pd.concat(
    [read_hand(config.HAND_LABELED_DONE), read_hand(config.HAND_LABEL_TOPUP_DONE)],
    ignore_index=True,
)
hand["label_source"] = "hand"

llm = pd.read_csv(config.LLM_LABELED_DATA, dtype=str)
llm["category"] = llm["category"].str.strip()
llm["label_source"] = "llm"

labels = pd.concat([hand, llm], ignore_index=True)
# replace, not map: it substitutes the listed names and leaves every other
# category untouched. map would turn anything missing from MERGE into NaN.
labels["category"] = labels["category"].replace(MERGE)


# Fail loudly rather than writing a category the classifier will never see.
unknown = sorted(set(labels["category"]) - set(config.CATEGORIES))
if unknown:
    raise SystemExit(f"categories not in config.CATEGORIES: {unknown}")

dupes = labels["external_id"].duplicated().sum()
if dupes:
    raise SystemExit(f"{dupes} postings carry more than one label")

conn = sqlite3.connect(config.DB_PATH)
postings = set(
    pd.read_sql_query("SELECT external_id FROM postings", conn)["external_id"].astype(str)
)
missing = postings - set(labels["external_id"])
extra = set(labels["external_id"]) - postings
if missing or extra:
    raise SystemExit(f"{len(missing)} postings unlabeled, {len(extra)} labels with no posting")

labels.to_csv(config.FINAL_LABELS_DATA, index=False)

print(f"{len(labels):,} labels -> {config.FINAL_LABELS_DATA}")
print(pd.crosstab(labels["category"], labels["label_source"], margins=True).to_string())
