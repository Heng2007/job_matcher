"""Tests for pipeline/combine.py.

Should test the three cleaning behaviours the combined dataset depends on:

- HTML stripping: a description containing tags and entities comes out as
  plain readable text with no markup left.
- Dedupe: the same posting appearing in two raw files survives exactly once.
- Length filter: rows whose description is 200 characters or shorter are
  dropped; rows just over the threshold are kept.

Plus the output contract: the combined frame has the expected columns
(title, description, source, url), source is one of the allowed values, and
title and description are never empty.
"""
