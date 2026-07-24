"""LLM-assisted labeling of postings into the 8 categories.

Responsible for: sending unlabeled postings to the Claude API in batches and
recording the category it returns, so the training set can grow past the
150-200 rows I label by hand.

Inputs: unlabeled postings from the database; the 8 category names from config;
ANTHROPIC_API_KEY from .env; a batch size.

Outputs: rows in the labels table with label_source 'llm', written
incrementally so an interrupted run keeps everything already labeled; a log of
any postings the model failed to classify.

How I'll know it works: every posting in the database ends up with a label,
killing the script mid-run loses nothing, and spot-checking 10% of the LLM
labels by hand gives an agreement percentage I can write into the README.
"""
