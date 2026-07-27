"""Load and sample the Kaggle LinkedIn job postings dataset.

Responsible for: reading the arshkon/linkedin-job-postings CSV that I download
manually from Kaggle, selecting the columns this project cares about, and
taking a reproducible random sample so the dataset does not dwarf the
Greenhouse rows. This is a loader for an already-downloaded file — it does not
scrape LinkedIn.

Inputs: the path to the downloaded Kaggle CSV, a sample size, and a random
seed (so re-running gives the same sample).

Outputs: a CSV in data/raw with the same column shape as the Greenhouse
output — external_id, company, title, description, url, fetched_at.
combine.py is what tags these rows with source='kaggle'.

How I'll know it works: the output has exactly the requested number of rows,
the same columns as the Greenhouse CSV, and two runs with the same seed produce
identical files.
"""

import pandas as pd
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
import config

raw_data = pd.read_csv(config.KAGGLE_CSV_PATH)  # changed: path from config, not hardcoded
fetched_at = pd.Timestamp.now()






raw_data = raw_data.dropna(subset=["company_name"])
# changed: sample size and seed from config, not hardcoded
sampled_data = raw_data.sample(n=config.KAGGLE_SAMPLE_SIZE, random_state=config.RANDOM_SEED)
sampled_data["fetched_at"] = fetched_at
sampled_data = sampled_data[["job_id", "company_name", "title", "description", "job_posting_url", "fetched_at"]]
sampled_data = sampled_data.rename(columns={"job_id": "external_id", 
                                            "company_name": "company",
                                              "job_posting_url": "url"})


sampled_data.to_csv(config.KAGGLE_OUTPUT_PATH, index=False)  # changed: path from config