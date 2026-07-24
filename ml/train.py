"""Train and compare the 8-way posting classifier.

Responsible for: turning labeled postings into TF-IDF features, fitting a
logistic regression and an XGBoost model on them, comparing the two, and
saving the winner for the rest of the tool to use. One 8-way classifier, not a
binary model plus a multiclass one; relevance is 1 - P(Not relevant).

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
