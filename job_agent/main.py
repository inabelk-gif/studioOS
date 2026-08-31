"""Entry point for the daily job-search agent."""

import logging
import time
from typing import Dict, List, Tuple

from job_agent import dedup
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


def _contains_keyword(text: str, keywords: List[str]) -> bool:
    text_lower = text.lower()

    return any(
        keyword.lower() in text_lower
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

    if _contains_keyword(
        location_lower,
        EXCLUDED_LOCATION_KEYWORDS,
    ):
        return False

    return _contains_keyword(
        location_lower,
        ALLOWED_LOCATION_KEYWORDS,
    )


def collect_vacancies() -> List[Vacancy]:
    seen_in_run: Dict[str, Vacancy] = {}

    for source in ALL_SOURCES:

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

                    # Ignore anything that is not actually
                    # a design-related position.
                    if not _is_relevant_job(vacancy):
                        logger.info(
                            "Excluded irrelevant vacancy: %s",
                            vacancy.title,
                        )
                        continue

                    # Remote-only positions are excluded.
                    if _is_remote(vacancy.location):
                        logger.info(
                            "Excluded remote vacancy: %s",
                            vacancy.title,
                        )
                        continue

                    existing = seen_in_run.get(
                        vacancy.dedup_key
                    )

                    # If we already found the same vacancy through
                    # a stronger query, keep that version.
                    if existing and existing.score >= weight:
                        continue

                    # Store the actual query that produced this result.
                    vacancy.matched_query = query

                    score_and_explain(
                        vacancy,
                        weight,
                    )

                    seen_in_run[
                        vacancy.dedup_key
                    ] = vacancy

                time.sleep(1)

    return list(seen_in_run.values())


def split_by_location(
    vacancies: List[Vacancy],
) -> Tuple[List[Vacancy], List[Vacancy]]:
    """Put nearby vacancies first and other locations second."""

    nearby: List[Vacancy] = []
    other: List[Vacancy] = []

    for vacancy in vacancies:

        if _is_nearby_location(
            vacancy.location
        ):
            nearby.append(vacancy)
        else:
            other.append(vacancy)

    return nearby, other


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

    nearby, other = split_by_location(
        ranked
    )

    logger.info(
        "Found %d relevant vacancies: "
        "%d nearby, %d other locations",
        len(ranked),
        len(nearby),
        len(other),
    )

    send_report(
        nearby,
        other,
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
