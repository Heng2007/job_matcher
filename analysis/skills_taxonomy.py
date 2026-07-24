"""Skill vocabulary and regex extraction of skills from posting text.

Responsible for: defining the skill list with a learning tier for each skill,
mapping skills to the 8 categories, and extracting which skills a posting
mentions. Extraction is regex, not ML — deliberately. Short tokens (R, AI, ML,
NLP, LLM) need word-boundary patterns, because plain substring matching
false-positives on words like "training" and "enrollment".

Inputs: raw posting description text; the skill pattern table defined in this
module.

Outputs: the set of skills detected in a posting; each skill's tier (used to
order what to learn next); the skill-to-category mapping used by the app and by
match scoring.

How I'll know it works: tests/test_taxonomy.py passes — known strings produce
exactly the expected skills, and the word-boundary cases behave: "enrollment"
does not match R, "training" does not match AI, "R and Python" does match R.
"""
