"""Daily check of the watched companies' own careers sites, and
recognition of watched companies in vacancies from the job boards."""

import hashlib
import logging
import re
from typing import List, Optional

import requests
from bs4 import BeautifulSoup

from job_agent.companies import WATCHED_COMPANIES, Company
from job_agent.config import REQUEST_HEADERS
from job_agent.models import Vacancy
from job_agent.sources._utils import fetch_html, is_recent

logger = logging.getLogger(__name__)

WORKDAY_PAGE_SIZE = 20
WORKDAY_MAX_JOBS = 100


def _source_name(company: Company) -> str:
    return f"сайт {company.name}"


def _israel_only(location: str) -> bool:
    return bool(re.search(r"israel|ישראל|jerusalem|ירושלים", location or "", re.I))


def _fetch_lever(company: Company, account: str) -> List[Vacancy]:
    url = f"https://api.eu.lever.co/v0/postings/{account}?mode=json"
    response = requests.get(url, headers=REQUEST_HEADERS, timeout=30)
    response.raise_for_status()

    vacancies = []
    for posting in response.json():
        location = (posting.get("categories") or {}).get("location") or ""
        if not _israel_only(location):
            continue
        vacancies.append(
            Vacancy(
                title=posting.get("text", ""),
                company=company.name,
                location=location,
                url=posting.get("hostedUrl", ""),
                description=posting.get("descriptionPlain", "")[:2000],
                source=_source_name(company),
                external_id=posting.get("id", ""),
            )
        )
    return vacancies


def _fetch_greenhouse(company: Company, board: str) -> List[Vacancy]:
    url = f"https://boards-api.greenhouse.io/v1/boards/{board}/jobs"
    response = requests.get(url, headers=REQUEST_HEADERS, timeout=30)
    response.raise_for_status()

    return [
        Vacancy(
            title=job.get("title", ""),
            company=company.name,
            location=(job.get("location") or {}).get("name", ""),
            url=job.get("absolute_url", ""),
            published_at=job.get("updated_at"),
            source=_source_name(company),
            external_id=str(job.get("id", "")),
        )
        for job in response.json().get("jobs", [])
    ]


def _fetch_workday(company: Company, host: str, tenant: str, site: str) -> List[Vacancy]:
    url = f"https://{host}/wday/cxs/{tenant}/{site}/jobs"
    headers = {**REQUEST_HEADERS, "Content-Type": "application/json"}
    vacancies = []

    # Search "designer" and keep Israeli jobs; the title filter in main
    # then drops e.g. "Mechanical Design Engineer".
    for offset in range(0, WORKDAY_MAX_JOBS, WORKDAY_PAGE_SIZE):
        response = requests.post(
            url,
            json={
                "appliedFacets": {},
                "limit": WORKDAY_PAGE_SIZE,
                "offset": offset,
                "searchText": "designer",
            },
            headers=headers,
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
        postings = data.get("jobPostings", [])

        for job in postings:
            location = job.get("locationsText", "")
            if not _israel_only(location):
                continue
            path = job.get("externalPath", "")
            vacancies.append(
                Vacancy(
                    title=job.get("title", ""),
                    company=company.name,
                    location=location,
                    url=f"https://{host}/{site}{path}",
                    source=_source_name(company),
                    external_id=path,
                )
            )

        if offset + WORKDAY_PAGE_SIZE >= (data.get("total") or 0) or not postings:
            break

    return vacancies


def _fetch_page(company: Company, url: str) -> List[Vacancy]:
    """Every short line of the careers page becomes a candidate title;
    main keeps only lines that look like design jobs, and the sent-history
    makes sure each line is reported once."""

    html = fetch_html(url, _source_name(company))
    if html is None:
        raise RuntimeError("page not available")

    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript", "svg", "nav", "footer"]):
        tag.decompose()

    vacancies = []
    seen = set()
    for line in soup.get_text("\n").split("\n"):
        line = " ".join(line.split())
        if not 4 <= len(line) <= 120 or line in seen:
            continue
        seen.add(line)
        line_id = hashlib.sha1(line.encode("utf-8")).hexdigest()[:12]
        vacancies.append(
            Vacancy(
                title=line,
                company=company.name,
                location="ירושלים",
                url=url,
                source=_source_name(company),
                external_id=line_id,
            )
        )
    return vacancies


_FETCHERS = {
    "lever": _fetch_lever,
    "greenhouse": _fetch_greenhouse,
    "workday": _fetch_workday,
    "page": _fetch_page,
}


def fetch_company_sites() -> List[Vacancy]:
    """All candidate vacancies from the companies' own sites. A broken
    site is logged and skipped."""

    vacancies: List[Vacancy] = []

    for company in WATCHED_COMPANIES:
        if not company.watch:
            continue

        kind, *args = company.watch
        try:
            found = [v for v in _FETCHERS[kind](company, *args) if is_recent(v.published_at)]
        except Exception as exc:
            logger.warning("Company site %s (%s) failed: %s", company.name, kind, exc)
            continue

        logger.info("Company site %s: %d candidates", company.name, len(found))
        vacancies.extend(found)

    return vacancies


def _alias_pattern(alias: str) -> re.Pattern:
    # Short all-caps names ("RAD", "MKS") must match exactly, so that
    # "Rad" inside other names does not count.
    flags = 0 if len(alias) <= 3 and alias.isupper() else re.IGNORECASE
    return re.compile(rf"(?<!\w){re.escape(alias)}(?!\w)", flags)


_ALIASES = [
    (company, _alias_pattern(alias))
    for company in WATCHED_COMPANIES
    for alias in company.aliases
]


def watched_company(company_name: str) -> Optional[Company]:
    """The watched company this job-board company name refers to, if any."""

    if not company_name:
        return None
    for company, pattern in _ALIASES:
        if pattern.search(company_name):
            return company
    return None
