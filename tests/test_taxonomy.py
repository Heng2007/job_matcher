"""Tests for analysis/skills_taxonomy.py.

Should test that known strings extract exactly the expected skills, with
particular attention to the word-boundary cases that plain substring matching
gets wrong:

- "Experience with R and Python" detects R and Python.
- "enrollment", "Rust", "Ruby" do NOT detect R.
- "training", "certification" do NOT detect AI.
- "HTML", "MLOps" vs the standalone token ML.
- "NLP" and "LLM" as standalone tokens vs embedded in longer words.
- Case insensitivity: "python", "Python", "PYTHON" all detect Python.
- A posting mentioning no known skills returns an empty set.
- Every skill in the taxonomy has a tier, and every tier is a valid value.

The junior/senior title patterns in config.py belong in this file too — they
are the same class of regex and they failed the same way. Cases to cover:

- "Internal Audit Analyst", "International Program Advisor" and "Internal
  Communications Manager" are NOT junior-eligible ("intern" inside a longer
  word).
- "Leadership Development Manager" is NOT senior ("lead" inside "Leadership");
  "Team Leader, Data Platform" IS.
- "Data Analyst Intern", "Junior Research Assistant" and "Summer 2026
  Internships - Data Science" ARE junior-eligible.
- "Senior Advisor Campus Recruitment" is not, and neither is a bare "Data
  Analyst" — it fails the allow-list rather than hitting the deny-list.
- Neither pattern emits a UserWarning when passed to Series.str.contains,
  which requires non-capturing groups (?:...).
"""
