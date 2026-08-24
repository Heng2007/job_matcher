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
   b. tag each frame with its source ('greenhouse', 'kaggle', 'uoft' — the
      values in `config.SOURCES`) and concatenate with `ignore_index=True`.
      There is nothing to rename: all three raw CSVs already share the column
      contract, so `source` is the only missing column, and once the frames
      are concatenated the filename that used to carry that fact is gone.
      Without `ignore_index=True` the three frames keep their own 0-based
      labels, so the combined index repeats and any later `.loc[i]` hits
      several rows at once,
   c. strip HTML tags from descriptions. Run this over the *combined* frame,
      not Greenhouse alone: Greenhouse is where the bulk is (all 5,447 rows
      carry tags) but Kaggle has 1 and UofT 6, and one pass covers all three.
      `BeautifulSoup(x, "html.parser").get_text(" ")` handles the entities
      (`&nbsp;`, `&amp;`) too, so no separate `html.unescape` is needed here —
      and unlike a regex it will not eat literal `&lt;text&gt;` that is
      content rather than markup. Pass a separator: `get_text()` with no
      argument glues words together across `</p><p>` boundaries,
   d. drop rows whose description is shorter than `config.MIN_DESCRIPTION_LENGTH`
      (200). This is a filter, so keep the rows you want with a boolean mask —
      `combined[combined["description"].str.len() >= config.MIN_DESCRIPTION_LENGTH]`
      — rather than dropping rows one at a time while iterating the frame,
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

**Goal: every posting has one of the 5 categories, and you know how much to trust the labels.**

> **Deviation from PROJECT_SPEC, decided 2026-08-14.** The original plan bought
> a Claude API key and ran `ml/label_llm.py` over the corpus (~$3.50). I'm doing
> the same job through Claude Code instead — same model, no key, no spend. The
> structure is unchanged: I hand-label a sample as ground truth, an LLM labels
> the rest, and I measure the agreement between them. Only the transport
> changes. `label_source` stays `'llm'` for the machine-labeled rows because
> that is what they are.

1. Hand-labeling first. Pull 150–200 postings out of the database (mix of all
   three sources). Put them in a spreadsheet with an empty `category` column.
   **Seed the sample so all 5 categories actually appear in it** — run
   `analysis.skills_taxonomy.weak_label_category(f"{title} {description}")`
   over the corpus and draw from each category's pool, plus a random slice.
   Data roles are under 2% of the corpus, so a purely random 200 gives barely
   any — and a class with too few training examples destroys macro-F1 in
   Week 4, which averages F1 equally across all 5. The keyword guess only
   decides *which postings you see*; every label is still yours.
2. Label them yourself in 30-minute sittings across the week (about 40–50 per
   sitting). Use exactly the 5 category names from `config.py` — a typo like
   "Machine learning/AI" vs "Machine learning / AI" will break training later.
3. While labeling, write down (in a notes file) which categories you found
   hard to tell apart. This becomes your README's limitations section.
4. ~~Get a Claude API key.~~ **Skipped — no key, no `.env`, no spend.** Claude
   Code does the labeling directly. (Revisit this in Week 10 if the Streamlit
   app needs to classify pasted postings live — that call has to happen inside
   the app, where there is no chat session.)
5. Export the unlabeled postings to CSV (`posting_id, title, description`).
   Claude Code reads it in chunks and returns `posting_id, category`. Load
   that back into the `labels` table with `label_source = 'llm'`. Keep the
   returned CSVs on disk — that file *is* the audit trail, in place of the
   API script.
6. Calibrate on 40 postings you already hand-labeled. Compare. If agreement is
   below ~75%, tell Claude the rules you're actually applying ("a
   dashboards-heavy Data Scientist posting is Data engineering / analytics to
   me") and redo those 40 before labeling the rest.
7. Label all remaining postings. Store them in the `labels` table with
   `label_source` = 'hanlad' or 'llm'.
8. **Confirm the taxonomy change while labeling** (decided 2026-08-14, before
   any labeling — see below). ✅ Answered 2026-08-23: `Data engineering` was
   not pulling its weight, and neither were three other classes. Collapsed
   8 → 5 — see the second revision note below.
9. Commit: "Phase 3: labels + agreement rate".

✅ **Done when:** every posting has a label, and the README states your
agreement rate **and how the labels were made**.

### Taxonomy revision — decided 2026-08-14, before labeling began

Two changes, still 8 categories:

**Added `Data engineering`.** 826 postings (12.4%) use data-engineering
vocabulary, and they were scattering across Data analyst (265), Not relevant
(209) and Software engineering (203) — the same kind of posting sorted three
ways, which teaches the classifier contradictions rather than a boundary. It's
also a distinct learning path (Airflow, dbt, Kafka vs sklearn, PyTorch), which
is what Week 8's unlock table exists to rank.

