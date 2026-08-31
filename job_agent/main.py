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


def _is_remote(location: str) -> bool:
    location_lower = location.lower()

    return any(
        keyword.lower() in location_lower
        for keyword in REMOTE_EXCLUDE_KEYWORDS
    )


def _is_nearby_location(location: str) -> bool:
    """Check whether the location belongs to the Jerusalem target area."""

    if not location:
        return False

    location_lower = location.lower()

    if _is_remote(location):
        return False

    if any(
        keyword.lower() in location_lower
        for keyword in EXCLUDED_LOCATION_KEYWORDS
    ):
        return False

    return any(
        keyword.lower() in location_lower
        for keyword in ALLOWED_LOCATION_KEYWORDS
    )


def _is_excluded_vacancy(vacancy: Vacancy) -> bool:
    """Exclude clearly unwanted job titles."""

    title_lower = vacancy.title.lower()

    return any(
        keyword.lower() in title_lower
        for keyword in EXCLUDE_KEYWORDS
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

                    if _is_excluded_vacancy(vacancy):
                        logger.info(
                            "Excluded vacancy: %s",
                            vacancy.title,
                        )
                        continue

                    if _is_remote(vacancy.location):
                        continue

                    existing = seen_in_run.get(
                        vacancy.dedup_key
                    )

                    if existing and existing.score >= weight:
                        continue

                    # Store the actual query that produced the result.
                    vacancy.matched_query = query

                    score_and_explain(
                        vacancy,
                        weight,
                    )

                    seen_in_run[vacancy.dedup_key] = vacancy

                time.sleep(1)

    return list(seen_in_run.values())


def split_by_location(
    vacancies: List[Vacancy],
) -> Tuple[List[Vacancy], List[Vacancy]]:
    """Split relevant vacancies into nearby and other locations."""

    nearby: List[Vacancy] = []
    other: List[Vacancy] = []

    for vacancy in vacancies:

        if _is_nearby_location(vacancy.location):
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

    ranked = rank(new_vacancies)

    nearby, other = split_by_location(ranked)

    logger.info(
        "Found %d vacancies total: %d nearby, %d other locations",
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

    dedup.save_sent(updated_sent)


if __name__ == "__main__":
    main()
