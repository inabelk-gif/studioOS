"""LinkedIn job source.

Uses LinkedIn's public "guest" job-search endpoint, which returns a page of
job cards as HTML without requiring login. This is not an official,
documented API and may change or be rate-limited by LinkedIn.
"""

import logging
from typing import List
from urllib.parse import urlencode

import requests
from bs4 import BeautifulSoup

from job_agent.config import (
    LINKEDIN_DISTANCE_MILES,
    LINKEDIN_LOCATION,
    REQUEST_HEADERS,
)
from job_agent.models import Vacancy
from job_agent.sources.base import JobSource

logger = logging.getLogger(__name__)

SEARCH_URL = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"

# f_TPR=r604800 => posted in the last 7 days.
DEFAULT_PARAMS = {
    "location": LINKEDIN_LOCATION,
    "distance": str(LINKEDIN_DISTANCE_MILES),
    "f_TPR": "r604800",
    "start": "0",
}


class LinkedInSource(JobSource):
    name = "LinkedIn"

    def fetch(self, query: str) -> List[Vacancy]:
        params = dict(DEFAULT_PARAMS)
        params["keywords"] = query
        url = f"{SEARCH_URL}?{urlencode(params)}"

        try:
            response = requests.get(
                url,
                headers=REQUEST_HEADERS,
                timeout=20,
            )
            response.raise_for_status()
        except requests.RequestException as exc:
            logger.warning(
                "LinkedIn fetch failed for %r: %s",
                query,
                exc,
            )
            return []

        soup = BeautifulSoup(response.text, "html.parser")
        cards = soup.select("li")
        vacancies: List[Vacancy] = []

        for card in cards:
            title_el = card.select_one(".base-search-card__title")
            company_el = card.select_one(".base-search-card__subtitle")
            location_el = card.select_one(".job-search-card__location")
            link_el = (
                card.select_one("a.base-card__full-link")
                or card.select_one("a")
            )
            time_el = card.select_one("time")

            if not (title_el and company_el and link_el):
                continue

            vacancies.append(
                Vacancy(
                    title=title_el.get_text(strip=True),
                    company=company_el.get_text(strip=True),
                    location=(
                        location_el.get_text(strip=True)
                        if location_el
                        else ""
                    ),
                    url=link_el.get("href", "").split("?")[0],
                    description="",
                    published_at=(
                        time_el.get("datetime")
                        if time_el
                        else None
                    ),
                    source=self.name,
                )
            )

        return vacancies
