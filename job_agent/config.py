"""Configuration for the daily job-search agent."""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DEDUP_FILE = DATA_DIR / "sent_vacancies.json"

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

DAYS_BACK = 7
DEDUP_RETENTION_DAYS = 60

# LinkedIn uses miles for its radius parameter.
# 50 miles ≈ 80 km.
LINKEDIN_DISTANCE_MILES = 50

LINKEDIN_LOCATION = "Jerusalem, Israel"


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


# A vacancy must contain at least one of these professional
# terms in its TITLE to be considered relevant.
RELEVANT_JOB_TITLE_KEYWORDS = [
    # Graphic / visual
    "graphic designer",
    "senior graphic designer",
    "visual designer",
    "senior visual designer",
    "brand designer",
    "senior brand designer",
    "marketing designer",
    "senior marketing designer",
    "creative designer",
    "senior creative designer",
    "digital designer",
    "senior digital designer",
    "communication designer",
    "content designer",
    "motion designer",
    "exhibition designer",

    # UI / UX / Product
    "ui designer",
    "ux designer",
    "ux/ui designer",
    "ui/ux designer",
    "product designer",
    "senior product designer",

    # Art direction
    "art director",
    "creative director",

    # Hebrew
    "מעצב גרפי",
    "מעצבת גרפית",
    "מעצב/ת גרפית",
    "מעצב ויזואלי",
    "מעצבת ויזואלית",
    "מעצב מותג",
    "מעצבת מותג",
    "מעצב שיווקי",
    "מעצבת שיווקית",
    "מעצב ui",
    "מעצבת ui",
    "מעצב ux",
    "מעצבת ux",
    "מעצב מוצר",
    "מעצבת מוצר",
    "ארט דירקטור",
    "ארט דיירקטור",
]


# Explicitly unwanted terms.
# These are checked in the vacancy title.
EXCLUDE_KEYWORDS = [
    "גרפיקאי/ת",
    "גרפיקאי.ת",
    "דפוס",
    "junior",
    "mid-level",
    "mid level",
    "ג'וניור",
    "ג׳וניור",
    "מיד-לבל",
    "מיד לבל",
]


REMOTE_EXCLUDE_KEYWORDS = [
    "remote",
    "work from home",
    "wfh",
    "anywhere",
    "עבודה מהבית",
    "עבודה מרחוק",
    "מרחוק",
]


# Locations that we consider part of the Jerusalem-centered
# preferred area.
#
# Shoham is intentionally included.
ALLOWED_LOCATION_KEYWORDS = [
    "jerusalem",
    "ירושלים",

    "maale adumim",
    "ma'ale adumim",
    "מעלה אדומים",

    "mevaseret zion",
    "מבשרת ציון",

    "beit shemesh",
    "בית שמש",

    "modiin",
    "modi'in",
    "modi'in-maccabim-reut",
    "modiin-maccabim-reut",
    "מודיעין",
    "מודיעין-מכבים-רעות",

    "gush etzion",
    "גוש עציון",
    "alon shvut",
    "אלון שבות",

    "efrat",
    "אפרת",

    "beitar illit",
    "ביתר עילית",

    "givat zeev",
    "גבעת זאב",

    "tzur hadassah",
    "צור הדסה",

    "abu ghosh",
    "אבו גוש",

    "har adar",
    "הר אדר",

    "mateh yehuda",
    "מטה יהודה",

    "mishor adumim",
    "מישור אדומים",

    "shoham",
    "שהם",
]


# These are definitely outside the preferred area.
# They are NOT discarded; relevant vacancies from these locations
# go into the second Telegram section.
EXCLUDED_LOCATION_KEYWORDS = [
    "tel aviv",
    "tel-aviv",
    "tel aviv-yafo",
    "tel-aviv-yafo",
    "תל אביב",
    "yafo",
    "יפו",

    "bnei brak",
    "בני ברק",

    "ramat gan",
    "רמת גן",

    "givatayim",
    "גבעתיים",

    "herzliya",
    "הרצליה",

    "petah tikva",
    "פתח תקווה",

    "kfar saba",
    "כפר סבא",

    "ra'anana",
    "רעננה",

    "hod hasharon",
    "הוד השרון",

    "rishon lezion",
    "ראשון לציון",

    "holon",
    "חולון",

    "bat yam",
    "בת ים",

    "netanya",
    "נתניה",

    "haifa",
    "חיפה",
]


RELEVANT_SKILLS = [
    "Figma",
    "Adobe",
    "Photoshop",
    "Illustrator",
    "InDesign",
    "Sketch",
    "XD",
    "Branding",
    "Brand Identity",
    "UI",
    "UX",
    "Typography",
    "Product Design",
    "Marketing",
    "Print",
    "Packaging",
]


REQUEST_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9,he;q=0.8",
}
