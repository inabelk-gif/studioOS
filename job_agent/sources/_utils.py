"""Helpers shared by the Israeli job-board sources."""

import logging
import re
from datetime import datetime, timedelta, timezone
from typing import Optional

import requests

from job_agent.config import DAYS_BACK, REQUEST_HEADERS

logger = logging.getLogger(__name__)


def fetch_html(url: str, source_name: str) -> Optional[str]:
    """GET a page; log and return None on any network/HTTP error."""

    try:
        response = requests.get(
            url,
            headers=REQUEST_HEADERS,
            timeout=20,
        )
        response.raise_for_status()

    except requests.RequestException as exc:
        logger.warning(
            "%s fetch failed for %s: %s",
            source_name,
            url,
            exc,
        )
        return None

    response.encoding = response.encoding or "utf-8"
    return response.text


_RELATIVE_UNITS = {
    "דקה": "minutes",
    "דקות": "minutes",
    "שעה": "hours",
    "שעות": "hours",
    "יום": "days",
    "ימים": "days",
    "שבוע": "weeks",
    "שבועות": "weeks",
}


def parse_hebrew_date(text: str) -> Optional[str]:
    """Turn 'לפני 21 שעות', '4 ימים', 'היום', '14/09/2026' into an
    ISO date-time string (UTC). Returns None if nothing recognisable."""

    if not text:
        return None

    now = datetime.now(timezone.utc)

    if "היום" in text:
        return now.isoformat()

    if "אתמול" in text:
        return (now - timedelta(days=1)).isoformat()

    match = re.search(r"(\d{1,2})/(\d{1,2})/(\d{4})", text)
    if match:
        day, month, year = (int(g) for g in match.groups())
        try:
            return datetime(year, month, day, tzinfo=timezone.utc).isoformat()
        except ValueError:
            return None

    match = re.search(r"(\d+)\s*(\S+)", text)
    if match and match.group(2) in _RELATIVE_UNITS:
        amount = int(match.group(1))
        unit = _RELATIVE_UNITS[match.group(2)]
        return (now - timedelta(**{unit: amount})).isoformat()

    return None


def is_recent(published_at: Optional[str]) -> bool:
    """True if the date is unknown or within DAYS_BACK days."""

    if not published_at:
        return True

    try:
        published = datetime.fromisoformat(published_at)
    except ValueError:
        return True

    if published.tzinfo is None:
        published = published.replace(tzinfo=timezone.utc)

    return datetime.now(timezone.utc) - published <= timedelta(days=DAYS_BACK)


def clean_company(name: str) -> str:
    """Job boards mark hidden employers as '- חסוי -' and similar."""

    name = (name or "").strip(" -‏‎")
    return name or "חסוי"
