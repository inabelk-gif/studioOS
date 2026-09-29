"""Fixed listing pages that are fetched once per run (not per query):
the whole page is already limited to design jobs near Jerusalem, and the
title filter in main keeps only the relevant ones."""

import json
import logging
import re
from datetime import datetime, timezone
from typing import List
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from job_agent.models import Vacancy
from job_agent.sources._utils import clean_company, fetch_html, is_recent
from job_agent.sources.drushim import BASE_URL as DRUSHIM_BASE_URL
from job_agent.sources.drushim import _NEXT_DATA_RE, _find_jobs

logger = logging.getLogger(__name__)

# Drushim category 26 ("עיצוב") within 30 km of Jerusalem.
DRUSHIM_DESIGN_JERUSALEM_URL = (
    DRUSHIM_BASE_URL
    + "/jobs/cat26/area/18-19-20/?geolexid=539070&isaa=true&ssaen=3&range=3"
)

# Janglo: Jerusalem-centred English-speaking community board.
JANGLO_URL = "https://www.janglo.net/jobs/graphic_design"


def fetch_drushim_design_jerusalem() -> List[Vacancy]:
    html = fetch_html(DRUSHIM_DESIGN_JERUSALEM_URL, "Drushim design")
    if not html:
        return []

    match = _NEXT_DATA_RE.search(html)
    if not match:
        logger.warning("Drushim design: no __NEXT_DATA__")
        return []

    vacancies = []
    for job in _find_jobs(json.loads(match.group(1))):
        published_at = job.get("publishedAtIso")
        if not job.get("title") or not job.get("jobUrl") or not is_recent(published_at):
            continue
        cities = job.get("cities") or []
        vacancies.append(
            Vacancy(
                title=job["title"].strip(),
                company=clean_company(job.get("companyName")),
                location=", ".join(cities) if cities else (job.get("city") or ""),
                url=DRUSHIM_BASE_URL + job["jobUrl"],
                description=job.get("description") or "",
                published_at=published_at,
                # Same source/id as DrushimSource, so a job found by both
                # is one vacancy.
                source="Drushim",
                external_id=str(job.get("id") or ""),
            )
        )
    return vacancies


def _parse_janglo_date(text: str):
    try:
        return (
            datetime.strptime(text.strip(), "%b %d, %Y")
            .replace(tzinfo=timezone.utc)
            .isoformat()
        )
    except ValueError:
        return None


def fetch_janglo() -> List[Vacancy]:
    html = fetch_html(JANGLO_URL, "Janglo")
    if not html:
        return []

    soup = BeautifulSoup(html, "html.parser")
    vacancies = []

    for card in soup.select("div.regular-post"):
        link = card.select_one('a[href*="item/"]')
        title_el = card.select_one("h4")
        if not link or not title_el:
            continue

        date_el = card.select_one("small")
        published_at = _parse_janglo_date(date_el.get_text()) if date_el else None
        if not is_recent(published_at):
            continue

        location_el = card.select_one(".nicebreak")
        url = urljoin(JANGLO_URL, link["href"])

        vacancies.append(
            Vacancy(
                title=" ".join(title_el.get_text().split()),
                company="חסוי",
                location=" ".join(location_el.get_text().split()) if location_el else "",
                url=url,
                published_at=published_at,
                source="Janglo",
                external_id=re.sub(r".*/item/", "", url),
            )
        )

    return vacancies


ALL_LISTINGS = [
    ("Drushim design (Jerusalem 30 km)", fetch_drushim_design_jerusalem),
    ("Janglo", fetch_janglo),
]
