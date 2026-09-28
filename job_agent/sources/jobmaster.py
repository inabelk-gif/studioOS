"""JobMaster (jobmaster.co.il) job source.

The public search page (/jobs/?q=...) renders job cards as
<article class="JobItem" data-jobnum="..."> without login.
"""

import logging
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

BASE_URL = "https://www.jobmaster.co.il"
SEARCH_URL = BASE_URL + "/jobs/"


class JobMasterSource(JobSource):
    name = "JobMaster"
    nationwide = True

    def fetch(self, query: str) -> List[Vacancy]:

        # JobMaster redirects ?q= to a path (/jobs/q-.../), where "/" 404s.
        html = fetch_html(
            f"{SEARCH_URL}?{urlencode({'q': query.replace('/', ' ')})}",
            self.name,
        )
        if not html:
            return []

        soup = BeautifulSoup(html, "html.parser")
        vacancies: List[Vacancy] = []

        for card in soup.select("article.JobItem[data-jobnum]"):

            job_num = card.get("data-jobnum", "").strip()
            title_el = card.select_one(".CardHeader")

            if not job_num or not title_el:
                continue

            title = title_el.get_text(" ", strip=True)
            if not title:
                continue

            date_el = card.select_one("span.Gray")
            published_at = parse_hebrew_date(
                date_el.get_text(" ", strip=True) if date_el else ""
            )
            if not is_recent(published_at):
                continue

            company_el = (
                card.select_one(".CompanyNameLink")
                or card.select_one(".ByTitle")
            )

            location_el = card.select_one(".jobLocation")
            location = ""
            if location_el:
                cities = [a.get_text(strip=True) for a in location_el.select("a")]
                location = ", ".join(c for c in cities if c)

            desc_el = card.select_one(".jobShortDescription")

            vacancies.append(
                Vacancy(
                    title=title,
                    company=clean_company(
                        company_el.get_text(strip=True) if company_el else ""
                    ),
                    location=location,
                    url=f"{BASE_URL}/jobs/checknum.asp?key={job_num}",
                    description=(
                        desc_el.get_text(" ", strip=True) if desc_el else ""
                    ),
                    published_at=published_at,
                    source=self.name,
                    external_id=job_num,
                )
            )

        return vacancies
