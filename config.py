"""Project-wide constants: filesystem paths, category names, database filename.

Responsible for: the single place every other module reads paths and the
category list from, so nothing hardcodes a directory or a category string.

Inputs: none — this module holds literals only, no logic and no environment
reads.

Outputs: path constants for the data, model and database locations; the 8
category names used by the classifier; the database filename.

How I'll know it works: every module imports its paths and categories from
here, and changing a path in this file changes it everywhere.
"""

# --- Paths ---
PROJECT_ROOT = "."
DATA_DIR = "data"
RAW_DATA_DIR = "data/raw"
PROCESSED_DATA_DIR = "data/processed"
DB_DIR = "db"
MODELS_DIR = "models"
SCHEMA_PATH = "db/schema.sql"
SKILLS_PROFILE_PATH = "my_skills.json"
SEED_LABELS_PATH = "seed_labels.csv"
GREENHOUSE_TOKENS_PATH = "data/raw/greenhouse_tokens.txt"
KAGGLE_INPUT_DATA = "data/raw/postings.csv"        
KAGGLE_OUTPUT_DATA = "data/raw/kaggle.csv"
UOFT_INPUT_DATA = "data/raw/uoft_workstudy_summer2025.csv"
UOFT_OUTPUT_DATA = "data/raw/uoft.csv"
GREENHOUSE_OUTPUT_DATA = "data/raw/greenhouse.csv"
PROCESSED_OUTPUT_DATA = "data/processed/all_postings.csv"
HAND_LABELED_DATA = "data/processed/hand_label.xlsx"


# --- Database ---
DB_FILENAME = "jobintel.sqlite"
DB_PATH = "db/jobintel.sqlite"

# --- Categories (8-way classifier) ---
CATEGORIES = [
    "Classical ML",
    "Deep learning",
    "NLP / LLM",
    "Data analyst",
    "Software engineering",
    "Research assistant",
    "Quant / finance",
    "Not relevant",
]

NOT_RELEVANT_CATEGORY = "Not relevant"

# --- Sources ---
SOURCES = ["greenhouse", "kaggle", "uoft"]

# --- Cleaning thresholds ---
MIN_DESCRIPTION_LENGTH = 200

# --- Sampling / reproducibility ---
KAGGLE_SAMPLE_SIZE = 1200
RANDOM_SEED = 42                

# --- Junior-eligibility title regexes (Streamlit tab 2 filter) ---
JUNIOR_TITLE_PATTERN = r"\b(?:intern|interns|internship|internships|junior|new grad|new graduate|research assistant)\b"
SENIOR_TITLE_PATTERN = r"\b(?:senior|sr|staff|principal|lead)\b"

# --- Near-miss threshold (match_scoring) ---
NEAR_MISS_MAX_MISSING_SKILLS = 2

# --- External endpoints ---
GREENHOUSE_API_BASE = "https://boards-api.greenhouse.io/v1/boards"
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
