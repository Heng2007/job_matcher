"""Tests for pipeline/combine.py.

Should test the three cleaning behaviours the combined dataset depends on:

- HTML stripping: a description containing tags and entities comes out as
  plain readable text with no markup left.
- Dedupe: the same posting appearing in two raw files survives exactly once.
- Length filter: rows whose description is 200 characters or shorter are
  dropped; rows just over the threshold are kept.

Plus the output contract: the combined frame has the expected columns
(title, description, source, url — with external_id, company and fetched_at
carried through), source is one of config.SOURCES, and title and description
are never empty.

Two failure modes worth an explicit test, because both are silent rather than
loud:

- Every row must keep its own description. Building the combined text with an
  f-string over a Series stringifies the whole Series and broadcasts one value
  to every row, so assert the combined frame has many distinct descriptions,
  not just that the column exists.
- The combined index must be unique (concat with ignore_index=True). Without
  it the three frames keep overlapping 0-based labels and a single .loc[i]
  write lands on several rows at once.
"""
