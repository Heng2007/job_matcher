"""Hyperparameter tuning for the winning classifier with Optuna.

Responsible for: running an Optuna study over the model that won in train.py,
searching its hyperparameters (and the TF-IDF settings) to squeeze out extra
macro-F1, then saving the tuned model if it actually improves on the default.

Inputs: the labeled training data, the winning model type from train.py, a
trial budget of about 50 trials, and the macro-F1 objective.

Outputs: an Optuna study with per-trial scores, the best parameter set printed
and saved, a tuned .joblib in models/, and a model_runs row for the tuned model.

How I'll know it works: the study completes 50 trials without error, the best
trial's macro-F1 beats or ties the default model's score from train.py, and the
tuned artifact loads and predicts.
"""
