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
"""
