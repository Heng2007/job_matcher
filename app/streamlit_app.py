"""Streamlit UI for the job intelligence tool.

Responsible for: the two-tab front end over everything else in the project.
Tab 1, "Analyze a posting": paste a job description, get back relevance %,
predicted category, detected skills colour-coded (green = I have it, red =
missing), and a learning priority list of the missing skills ordered by tier.
Tab 2, "My matches & plan": postings ranked by match %, a junior-eligible
filter (title matches intern|junior|new grad|research assistant, excluding
senior|staff|principal|lead), the near-miss list, and the "learn X -> unlock N
postings" bar chart. Until the models exist, the app shows "model not trained
yet" placeholders instead of crashing.

Inputs: the database at db/jobintel.sqlite; the saved model artifacts in
models/; my_skills.json; pasted text from the user.

Outputs: the rendered two-tab web app — no files written.

How I'll know it works: `streamlit run app/streamlit_app.py` opens both tabs
with real data, pasting a known ML posting shows a sensible category and skill
breakdown, and the app still loads cleanly on a machine where no model has been
trained yet.
"""
