"""Cosine-similarity "more like this" search over the posting corpus.

Responsible for: embedding every posting description once, then answering
"find me postings similar to this one" (or to a free-text query) by ranking the
corpus on cosine similarity.

Inputs: posting descriptions from the database; a query — either a posting id
or a block of text; k, the number of results to return.

Outputs: cached corpus embeddings; the top-k most similar postings with their
similarity scores, ids and titles.

How I'll know it works: querying with a posting returns itself first at
similarity ~1.0, the remaining results are visibly in the same job family
rather than random, and a query for something like "NLP research intern"
returns NLP/research postings rather than software engineering ones.
"""
