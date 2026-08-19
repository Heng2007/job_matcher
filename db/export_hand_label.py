"""This document is for exporting job data from table to a seperate spreadsheet. It pulls hundreds 
postings with random categories and save it as a spreadsheet which I will hand label all the postings."""


import sqlite3
import pandas as pd
import numpy as np
import sys
from pathlib import Path
import random

sys.path.append(str(Path(__file__).resolve().parent.parent))

import analysis.skills_taxonomy as identifier
import config


# This script overwrites the sheet unconditionally, which destroys hand labels.
# Refuse to run if the existing file has any category filled in.
if Path(config.HAND_LABELED_DATA).exists():
    existing = pd.read_excel(config.HAND_LABELED_DATA)
    if "category" in existing and existing["category"].notna().any():
        raise SystemExit(
            f"Refusing to overwrite {config.HAND_LABELED_DATA}: "
            f"{existing['category'].notna().sum()} of {len(existing)} rows are already labeled. "
            "Move or rename the file first if you really want a fresh sheet."
        )


conn = sqlite3.connect(config.DB_PATH)

df = pd.read_sql_query(("SELECT * FROM postings") , conn)
# "id', 'external_id', 'source', 'company', 'title', 'description', 'url', 'fetched_at'"

category = {c: [] for c in config.CATEGORIES}



for index, rows in df.iterrows():
    find = category[identifier.weak_label_category(f"{rows["title"]} {rows["description"]}")]
    find.append(rows["external_id"])

export = {"external_id":[],
          "title":[],
          "description":[],
          }


for value in category.values():
    if len(value) <= 25:
        export["external_id"].extend(value)
    else:
        export["external_id"].extend(random.sample(value, k = 25))


for posting in export["external_id"]:
    export["title"].append(df[df["external_id"]==posting]["title"].iloc[0])
    export["description"].append(df[df["external_id"]==posting]["description"].iloc[0])



df1 = pd.DataFrame(export)
df1["category"] = ""

spread_sheet = df1.to_excel(config.HAND_LABELED_DATA, index = False)
