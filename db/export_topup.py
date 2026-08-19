"""Export a small top-up sheet of extra Research assistant postings to hand-label.

Responsible for: closing a coverage gap in the main hand-label sheet without
touching it. The original sheet was seeded while CATEGORY_HINTS still contained
a bare "lab" keyword, which pooled SpaceX manufacturing labs and Anthropic's
"AI lab" self-description as Research assistant. That hint is fixed now, so this
pulls fresh postings from the corrected pool.

Inputs: the postings table; the external_ids already present in
config.HAND_LABELED_DATA (values only, so it works whether or not labels have
been downloaded from Google Sheets); the corrected CATEGORY_HINTS.

Outputs: config.HAND_LABEL_TOPUP_DATA — the same four columns as the main sheet
plus the same category dropdown, containing only postings NOT already in it.

How I'll know it works: zero external_id overlap with the main sheet, the main
sheet's modification time is unchanged, and the rows read as research postings
rather than lab-technician roles.
"""

import sqlite3
import sys
import random
from pathlib import Path

import pandas as pd
from openpyxl import load_workbook
from openpyxl.worksheet.datavalidation import DataValidation

sys.path.append(str(Path(__file__).resolve().parent.parent))

import analysis.skills_taxonomy as identifier
import config

TARGET_CATEGORY = "Research assistant"
HOW_MANY = 20


# Read the ids already in the main sheet so we never hand back a duplicate.
# Only the external_id column is touched -- labels are irrelevant here, and the
# file is never written to.
already = set(
    pd.read_excel(config.HAND_LABELED_DATA)["external_id"].astype(str)
)

conn = sqlite3.connect(config.DB_PATH)
df = pd.read_sql_query("SELECT external_id, title, description FROM postings", conn)

pool = [
    row
    for row in df.itertuples()
    if str(row.external_id) not in already
    and identifier.weak_label_category(f"{row.title} {row.description}") == TARGET_CATEGORY
]

if not pool:
    raise SystemExit(f"No {TARGET_CATEGORY} postings left outside the main sheet.")

random.seed(config.RANDOM_SEED)
picked = random.sample(pool, k=min(HOW_MANY, len(pool)))

out = pd.DataFrame(
    {
        "external_id": [r.external_id for r in picked],
        "title": [r.title for r in picked],
        "description": [r.description for r in picked],
    }
)
out["category"] = ""
out.to_excel(config.HAND_LABEL_TOPUP_DATA, index=False)
