"""Train and compare the 5-way posting classifier.

Responsible for: turning labeled postings into TF-IDF features, fitting a
logistic regression, an XGBoost model on them and pytorch model on them, comparing the three, and
saving the winner for the rest of the tool to use. One 5-way classifier.

Inputs: labeled postings from the database (description text and category);
the category list from config; a train/test split.

Outputs: a fitted vectorizer and model saved as .joblib in models/; a macro-F1
score and confusion matrix for each candidate; a row in the model_runs table
recording the run date, model name and macro-F1.

How I'll know it works: both models train without error, macro-F1 is reported
per model, the confusion matrix shows the errors are spread across categories
rather than everything collapsing into one class, and the saved artifact
reloads and predicts on a fresh posting.
"""


import sys 
from pathlib import Path
import pandas as pd
import sqlite3
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer 
sys.path.append(str(Path(__file__).resolve().parent.parent))
import config



conn = sqlite3.connect(config.DB_PATH)
df = pd.read_sql_query("SELECT p.title, p.description, l.category "
                        "FROM postings p "
                        "JOIN labels l ON l.posting_id = p.id", conn)

X = df["title"] + " "+ df["description"]
Y = df["category"]

X_train, X_test, Y_train, Y_test = train_test_split(X, Y, stratify= Y, test_size= 0.2, random_state= config.RANDOM_SEED)

vectorizer = TfidfVectorizer()
fitted = vectorizer.fit_transform(X_train)
print(X.shape)

#.venv/bin/python -m ml.train