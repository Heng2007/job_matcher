"""Fetch job postings from the public Greenhouse Job Board API.

Responsible for: pulling every open posting for a list of company board tokens
from boards-api.greenhouse.io (public, no auth needed for GET), and writing the
results to data/raw as CSV. This is a ToS-clean source; nothing here scrapes
Indeed or LinkedIn.

Inputs: company board tokens read from the file at config.GREENHOUSE_TOKENS_PATH
(one per line, either a full board URL or a bare token); the Greenhouse API
endpoint from config.

Outputs: one CSV in data/raw per run containing external_id, company, title,
description (raw HTML as returned), url and fetched_at for every posting found.

How I'll know it works: running it with 15-20 tokens produces a CSV of roughly
a thousand-plus rows, each with a non-empty description and a working url, and
companies with no open roles are skipped with a warning rather than crashing
the run.
"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

import html
import requests
import pandas as pd
import config

with open(config.GREENHOUSE_TOKENS_PATH, "r") as f:
    companies = [line.rsplit('/')[-1].rsplit('\n')[0] for line in f.readlines()]


rows = []
fetched_at = pd.Timestamp.now()
for company in companies:
    url = f"{config.GREENHOUSE_API_BASE}/{company}/jobs?content=true"
    rq = requests.get(url, timeout=15)

    try:    
        rq.raise_for_status()
    except requests.RequestException as e:
        print(f"Request failed from Greenhouse API: {e}")
        continue

    if rq.json()["jobs"].__len__() == 0:
         print(f"No open roles found for {company}. Skipping.")
         continue

    for jobs in rq.json()["jobs"]:
        rows.append({
            "external_id": jobs["id"],
            "company": jobs.get("company_name"),
            "title": jobs["title"],
            "description": html.unescape(jobs.get("content") or ""),
            "url": jobs["absolute_url"],
            "fetched_at": fetched_at,
            })


greeenhouse_jobs = pd.DataFrame(rows)
greeenhouse_jobs.to_csv(config.RAW_DATA_DIR + "/greenhouse.csv", index=False)

 