import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
FILTERED_DIR = DATA_DIR / "filtered_datasets"
PROCESSED_DIR = DATA_DIR / "processed"

DATABASE_URL = os.getenv("DATABASE_URL")
OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"
POSTCODES_SQL_PATH = RAW_DIR / "australian-postcodes.sql"