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

# How long dedup history is kept (avoids the file growing forever).
DEDUP_RETENTION_DAYS = 60

# (search query in English, search query in Hebrew, relevance weight)
# Weight is used later for ranking results.
SEARCH_QUERIES = [
    ("Senior Graphic Designer", "מעצב גרפי בכיר", 10),
    ("Graphic Designer", "מעצב גרפי", 9),
    ("Visual Designer", "מעצב ויזואלי", 9),
    ("Brand Designer", "מעצב מותג", 8),
    ("Marketing Designer", "מעצב שיווקי", 7),
    ("UI Designer", "מעצב UI", 8),
    ("UI/UX Designer", "מעצב UX/UI", 8),
    ("Product Designer", "מעצב מוצר", 5),
]

# Base LinkedIn location string. LinkedIn applies its own ~40km default
# radius around this, which covers the "Jerusalem + 30km" requirement well
# enough; ALLOWED_LOCATION_KEYWORDS below is the real, authoritative filter.
LINKEDIN_LOCATION = "Jerusalem, Israel"

# Jerusalem and everything within roughly 30km of it, in English and Hebrew.
# A vacancy is only kept if its location text matches one of these.
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

# Terms that mark a listing as fully remote. Even if a remote listing
# happens to mention an allowed city, it's still excluded per the
# "no remote work" requirement.
REMOTE_EXCLUDE_KEYWORDS = [
    "remote", "work from home", "wfh", "anywhere",
    "עבודה מהבית", "עבודה מרחוק", "מרחוק",
]

# Tools/skills surfaced in the "why it matches" explanation when found in
# the title or description.
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
