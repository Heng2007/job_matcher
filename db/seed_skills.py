import sys 
from pathlib import Path
import pandas as pd
import sqlite3
sys.path.append(str(Path(__file__).resolve().parent.parent))
import config
from analysis.skills_taxonomy import SKILL_TIER
from db.database import insert_skills, conn

print(insert_skills(conn,SKILL_TIER.items()))