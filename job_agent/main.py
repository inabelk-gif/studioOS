"""Entry point for the daily job-search agent."""

import logging
import re
import time
from typing import Dict, List, Tuple

from job_agent import dedup
from job_agent.company_watch import fetch_company_sites, watched_company
from job_agent.config import (
    ALLOWED_LOCATION_KEYWORDS,
    EXCLUDED_LOCATION_KEYWORDS,
    EXCLUDE_KEYWORDS,
    REMOTE_EXCLUDE_KEYWORDS,
    RELEVANT_JOB_TITLE_KEYWORDS,
    SEARCH_QUERIES,
)
from job_agent.models import Vacancy
from job_agent.ranking import rank, score_and_explain
from job_agent.sources import ALL_SOURCES
from job_agent.telegram_notifier import send_report


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)

logger = logging.getLogger("job_agent")

# Same weight as the strongest search queries (see SEARCH_QUERIES).
COMPANY_SITE_WEIGHT = 9


# Hebrew job titles mark both genders in many ways: "מעצב/ת", "מעצב /ת",
# "מעצב.ת", "מעצב\ת", "גרפי/ת". Strip the suffix so keywords match all.
_GENDER_SUFFIX_RE = re.compile(
    r"\s*[/.\\]\s*(?:ית|ת|ה)(?![֐-׿])"
)


def _normalize(text: str) -> str:
    text = _GENDER_SUFFIX_RE.sub("", text.lower())
    return re.sub(r"\s+", " ", text)


def _contains_keyword(text: str, keywords: List[str]) -> bool:
    text_norm = _normalize(text)

    return any(
        _normalize(keyword) in text_norm
        for keyword in keywords
    )


def _is_relevant_job(vacancy: Vacancy) -> bool:
    """Return True only for genuinely relevant design positions."""

    title = vacancy.title.strip()

    if not title:
        return False

    # First reject explicitly unwanted titles.
    if _contains_keyword(
        title,
        EXCLUDE_KEYWORDS,
    ):
        return False

    # Then require at least one recognised design role.
    return _contains_keyword(
        title,
        RELEVANT_JOB_TITLE_KEYWORDS,
    )


def _is_remote(location: str) -> bool:
    if not location:
        return False

    return _contains_keyword(
        location,
        REMOTE_EXCLUDE_KEYWORDS,
    )


def _is_nearby_location(location: str) -> bool:
    """Return True for the preferred Jerusalem-area locations."""

    if not location:
        return False

    location_lower = location.lower()

    if _is_remote(location):
        return False

    # Israeli boards list several cities per job ("ירושלים, מודיעין,
    # תל אביב"); any preferred city makes the job count as nearby.
    return _contains_keyword(
        location_lower,
        ALLOWED_LOCATION_KEYWORDS,
    )


def _is_in_search_area(location: str) -> bool:
    """For nationwide boards: keep the Jerusalem area and the cities
    listed for the second report section; drop the rest of Israel.
    Jobs without a location are kept."""

    if not location:
        return True

    return _contains_keyword(
        location,
        ALLOWED_LOCATION_KEYWORDS + EXCLUDED_LOCATION_KEYWORDS,
    )


def _content_key(vacancy: Vacancy) -> str:
    """The same job is often posted twice, or on several boards."""

    return "|".join(
        _normalize(part)
        for part in (vacancy.title, vacancy.company, vacancy.location)
    )


def _accept(
    vacancy: Vacancy,
    weight: float,
    query: str,
    nationwide: bool,
    seen_in_run: Dict[str, Vacancy],
    seen_content: Dict[str, str],
) -> None:
    """Filter, score and store one candidate vacancy."""

    # Ignore anything that is not actually
    # a design-related position.
    if not _is_relevant_job(vacancy):
        logger.info(
            "Excluded irrelevant vacancy: %s",
            vacancy.title,
        )
        return

    # Remote-only positions are excluded.
    if _is_remote(vacancy.location):
        logger.info(
            "Excluded remote vacancy: %s",
            vacancy.title,
        )
        return

    if nationwide and not _is_in_search_area(
        vacancy.location
    ):
        logger.info(
            "Excluded far-away vacancy: %s (%s)",
            vacancy.title,
            vacancy.location,
        )
        return

    content_key = _content_key(vacancy)
    first_key = seen_content.setdefault(
        content_key,
        vacancy.dedup_key,
    )

    # Same title/company/location already found
    # under a different id or on another board.
    if first_key != vacancy.dedup_key:
        return

    existing = seen_in_run.get(
        vacancy.dedup_key
    )

    # If we already found the same vacancy through
    # a stronger query, keep that version.
    if existing and existing.score >= weight:
        return

    # Store the actual query that produced this result.
    vacancy.matched_query = query

    company = watched_company(vacancy.company)
    if company:
        vacancy.watched_company = company.name

    score_and_explain(
        vacancy,
        weight,
    )

    seen_in_run[
        vacancy.dedup_key
    ] = vacancy


def collect_vacancies() -> List[Vacancy]:
    seen_in_run: Dict[str, Vacancy] = {}
    seen_content: Dict[str, str] = {}

    # Companies' own careers sites first, so that a job also posted on
    # a board is reported with the company's own link.
    for vacancy in fetch_company_sites():
        _accept(
            vacancy,
            COMPANY_SITE_WEIGHT,
            "",
            False,
            seen_in_run,
            seen_content,
        )

    logger.info(
        "Company sites: %d relevant vacancies",
        len(seen_in_run),
    )

    for source in ALL_SOURCES:
        found_before = len(seen_in_run)

        for query_en, query_he, weight in SEARCH_QUERIES:

            for query in (query_en, query_he):

                logger.info(
                    "Querying %s for %r",
                    source.name,
                    query,
                )

                try:
                    results = source.fetch(query)

                except Exception:
                    logger.exception(
                        "Source %s failed for query %r",
                        source.name,
                        query,
                    )
                    results = []

                for vacancy in results:
                    _accept(
                        vacancy,
                        weight,
                        query,
                        source.nationwide,
                        seen_in_run,
                        seen_content,
                    )

                time.sleep(1)

        logger.info(
            "%s: %d relevant vacancies",
            source.name,
            len(seen_in_run) - found_before,
        )

    return list(seen_in_run.values())


def split_by_location(
    vacancies: List[Vacancy],
) -> Tuple[List[Vacancy], List[Vacancy], List[Vacancy]]:
    """Watched companies first, then nearby, then other locations."""

    watched: List[Vacancy] = []
    nearby: List[Vacancy] = []
    other: List[Vacancy] = []

    for vacancy in vacancies:

        if vacancy.watched_company:
            watched.append(vacancy)
        elif _is_nearby_location(
            vacancy.location
        ):
            nearby.append(vacancy)
        else:
            other.append(vacancy)

    return watched, nearby, other


def main() -> None:

    sent = dedup.load_sent()

    all_vacancies = collect_vacancies()

    new_vacancies = dedup.filter_new(
        all_vacancies,
        sent,
    )

    ranked = rank(
        new_vacancies
    )

    watched, nearby, other = split_by_location(
        ranked
    )

    logger.info(
        "Found %d relevant vacancies: %d from watched companies, "
        "%d nearby, %d other locations",
        len(ranked),
        len(watched),
        len(nearby),
        len(other),
    )

    send_report(
        nearby,
        other,
        watched,
    )

    updated_sent = dedup.mark_sent(
        ranked,
        sent,
    )

    dedup.save_sent(
        updated_sent
    )


if __name__ == "__main__":
    main()