**Merged `Classical ML` into `Machine learning`** (renamed from Deep learning,
since the merged class is no longer deep-only). The distinguishing vocabulary
isn't in this corpus: `feature engineering` 23, `clustering` 10, `decision
tree` 0, original hints 23 — against 506 for the generic phrase "machine
learning". Postings say "machine learning" and then name PyTorch. This is a
README finding: **the market doesn't advertise classical ML as a separate
thing.** The surviving axis is domain-based — NLP / LLM is language work,
Machine learning is methods on everything else.

**One trap found while measuring, worth remembering:** `spark` and `databricks`
were excluded from the Data engineering hints because 565 of this corpus's
6,636 postings are Databricks' own ads, and they name both in boilerplate
regardless of role. A keyword that looks like a skill can be a company's
house style — check the company spread before trusting any keyword count.

### Taxonomy revision — decided 2026-08-23, after all 6,636 were labeled

**Collapsed 8 categories to 5.** Final counts across the whole corpus:

| | count | % |
|---|---:|---:|
| Not relevant | 5172 | 77.9 |
| Software engineering | 950 | 14.3 |
| Machine learning | 217 | 3.3 |
| Research assistant | 131 | 2.0 |
| Data engineering | 62 | 0.9 |
| NLP / LLM | 48 | 0.7 |
| Data analyst | 46 | 0.7 |
| Quant / finance | 10 | 0.15 |

Four classes under 1%. Macro-F1 weights every class equally, so with ~10 test
examples in a class a single misclassification moves the headline number by
more than a point — the metric would measure sampling noise. Merged
`Machine learning` + `NLP / LLM` → **Machine learning / AI**, `Data engineering`
+ `Data analyst` → **Data engineering / analytics**, and folded
`Quant / finance` into `Not relevant`. Smallest class is now 108. Merging is a
remap of labels that already exist, so it cost no relabeling —
`db/build_labels.py` applies it.

**The 826 number above was wrong, and the reason it was wrong is the lesson.**
`Data engineering` was added on the strength of "826 postings use
data-engineering vocabulary". After labeling every posting, the real count is
**62** — thirteen times fewer. The 826 counted postings that *mention* Airflow,
ETL or pipelines, which at Databricks and Stripe is nearly every ad regardless
of role. **A keyword count measures vocabulary, not jobs.** Same failure as
`lab` matching SpaceX manufacturing technicians, and as the `Data analyst`
keyword pool turning out to be 1,270 accountants. Sampling more could not have
fixed it: only 29 postings in the corpus carry a data-role title at all.

---

## Week 4 (Aug 24–30) — Phase 4: Baseline models  🏁 the milestone week

**Goal: a trained classifier with honest metrics, pushed to GitHub — nameable on work-study applications.**

1. Write `ml/train.py`. In order: load labeled postings from the database →
   train/test split (stratified by category) → TF-IDF features → train
   Logistic Regression → print macro-F1 and the per-class report → train
   XGBoost on the same features → same report.
2. Generate a confusion matrix image for your best model. Look at it. Name
   the two categories it confuses most.
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
   - junior filter = title matches `config.JUNIOR_TITLE_PATTERN` and does NOT
     match `config.SENIOR_TITLE_PATTERN`. Both patterns are whole-word
     (`\b...\b`) — without that, "intern" matches inside "Internal" and
     "International", and "lead" inside "Leadership".
   - the unlock table: for each skill you lack, how many additional postings
     would become near-misses if you learned it — sorted descending.

   **Known limit of the title filter, measured on the 5,447 Greenhouse rows.**
   A title is a name, not a requirement, so it cannot tell you a posting wants
   8 years of experience. Cross-checking titles against the years stated in
   the descriptions:
   - 35 postings pass the junior title test; exactly **1** of them is a fake
     ("Junior Software Engineer" asking for 7 years).
   - **358** postings ask for ≤1 year but fail the title test, because their
     titles are things like "Data Analyst" with no junior keyword.

   So the filter throws away roughly 358 good postings to catch 1 bad one, and
   tightening the title words makes that worse. If you want to fix it, the
   signal is in the description — 4,636 of 5,447 postings (85%) state a years
   requirement, extractable with something like `(\d{1,2})\s*\+?\s*year`.
   Eligibility then becomes "junior title OR stated years ≤ 2, minus senior
   title, minus years ≥ 5". Decide in this week whether it is worth the
   complexity; the plain title filter is a defensible v1 as long as the README
   says what it misses.
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
