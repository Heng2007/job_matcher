"""Weekly orchestration script: fetch, combine, upsert, re-score.

Responsible for: running the whole refresh end to end on a schedule (cron or
Task Scheduler) so the database stays current without manual steps. Calls the
fetchers, then combine, then the database upsert, then re-scores postings
against my skill profile.

Inputs: the Greenhouse company token list and Kaggle CSV path from config; the
existing database at db/jobintel.sqlite; my_skills.json.

Outputs: new rows added to the postings table (existing ones untouched),
refreshed skill extractions and match scores, and a printed summary of how many
postings were fetched, how many were new, and how many were skipped.

How I'll know it works: `python pipeline/weekly_update.py` completes without
error, reports a sensible new-row count, and running it twice in a row reports
zero new rows the second time.
"""
