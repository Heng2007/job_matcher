# Job Intel Project — The Handbook

Step-by-step instructions, furniture-manual style. No code in here — just what
to do, in what order, and how to know each step is done. This follows the final
clean 8-phase plan (no R, no DistilBERT, no RAG — those were cut).

Rule for the whole project: **do the steps in order.** Every step assumes the
ones before it are done. If a step fails, fix it before moving on — later steps
will not work around it.

---

## Week 0 — Before anything (do this the weekend before Week 1)

**Goal: your machine is ready and the empty project structure exists.**

1. Check Python is installed: open a terminal, run `python --version`. You want
   3.10 or newer. If not installed, install from python.org.
2. Check Git is installed: `git --version`. If not, install from git-scm.com.
3. Make a GitHub account if you don't have one. Create a new **empty** repo
   named `job-intel`. Private is fine for now. Do NOT initialize it with a
   README (you'll push your own).
4. Create a folder on your PC: `Projects\job-intel` (not inside Downloads,
   not on Desktop — somewhere permanent).
5. Put two things into that folder: `PROJECT_SPEC.md` (from our chat) and your
   starter files (`skills_taxonomy.py`, `my_skills.json`, `seed_labels.csv`).
6. Open Claude Desktop → Cowork → "Work in a Folder" → select `job-intel` →
   paste the scaffold-only instruction (the one that says "create everything
   blank except docstrings and schema.sql").
7. When Cowork finishes, open the folder and check: every subfolder from the
   spec exists (`pipeline/`, `db/`, `ml/`, `analysis/`, `app/`, `tests/`,
   `data/`), every .py file exists and contains only a comment block, and
   `db/schema.sql` is fully written.
8. Open the folder in PyCharm (or VS Code). Create a virtual environment when
   PyCharm offers. Install packages from `requirements.txt`.

✅ **Done when:** the structure exists, PyCharm opens it without errors, and
`git log` shows one commit ("Initial project scaffold").

---

## Week 1 (Aug 3–9) — Phase 1: Get the data

**Goal: ~2,000 real job postings sitting in `data/processed/all_postings.csv`.**

**Part A — Greenhouse postings (do first, it's the most fun)**

1. Collect board tokens. Go to careers pages of tech companies you know. If
   the URL looks like `boards.greenhouse.io/SOMENAME` or
   `job-boards.greenhouse.io/SOMENAME`, that SOMENAME is a token. Write each
   one into a text file `data/raw/greenhouse_tokens.txt`, one per line.
   Target 15–20 tokens. (Tip: search "site careers greenhouse" + a company
   name; startups and mid-size tech companies use it heavily.)
2. Write `pipeline/fetch_greenhouse.py` yourself. Its docstring tells you what
   it must do. You have a working reference version from our earlier chat —
   read it if stuck, but type yours fresh.
3. Test with only 5 tokens first. Check the output CSV opens and descriptions
   look like real job text (they will contain HTML tags — that's expected,
   Week 1 Part C handles it).
4. Run with all your tokens. Save to `data/raw/greenhouse.csv`.

**Part B — Kaggle postings**

5. Make a Kaggle account, download the dataset `arshkon/linkedin-job-postings`.
6. Unzip; find the file that contains job descriptions.
7. Write `pipeline/fetch_kaggle.py`: load that file, keep only title +
   description + a link column if present, randomly sample about 1,200 rows,
   save to `data/raw/kaggle.csv`. (Sample — do not load all 120k rows into
   your pipeline.)

**Part C — UofT work-study postings**

8. Copy your UofT csv into `data/raw/`. It is a raw CLNx export with 17
   columns and does NOT match the column contract the two fetchers produce —
   no `company`, no `url`, no `fetched_at`, and the skills you care about sit
   in a separate `Qualifications` column, not in `Description`.
9. Write `pipeline/fetch_uoft.py`: read `config.UOFT_INPUT_DATA`, map it onto
   `external_id, company, title, description, url, fetched_at`, save to
   `config.UOFT_OUTPUT_DATA`. Its docstring lists the four judgment calls
   (what goes into `description`, what counts as `company`, what to do about
   the missing url, and how to treat `Num. Posts`).
10. Check the output: 837 rows, six columns, same order as `kaggle.csv`.

**Part D — Combine everything**

11. Write `pipeline/combine.py`. It must, in this order:
   a. load all three raw files,
   b. add the `source` column so every source has exactly: title, description,
      source, url (all three raw files already share the column contract —
      only Greenhouse and Kaggle need no renaming, and UofT was normalized in
      Part C),
   c. strip HTML tags from descriptions (the Greenhouse ones),
   d. drop rows whose description is shorter than ~200 characters,
   e. drop duplicates (same title + same company),
   f. save `data/processed/all_postings.csv`.
12. Sanity-check: open the CSV, read 10 random descriptions. They should be
    clean readable text, no `<p>` or `&amp;` junk. If you see junk, your HTML
    stripping missed something — fix before continuing.
13. Commit: "Phase 1: data pipeline".

✅ **Done when:** `all_postings.csv` has roughly 2,000 rows, 4 columns, clean text.

---

## Week 2 (Aug 10–16) — Phase 2: Database

**Goal: all postings live in SQLite, and re-running ingestion does NOT create duplicates.**

1. Read `db/schema.sql` line by line until you can say out loud what each
   table stores and why `posting_skills` exists (it's the many-to-many link
   between postings and skills).
2. Write `db/database.py`: a function that creates the database from
   schema.sql, a function `upsert_postings()` that inserts rows from the CSV
   but skips ones already present (the UNIQUE constraint in the schema is
   what makes this possible), and 2–3 query helper functions.
3. Ingest `all_postings.csv` into the database.
4. **The critical test:** run the ingestion a second time. Count rows before
   and after — the count must not change. If it doubles, your upsert is
   actually an insert; fix it. This is the whole reason the database exists.
5. Practice queries — answer these using SQL only, no pandas:
   - How many postings per source?
   - Which company has the most postings?
   - What is the average description length per source?
6. Also ingest the skills list: write a tiny script that reads the skill
   names + tiers from `skills_taxonomy.py` into the `skills` table.
7. Commit: "Phase 2: SQLite database + idempotent ingestion".

✅ **Done when:** re-ingestion changes nothing, and you answered the three
questions with SELECT statements.

---

## Week 3 (Aug 17–23) — Phase 3: Labeling  ⚠️ the wall — protect this week

**Goal: every posting has one of the 8 categories, and you know how much to trust the labels.**

1. Hand-labeling first. Pull 150–200 postings out of the database (mix of all
   three sources). Put them in a spreadsheet with an empty `category` column.
2. Label them yourself in 30-minute sittings across the week (about 40–50 per
   sitting). Use exactly the 8 category names from `config.py` — a typo like
   "NLP/LLM" vs "NLP / LLM" will break training later.
3. While labeling, write down (in a notes file) which categories you found
   hard to tell apart. This becomes your README's limitations section.
4. Get a Claude API key (console.anthropic.com), put it in `.env` (never in
   code, never committed — `.gitignore` already covers `.env`).
5. Write `ml/label_llm.py`: send postings in batches of ~20, ask for JSON
   back with a category per posting constrained to your 8 names, save results
   incrementally after every batch (so a crash mid-run loses one batch, not
   everything).
6. Test on 40 postings you already hand-labeled. Compare. If agreement is
   below ~75%, improve your prompt (add one example posting per category to
   it) before running the full batch.
7. Run over all remaining postings. Store labels in the `labels` table with
   `label_source` = 'hand' or 'llm'.
8. Spot-check: sample 10% of the LLM-labeled rows, label them yourself
   without peeking, compute the agreement percentage. **Write the number in
   the README.** This number is part of your project's credibility.
9. Commit: "Phase 3: labels + agreement rate".

✅ **Done when:** every posting has a label, and the README states your
agreement rate.

---

## Week 4 (Aug 24–30) — Phase 4: Baseline models  🏁 the milestone week

**Goal: a trained classifier with honest metrics, pushed to GitHub — nameable on work-study applications.**

1. Write `ml/train.py`. In order: load labeled postings from the database →
   train/test split (stratified by category) → TF-IDF features → train
   Logistic Regression → print macro-F1 and the per-class report → train
   XGBoost on the same features → same report.
2. Generate a confusion matrix image for your best model. Look at it. Name
   the two categories it confuses most (predicting: Classical ML vs Data
   analyst, based on how similar their postings read).
3. Record each run in the `model_runs` table (date, model, macro-F1).
4. Save the winning model + vectorizer to `models/`.
5. Reality check: if macro-F1 is suspiciously high (>0.95), something leaked —
   most likely duplicates across your train/test split. If it's very low
   (<0.5), check your labels for category-name typos first, model second.
6. Write the README properly now: what the project is, data sources, label
   agreement rate, model comparison table, confusion-matrix findings.
7. Connect the repo to GitHub and push everything.
8. Commit: "Phase 4: baseline models + evaluation".

✅ **Milestone:** the GitHub link works, the README tells the honest story,
and you can explain every file in the repo out loud.

---

## Week 5 (Aug 31–Sep 6) — Phase 5: Optuna tuning  (light week, semester starts)

**Goal: your best model, tuned, and proof of whether tuning helped.**

1. Install Optuna. Read its "first optimization" tutorial page (10 minutes).
2. Write `ml/tune.py`: define the search space for your winning model's main
   hyperparameters (for XGBoost: number of trees, depth, learning rate),
   objective = cross-validated macro-F1, run ~50 trials.
3. Compare tuned vs default in the `model_runs` table. Save Optuna's history
   plot. If tuning barely helped, say so in the README — "tuning gained
   +0.01 macro-F1" is an honest, normal result.
4. Save the tuned model as the new production model.
5. Commit: "Phase 5: Optuna tuning".

✅ **Done when:** the tuned-vs-default comparison is written down.

---

## Weeks 6–7 (Sep 7–20) — Phase 6: Embeddings (conditional)

**Goal: know whether embeddings beat TF-IDF for YOUR data — and keep whichever wins.**

1. Install `sentence-transformers`. First run downloads the model
   `all-MiniLM-L6-v2` (~90MB) automatically.
2. Write `ml/embeddings.py`: encode every posting's text into a vector,
   cache the vectors to disk (encoding 2,000 postings takes minutes, don't
   redo it every run).
3. Train the SAME classifier heads (LogReg, XGBoost) on the embedding
   vectors instead of TF-IDF. Same split, same metric.
4. Compare all four combinations in `model_runs`. **Decision rule from the
   spec: keep embeddings only if they beat TF-IDF on macro-F1.** Either
   outcome is a good result — write down which won and by how much.
5. Whichever loses is NOT deleted — the embedding vectors get reused in
   Week 9 for semantic search regardless of who won the classifier contest.
6. Commit: "Phase 6: embeddings comparison".

✅ **Done when:** the four-way comparison table is in the README and the
production model is whichever won.

---

## Week 8 (Sep 21–27) — Phase 7: Match scoring — the payoff

**Goal: the tool finally does something FOR you: ranked matches + a learning plan.**

1. First, verify the skill extractor. Pick 25 postings, read them yourself,
   list the skills a human would say each requires, run the regex extractor
   on the same 25, compare. Fix regex patterns that missed things. Note in
   the README what it still can't catch (e.g. "deep learning frameworks"
   with no framework named).
2. Run the extractor over all postings; store results in `posting_skills`.
3. Write `analysis/match_scoring.py`:
   - match score per posting = (skills you have ∩ skills it wants) / (skills it wants)
   - near-miss list = postings where you're missing 2 or fewer skills
   - junior filter = title contains intern/junior/new grad/research assistant
     and does NOT contain senior/staff/principal/lead
   - the unlock table: for each skill you lack, how many additional postings
     would become near-misses if you learned it — sorted descending.
4. Look at the unlock table. That ranked list is your actual, data-derived
   learning plan. Sanity-check it against intuition (PyTorch and SQL should
   rank high; if MATLAB ranks #1, inspect why before believing it).
5. Commit: "Phase 7: match scoring + learning plan".

✅ **Done when:** you have a ranked shortlist of postings and the unlock table,
and you've read both.

---

## Week 9 (Sep 28–Oct 4) — Phase 8a: Semantic search  (+ built-in buffer)

**Goal: "find postings like this one" works.**

1. Write `analysis/semantic_search.py`: load the cached embedding vectors
   from Week 6, compute cosine similarity between a query posting and all
   others, return top-k most similar.
2. Test it: feed it an NLP posting — the top results should be other NLP
   postings. Feed it a retail posting — results should be non-technical.
   If results look random, the most common cause is comparing vectors from
   different encoding runs.
3. This week is deliberately light — it's also the schedule's buffer. If
   you're behind from earlier weeks, catch up here.
4. Commit: "Phase 8a: semantic search".

✅ **Done when:** similar-posting queries return obviously sensible results.

---

## Week 10 (Oct 5–11) — Phase 8b: Interface + automation — ship it

**Goal: a tool you open in the browser, and a pipeline that refreshes itself.**

1. Install Streamlit, skim its "get started" page (15 minutes).
2. Write `app/streamlit_app.py`, two tabs:
   - Tab 1 "Analyze a posting": text box → relevance %, category, detected
     skills (mark which you have vs are missing), learning priority.
   - Tab 2 "My matches & plan": ranked postings table, junior-only toggle,
     near-miss list, the unlock table as a bar chart.
3. Write `pipeline/weekly_update.py`: one script that runs fetch → combine →
   upsert → re-extract skills → re-score, in order. Run it manually once,
   end to end.
4. Schedule it weekly (Windows Task Scheduler) — or skip scheduling and just
   run it manually each Monday; both are fine, note which you chose.
5. Final README pass: setup instructions someone else could follow,
   methodology, all the honest numbers (agreement rate, model table,
   extractor limitations).
6. Final push to GitHub.

✅ **PROJECT DONE when:** you run the weekly update, open the app, and it
shows you this week's ranked matches — a tool you'll actually use.

---

## The survival rules

- **Weeks 1–4 are the project.** Everything after improves it. If life
  happens, cut from the end (semantic search → Streamlit polish), never
  the front.
- **Order within a week matters too** — each part's numbered steps assume
  the previous ones. Don't write combine.py before the fetchers work.
- **Never a zero week.** 30 minutes (label 20 rows, fix one regex) keeps it
  alive.
- **Stuck longer than 45 minutes on one error:** stop, write down exactly
  what you tried, and ask Claude Code with that context. Don't burn a whole
  session on one bug.
- **Commit at every checkpoint,** minimum. Commit messages describe the
  change ("add HTML stripping to combine"), not "update".
