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
