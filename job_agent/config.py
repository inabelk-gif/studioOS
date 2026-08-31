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
# 50 miles is approximately 80 km.
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

# These terms exclude unwanted vacancies.
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

# Cities/areas that are acceptable within the intended
# Jerusalem-centered search area.
#
# Tel Aviv metro is deliberately excluded even though parts of
# it can fall within a 65 km straight-line radius.
ALLOWED_LOCATION_KEYWORDS = [
    # Jerusalem
    "jerusalem",
    "ירושלים",

    # East / west Jerusalem area
    "maale adumim",
    "ma'ale adumim",
    "מעלה אדומים",
    "mevaseret zion",
    "מבשרת ציון",
    "abu ghosh",
    "אבו גוש",
    "har adar",
    "הר אדר",
    "givat zeev",
    "גבעת זאב",
    "beitar illit",
    "beitar illit",
    "ביתר עילית",
    "tzur hadassah",
    "צור הדסה",

    # Judea / Jerusalem district
    "beit shemesh",
    "בית שמש",
    "efrat",
    "אפרת",
    "gush etzion",
    "גוש עציון",
    "alon shvut",
    "אלון שבות",
    "mateh yehuda",
    "מטה יהודה",

    # North-west / west of Jerusalem
    "modiin",
    "modi'in",
    "modi'in-maccabim-reut",
    "modiin-maccabim-reut",
    "מודיעין",
    "מודיעין-מכבים-רעות",
    "maccabim",
    "מכבים",

    # Central locations that can reasonably fall within the
    # broader search area
    "ramla",
    "רמלה",
    "lod",
    "לוד",
    "rehovot",
    "רחובות",
    "yavne",
    "יבנה",
    "ashdod",
    "אשדוד",
    "kiryat malakhi",
    "קריית מלאכי",

    # North / north-east of Jerusalem
    "beit shean",
    "בית שאן",
    "ariel",
    "אריאל",
]

# Explicitly excluded metropolitan areas.
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
