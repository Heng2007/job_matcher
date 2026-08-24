# Job Market Intelligence Tool — Build Spec

Handoff document for Claude Cowork. Build this project in the target directory,
initialize Git, and push to GitHub when instructed.

## What this is

A personal tool that maintains a database of job postings (work-study + real
market), classifies them into skill categories, scores each posting against the
owner's current skills, and produces a "learn X → unlock N postings" plan.

Owner context: first-year UofT CS/Stats student. Python: comfortable with
pandas, scikit-learn (LogReg, Random Forest, XGBoost), basic Git. New to: SQL,
embeddings, Optuna, Streamlit.

## Division of work — IMPORTANT

Cowork builds the **scaffolding**. The owner writes the **ML core** himself
(that's the point of the project). Concretely:

**Cowork: build fully**
- Repo structure, pyproject/requirements, .gitignore, README skeleton
- `db/schema.sql` + `db/database.py` (all SQLite code)
- `pipeline/fetch_greenhouse.py`, `pipeline/fetch_kaggle.py`, `pipeline/combine.py`
- `pipeline/weekly_update.py` (orchestration script)
- `app/streamlit_app.py` (full UI, calling into stub functions)
- `analysis/skills_taxonomy.py` (port from existing starter kit, see below)

**Cowork: create as STUBS ONLY** — file, function signatures, docstrings
describing exactly what to implement, `raise NotImplementedError`:
- `ml/train.py` (model training + comparison)
- `ml/tune.py` (Optuna tuning)
- `ml/embeddings.py` (sentence-transformers features)
- `ml/label_llm.py` (LLM-assisted labeling)
- `analysis/match_scoring.py` (match scores + unlock table)
- `analysis/semantic_search.py` (cosine-similarity search)

Each stub's docstring must state: inputs, outputs, the acceptance test
(how the owner knows it works), and a hint on approach — but NO implementation.

**Existing starter code to port in** (owner has these files from a prior
session; ask for them or rebuild from the descriptions in each file spec):
`skills_taxonomy.py`, `fetch_greenhouse.py`, `train_baseline.py`,
`classify_posting.py`, `my_skills.json`, `seed_labels.csv`.

## Repository structure

```
job-intel/
├── README.md                  # what/why/how + honest metrics section (filled as phases complete)
├── requirements.txt           # pinned versions
├── .gitignore                 # data/, models/, .env, __pycache__
├── .env.example               # ANTHROPIC_API_KEY=  (for labeling phase)
├── config.py                  # paths, category list, constants
├── my_skills.json             # owner's skill profile (checked in, it's the point)
│
├── data/                      # gitignored
│   ├── raw/                   # as-fetched CSVs
│   └── processed/             # cleaned/combined
│
├── db/
│   ├── schema.sql             # tables: postings, labels, skills, posting_skills, model_runs
│   ├── database.py            # connection, upsert_postings(), query helpers
│   └── jobintel.sqlite        # gitignored
│
├── pipeline/
│   ├── fetch_greenhouse.py    # public Greenhouse Job Board API, --companies tokens
│   ├── fetch_kaggle.py        # loader/sampler for arshkon/linkedin-job-postings CSV
│   ├── combine.py             # normalize → title,description,source,url; strip HTML; dedupe; length filter >200 chars
│   └── weekly_update.py       # re-fetch → combine → upsert only new rows → re-score
│
├── ml/
│   ├── label_llm.py           # STUB: batch postings to Claude API, JSON out, incremental saves
│   ├── train.py               # STUB: TF-IDF → LogReg + XGBoost, macro-F1, confusion matrix, save winner
│   ├── tune.py                # STUB: Optuna, ~50 trials on the winner
│   └── embeddings.py          # STUB: all-MiniLM-L6-v2 features, same heads, keep only if beats TF-IDF
│
├── analysis/
│   ├── skills_taxonomy.py     # regex skill patterns + tiers + 5 categories (port from starter kit)
│   ├── match_scoring.py       # STUB: match %, near-misses (≤2 missing), unlock table
│   └── semantic_search.py     # STUB: embed corpus, cosine top-k "more like this"
│
├── models/                    # gitignored; .joblib artifacts
│
├── app/
│   └── streamlit_app.py       # 2 tabs: "Analyze a posting" | "My matches & plan"
│
└── tests/
    ├── test_taxonomy.py       # skill regex: known strings → expected skills (incl. R/AI/ML word-boundary cases)
    ├── test_combine.py        # HTML stripping, dedupe, length filter
    └── test_database.py       # upsert idempotency: re-inserting same posting doesn't duplicate
```

## Key design decisions (do not change without asking owner)

1. **One 5-way classifier**, not binary + multiclass. Categories: Machine
   learning / AI, Data engineering / analytics, Software engineering, Research
   assistant, Not relevant. Relevance score = 1 − P(Not relevant).
   *(Revised 2026-08-14 before labeling: added Data engineering, merged
   Classical ML into Machine learning. Revised again 2026-08-23 after labeling
   all 6,636 postings: collapsed 8 → 5, because four classes came in under 1%
   of the data — Data engineering 62, NLP / LLM 48, Data analyst 46, Quant /
   finance 10 — and macro-F1 weights every class equally. See HANDBOOK Week 3.)*
2. **Skill extraction is regex, not ML.** Word-boundary patterns for short
   tokens (R, AI, ML, NLP, LLM) — plain substring matching false-positives on
   words like "training" and "enrollment". **The same rule applies to the
   junior/senior title patterns in `config.py`**, which originally lacked it:
   "intern" matched inside "Internal" and "International", and "lead" inside
   "Leadership". Every regex in this project that matches a short word matches
   it whole (`\b...\b`), and uses non-capturing groups `(?:...)` so
   `pandas.Series.str.contains` does not warn about unused match groups.
3. **SQLite, not Postgres.** No server; the tool is single-user.
4. **Embeddings are conditional.** Kept only if they beat TF-IDF on macro-F1;
   otherwise noted in README and dropped.
5. **Data sources are ToS-clean only**: public Greenhouse Job Board API
   (boards-api.greenhouse.io, no auth for GET), Kaggle datasets, owner's UofT
   xlsx. **Never scrape Indeed/LinkedIn.**

## Database schema (implement exactly)

```sql
CREATE TABLE postings (
  id INTEGER PRIMARY KEY,
  external_id TEXT,            -- source's own id if any
  source TEXT NOT NULL,        -- 'greenhouse' | 'kaggle' | 'uoft'
  company TEXT,
  title TEXT NOT NULL,
  description TEXT NOT NULL,
  url TEXT,
  fetched_at TEXT NOT NULL,    -- ISO date
  UNIQUE(source, external_id, title)
);

CREATE TABLE labels (
  posting_id INTEGER REFERENCES postings(id),
  category TEXT NOT NULL,
  label_source TEXT NOT NULL,  -- 'hand' | 'llm'
  PRIMARY KEY (posting_id)
);

CREATE TABLE skills (
  id INTEGER PRIMARY KEY,
  name TEXT UNIQUE NOT NULL,
  tier INTEGER NOT NULL
);

CREATE TABLE posting_skills (
  posting_id INTEGER REFERENCES postings(id),
  skill_id INTEGER REFERENCES skills(id),
  PRIMARY KEY (posting_id, skill_id)
);

CREATE TABLE model_runs (
  id INTEGER PRIMARY KEY,
  run_date TEXT NOT NULL,
  model_name TEXT NOT NULL,
  macro_f1 REAL,
  notes TEXT
);
```

## Streamlit app spec

Tab 1 — "Analyze a posting": text area → on submit show relevance %,
category, detected skills (green = owner has, red = missing), learning
priority (missing skills sorted by tier).

Tab 2 — "My matches & plan": table of postings ranked by match %, filter
toggle for junior-eligible (`config.JUNIOR_TITLE_PATTERN`, excluding
`config.SENIOR_TITLE_PATTERN`), near-miss list, and the "learn X → unlock N
postings" bar chart.

The junior toggle is a coarse title heuristic, not a judgment of eligibility —
it cannot see that a posting titled "intern" wants 8 years of experience,
because that lives in the description. Measured on the Greenhouse corpus it
admits 1 fake junior per 35 and discards 358 postings asking for ≤1 year whose
titles carry no junior keyword. Ranking by match % is what actually protects
against over-senior postings: they demand skills the owner lacks and sink on
their own. Keep the toggle off by default so it narrows rather than hides.

Until the ML stubs are implemented, the app should run with graceful
placeholders ("model not trained yet") rather than crash.

## Timeline (owner's schedule: ~6-8 hrs/wk August, ~4-5 hrs/wk after)

| Week | Dates | Work | Who | Done when |
|---|---|---|---|---|
| 1 | Aug 3–9 | Cowork builds scaffold; owner finds 15–20 Greenhouse tokens, runs fetch + combine | Both | ~2,000 rows in data/processed |
| 2 | Aug 10–16 | Database live; ingest all postings; owner practices queries | Cowork built it, owner uses it | upsert idempotency test passes |
| 3 | Aug 17–23 | Owner hand-labels 150–200 rows; implements label_llm.py; runs it; spot-checks 10% | Owner | every row labeled, agreement % recorded in README |
| 4 | Aug 24–30 | Owner implements train.py; confusion matrix; push to GitHub | Owner | **Milestone: named on work-study applications** |
| 5 | Aug 31–Sep 6 | Owner implements tune.py (Optuna, 50 trials) — light week, semester starts | Owner | tuned model beats or ties default |
| 6–7 | Sep 7–20 | Owner implements embeddings.py; compare vs TF-IDF; keep winner | Owner | comparison table in README |
| 8 | Sep 21–27 | Owner implements match_scoring.py + unlock table | Owner | ranked shortlist + learning plan exist |
| 9 | Sep 28–Oct 4 | Owner implements semantic_search.py; buffer for slippage | Owner | "more like this" returns sane results |
| 10 | Oct 5–11 | Wire real functions into Streamlit; weekly_update.py cron/Task Scheduler; final README | Both | tool runs end to end weekly |

Fallback rules: if behind, cut from the end (semantic search first), never
from weeks 1–4. A 30-minute week beats a zero week.

## Definition of done

- `python pipeline/weekly_update.py` fetches, dedupes, upserts, re-scores without error
- `streamlit run app/streamlit_app.py` shows both tabs with real data
- All tests pass
- README contains: data sources, label agreement %, model comparison table
  (macro-F1), known limitations (skill-regex misses, LLM label noise)
- Pushed to GitHub with a sensible commit history (not one giant commit)

## Instructions to Cowork, verbatim

1. Build the structure above in the target directory.
2. Implement everything in the "build fully" list; stub everything in the
   "STUBS ONLY" list with detailed docstrings.
3. Write the three test files; make the taxonomy and combine tests pass
   against your implementations.
4. `git init`, commit in logical chunks (scaffold / pipeline / db / app / tests),
   and push to the GitHub repo the owner specifies.
5. Do not implement the stubbed ML files even if it would be easy — the owner
   is implementing those. Leave them failing NotImplementedError.
6. Where the spec is ambiguous, choose the simpler option and note it in a
   DECISIONS.md file.
