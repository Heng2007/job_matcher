"""Weekly orchestration script: fetch, combine, upsert, re-score.

Responsible for: running the whole refresh end to end on a schedule (cron or
Task Scheduler) so the database stays current without manual steps. Calls the
fetchers, then combine, then the database upsert, then re-scores postings
against my skill profile.

Inputs: the Greenhouse company token list and Kaggle CSV path from config; the
existing database at db/jobintel.sqlite; my_skills.json.

Note on the three sources: Greenhouse is the only one that genuinely re-fetches
each week. Kaggle is a fixed downloaded file with a seeded sample, so it
produces the same 1,200 rows every run. The UofT export is a static Summer 2025
snapshot — re-running fetch_uoft.py is harmless and idempotent, but it will
never yield new postings until I download a fresh export. Neither of those is a
bug; just don't read a flat new-row count as "the scrape failed".

Outputs: new rows added to the postings table (existing ones untouched),
refreshed skill extractions and match scores, and a printed summary of how many
postings were fetched, how many were new, and how many were skipped.

How I'll know it works: `python pipeline/weekly_update.py` completes without
error, reports a sensible new-row count, and running it twice in a row reports
zero new rows the second time.
"""
