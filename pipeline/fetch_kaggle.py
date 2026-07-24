"""Load and sample the Kaggle LinkedIn job postings dataset.

Responsible for: reading the arshkon/linkedin-job-postings CSV that I download
manually from Kaggle, selecting the columns this project cares about, and
taking a reproducible random sample so the dataset does not dwarf the
Greenhouse rows. This is a loader for an already-downloaded file — it does not
scrape LinkedIn.

Inputs: the path to the downloaded Kaggle CSV, a sample size, and a random
seed (so re-running gives the same sample).

Outputs: a CSV in data/raw with the same column shape as the Greenhouse
output — external_id, company, title, description, url, fetched_at — with
source marked as 'kaggle'.

How I'll know it works: the output has exactly the requested number of rows,
the same columns as the Greenhouse CSV, and two runs with the same seed produce
identical files.
"""
