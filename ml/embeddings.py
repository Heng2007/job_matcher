"""Sentence-embedding features as an alternative to TF-IDF.

Responsible for: encoding posting descriptions with all-MiniLM-L6-v2, feeding
those vectors to the same classifier heads used in train.py, and comparing the
result against the TF-IDF baseline. This is conditional work: embeddings are
kept only if they beat TF-IDF on macro-F1, otherwise they get dropped and the
negative result is noted in the README.

Inputs: labeled posting descriptions from the database; the all-MiniLM-L6-v2
model; the same train/test split used in train.py so the comparison is fair.

Outputs: cached embedding vectors for the corpus, macro-F1 for the
embedding-based models, a comparison table against the TF-IDF numbers, and a
saved model only if embeddings win.

How I'll know it works: the comparison table exists with both feature types
scored on the same split, and I can state plainly in the README whether
embeddings won or lost.
"""
