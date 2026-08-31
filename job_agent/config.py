"""Configuration for the daily job-search agent.

Nothing sensitive lives here. TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID are
read from environment variables (see .env.example / README.md).
"""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DEDUP_FILE = DATA_DIR / "sent_vacancies.json"

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

# How many days back a vacancy is still considered "new".
DAYS_BACK = 7

# How long dedup history is kept.
DEDUP_RETENTION_DAYS = 60

# LinkedIn distance is specified in miles.
# 50 miles is approximately 80 km from Jerusalem.
LINKEDIN_DISTANCE_MILES = 50

# Search queries:
# (English query, Hebrew query, relevance weight)
SEARCH_QUERIES = [
    ("Senior Graphic Designer", "מעצב גרפי בכיר", 10),
    ("Graphic Designer", "מעצב גרפי", 9),
    ("Visual Designer", "מעצב ויזואלי", 9),
    ("Brand Designer", "מעצב מותג", 8),
    ("Marketing Designer", "מעצב שיווקי", 7),
    ("UI Designer", "מעצב UI", 8),
    ("UI/UX Designer", "מעצב UX/UI", 8),
    ("Product Designer", "מעצב מוצר", 5),
    ("Art Director", "ארט דירקטור", 9),
    ("Graphic Designer", "מעצב/ת גרפית", 9),
]

# Base LinkedIn location.
LINKEDIN_LOCATION = "Jerusalem, Israel"

# Additional location filter.
# LinkedIn performs the main radius search; this list provides an
# additional safety filter for clearly identified nearby locations.
ALLOWED_LOCATION_KEYWORDS = [
    "jerusalem", "ירושלים",
    "mevaseret zion", "מבשרת ציון",
    "beit shemesh", "בית שמש",
    "maale adumim", "ma'ale adumim", "מעלה אדומים",
    "efrat", "אפרת",
    "gush etzion", "גוש עציון", "alon shvut", "אלון שבות",
    "beitar illit", "ביתר עילית",
    "givat zeev", "גבעת זאב",
    "tzur hadassah", "צור הדסה",
    "mateh yehuda", "מטה יהודה",
    "abu ghosh", "אבו גוש",
    "har adar", "הר אדר",
    "mishor adumim", "מישור אדומים",
]

# Job-title/content terms that should exclude a vacancy.
EXCLUDE_KEYWORDS = [
    "גרפיקאי/ת",
    "גרפיקאי.ת",
    "דפוס",
    "junior",
    "mid-level",
    "mid level",
]

# Fully remote listings are excluded.
REMOTE_EXCLUDE_KEYWORDS = [
    "remote",
    "work from home",
    "wfh",
    "anywhere",
    "עבודה מהבית",
    "עבודה מרחוק",
    "מרחוק",
]

# Tools/skills used in the "why it matches" explanation.
RELEVANT_SKILLS = [
    "Figma", "Adobe", "Photoshop", "Illustrator", "InDesign", "Sketch",
    "XD", "Branding", "Brand Identity", "UI", "UX", "Typography",
    "Product Design", "Marketing", "Print", "Packaging",
]

REQUEST_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9,he;q=0.8",
}
