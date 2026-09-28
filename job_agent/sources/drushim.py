"""Drushim (drushim.co.il) job source.

The search page is a Next.js app that embeds the first page of results
(25 jobs) as JSON in the <script id="__NEXT_DATA__"> tag, so no login
and no browser are needed.
"""

import json
import logging
import re
from typing import List
from urllib.parse import quote

from job_agent.models import Vacancy
from job_agent.sources._utils import clean_company, fetch_html, is_recent
from job_agent.sources.base import JobSource

logger = logging.getLogger(__name__)

BASE_URL = "https://www.drushim.co.il"
SEARCH_URL = BASE_URL + "/jobs/search/{query}/"

_NEXT_DATA_RE = re.compile(
    r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>',
    re.S,
)


def _find_jobs(data) -> list:
    """Find the 'jobs' list inside the dehydrated react-query state."""

    queries = (
        data.get("props", {})
        .get("pageProps", {})
        .get("dehydratedState", {})
        .get("queries", [])
    )

    for query in queries:
        pages = (query.get("state", {}).get("data") or {})
        if isinstance(pages, dict):
            for page in pages.get("pages", []):
                if isinstance(page, dict) and "jobs" in page:
                    return page["jobs"]

    return []


class DrushimSource(JobSource):
    name = "Drushim"
    nationwide = True

    def fetch(self, query: str) -> List[Vacancy]:

        # The query is part of the URL path, so "UI/UX" must lose its "/".
        html = fetch_html(
            SEARCH_URL.format(query=quote(query.replace("/", " "))),
            self.name,
        )
        if not html:
            return []

        match = _NEXT_DATA_RE.search(html)
        if not match:
            logger.warning("Drushim: no __NEXT_DATA__ for %r", query)
            return []

        try:
            jobs = _find_jobs(json.loads(match.group(1)))
        except (json.JSONDecodeError, AttributeError) as exc:
            logger.warning("Drushim: bad JSON for %r: %s", query, exc)
            return []

        vacancies: List[Vacancy] = []

        for job in jobs:
            title = (job.get("title") or "").strip()
            job_url = job.get("jobUrl") or ""
            published_at = job.get("publishedAtIso")

            if not title or not job_url or not is_recent(published_at):
                continue

            cities = job.get("cities") or []
            location = ", ".join(cities) if cities else (job.get("city") or "")

            vacancies.append(
                Vacancy(
                    title=title,
                    company=clean_company(job.get("companyName")),
                    location=location,
                    url=BASE_URL + job_url,
                    description=job.get("description") or "",
                    published_at=published_at,
                    source=self.name,
                    external_id=str(job.get("id") or ""),
                )
            )

        return vacancies
