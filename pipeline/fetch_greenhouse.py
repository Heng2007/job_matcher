"""Fetch job postings from the public Greenhouse Job Board API.

Responsible for: pulling every open posting for a list of company board tokens
from boards-api.greenhouse.io (public, no auth needed for GET), and writing the
results to data/raw as CSV. This is a ToS-clean source; nothing here scrapes
Indeed or LinkedIn.

Inputs: company board tokens, passed as --companies on the command line (e.g.
stripe, figma, databricks); the Greenhouse API endpoint from config.

Outputs: one CSV in data/raw per run containing external_id, company, title,
description (raw HTML as returned), url and fetched_at for every posting found.

How I'll know it works: running it with 15-20 tokens produces a CSV of roughly
a thousand-plus rows, each with a non-empty description and a working url, and
companies with no open roles are skipped with a warning rather than crashing
the run.
"""
