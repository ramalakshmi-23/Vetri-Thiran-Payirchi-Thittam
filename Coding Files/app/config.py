import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"sqlite:///{BASE_DIR / 'fitbuddy.db'}",
)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()

# Current Gemini model IDs. They can be changed in .env if needed.
WORKOUT_MODEL = os.getenv("WORKOUT_MODEL", "gemini-3.1-pro-preview")
TIP_MODEL = os.getenv("TIP_MODEL", "gemini-3.6-flash")

APP_NAME = os.getenv("APP_NAME", "FitBuddy")
