"""Entry point: run one full daily job-search cycle.

1. Query every registered source for every search term.
2. Filter by allowed location and exclude remote-only listings.
3. Exclude unwanted job titles/content.
4. Drop vacancies already sent on a previous run.
5. Score and rank what's left.
6. Send the report to Telegram.
7. Persist the updated "already sent" history.
"""

import logging
import time
from typing import Dict, List

from job_agent import dedup
from job_agent.config import (
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


def _is_allowed_location(location: str) -> bool:
    """Accept locations returned by LinkedIn's radius search,
    while excluding remote-only jobs.
    """
    if not location:
        return False

    location_lower = location.lower()

    if any(
        bad.lower() in location_lower
        for bad in REMOTE_EXCLUDE_KEYWORDS
    ):
        return False

    return True


def _is_excluded_vacancy(vacancy: Vacancy) -> bool:
    """Exclude unwanted job titles and listings."""

    title_lower = vacancy.title.lower()
    description_lower = vacancy.description.lower()

    # For title-related exclusions, check the title.
    # For "דפוס", also check the description when available.
    if any(
        keyword.lower() in title_lower
        for keyword in EXCLUDE_KEYWORDS
    ):
        return True

    if any(
        keyword.lower() in description_lower
        for keyword in ["דפוס"]
    ):
        return True

    return False


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
                    # Location filter
                    if not _is_allowed_location(vacancy.location):
                        continue

                    # Unwanted job filter
                    if _is_excluded_vacancy(vacancy):
                        logger.info(
                            "Excluded vacancy: %s",
                            vacancy.title,
                        )
                        continue

                    existing = seen_in_run.get(vacancy.dedup_key)

                    if existing and existing.score >= weight:
                        continue

                    vacancy.matched_query = query_en

                    score_and_explain(
                        vacancy,
                        weight,
                    )

                    seen_in_run[vacancy.dedup_key] = vacancy

                time.sleep(1)

    return list(seen_in_run.values())


def main() -> None:
    sent = dedup.load_sent()

    all_vacancies = collect_vacancies()
    new_vacancies = dedup.filter_new(
        all_vacancies,
        sent,
    )
    ranked = rank(new_vacancies)

    logger.info(
        "Found %d vacancies total, %d new after dedup",
        len(all_vacancies),
        len(ranked),
    )

    send_report(ranked)

    updated_sent = dedup.mark_sent(
        ranked,
        sent,
    )
    dedup.save_sent(updated_sent)


if __name__ == "__main__":
    main()
