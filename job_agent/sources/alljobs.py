"""AllJobs (alljobs.co.il) job source.

Uses the public guest search page (SearchResultsGuest.aspx), which lists
~30 jobs per page without login. An AllJobs subscription is not needed
for searching; it only matters when applying on the site itself.
"""

import logging
import re
from typing import List
from urllib.parse import urlencode

from bs4 import BeautifulSoup

from job_agent.models import Vacancy
from job_agent.sources._utils import (
    clean_company,
    fetch_html,
    is_recent,
    parse_hebrew_date,
)
from job_agent.sources.base import JobSource

logger = logging.getLogger(__name__)

BASE_URL = "https://www.alljobs.co.il"
SEARCH_URL = BASE_URL + "/SearchResultsGuest.aspx"

_JOB_ID_RE = re.compile(r"JobID=(\d+)")


class AllJobsSource(JobSource):
    name = "AllJobs"
    nationwide = True

    def fetch(self, query: str) -> List[Vacancy]:

        params = {
            "page": "1",
            "position": "",
            "type": "",
            "freetxt": query,
            "city": "",
            "region": "",
        }

        html = fetch_html(f"{SEARCH_URL}?{urlencode(params)}", self.name)
        if not html:
            return []

        soup = BeautifulSoup(html, "html.parser")
        vacancies: List[Vacancy] = []

        for card in soup.select("div.job-content-top"):

            link_el = card.select_one('a[href*="JobID="]')
            if not link_el:
                continue

            job_id_match = _JOB_ID_RE.search(link_el.get("href", ""))
            title = link_el.get_text(" ", strip=True)

            if not job_id_match or not title:
                continue

            date_el = card.select_one(".job-content-top-date")
            published_at = parse_hebrew_date(
                date_el.get_text(" ", strip=True) if date_el else ""
            )
            if not is_recent(published_at):
                continue

            company_el = card.select_one('a[href*="/Employer/"]')

            location = ""
            location_el = card.select_one(".job-content-top-location")
            if location_el:
                cities = [a.get_text(strip=True) for a in location_el.select("a")]
                location = ", ".join(c for c in cities if c)

            desc_el = card.select_one(".job-content-top-desc")

            job_id = job_id_match.group(1)

            vacancies.append(
                Vacancy(
                    title=title,
                    company=clean_company(
                        company_el.get_text(strip=True) if company_el else ""
                    ),
                    location=location,
                    url=f"{BASE_URL}/Search/UploadSingle.aspx?JobID={job_id}",
                    description=(
                        desc_el.get_text(" ", strip=True) if desc_el else ""
                    ),
                    published_at=published_at,
                    source=self.name,
                    external_id=job_id,
                )
            )

        return vacancies
