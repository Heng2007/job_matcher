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
import torch
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer 
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report


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
fitted_x_train = vectorizer.fit_transform(X_train)
fitted_x_test = vectorizer.transform(X_test)
fitted_y_train = vectorizer.fit_transform(Y_train)
fitted_y_test = vectorizer.transform(Y_test)



# Logistic Regression--------------------------------------------------------------------------------------------------
model = LogisticRegression(C = 100, class_weight = "balanced", solver= "lbfgs", max_iter= 1000).fit(fitted_x_train, Y_train)


def logistic_predict(input):
        """Return the predicted outcome(s) as a numpy array of label strings."""
        model_prediction = model.predict(input)
        return model_prediction

# MLP-------------------------------------------------------------------------------------------------------------------

# Order of steps:

# Encode labels — LabelEncoder fit on Y_train, then .transform on Y_test with the same fitted encoder. You'll need it again at the end to turn 
# predictions back into category names.
# Tensors — .toarray() → torch.tensor(..., dtype=torch.float32) for both feature matrices; labels as torch.long.
# Model — nn.Sequential: Linear(34217 → hidden) → ReLU → Dropout → Linear(hidden → 5). Output raw scores, no softmax.
# Loss + optimizer — nn.CrossEntropyLoss (it applies softmax internally, which is why step 3 doesn't) and torch.optim.Adam.
# Training loop — TensorDataset + DataLoader for batching, then per batch: zero grads → forward → loss → backward → step.
# Evaluate — model.eval() + torch.no_grad(), argmax the logits, inverse_transform back to strings, feed to the same classification_report. Compare the macro avg to LogReg's 0.74.
# Two things that will bite: CrossEntropyLoss needs a weight= argument to
#  match the class_weight="balanced" you gave LogReg, otherwise the comparison isn't
#  fair and the net will just learn "Not relevant". And set torch.manual_seed(config.RANDOM_SEED) 
# or your numbers move every run


x_train_tensor = torch.tensor(fitted_x_train.toarray(), dtype =torch.float32)
x_test_tensor = torch.tensor(fitted_x_test.toarray(), dtype = torch.float32)

