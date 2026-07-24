"""Tests for db/database.py.

Should test, against a temporary database file rather than the real one:

- Schema creation: a fresh database gets all five tables (postings, labels,
  skills, posting_skills, model_runs).
- Upsert idempotency: inserting the same posting twice leaves exactly one row —
  the UNIQUE(source, external_id, title) constraint does its job and the second
  insert is reported as skipped, not as an error.
- Genuinely new postings are inserted alongside existing ones.
- Foreign key relationships hold: a label or posting_skills row can be attached
  to an existing posting and read back.
- Query helpers return the rows that were written, in the expected shape.
"""
