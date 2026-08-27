"""Entry point: run one full daily job-search cycle.

1. Query every registered source for every search term.
2. Filter by allowed location and exclude remote-only listings.
3. Drop vacancies already sent on a previous run.
4. Score and rank what's left.
5. Send the report to Telegram.
6. Persist the updated "already sent" history.
"""
import logging
import time
from typing import Dict, List

from job_agent import dedup
from job_agent.config import ALLOWED_LOCATION_KEYWORDS, REMOTE_EXCLUDE_KEYWORDS, SEARCH_QUERIES
from job_agent.models import Vacancy
from job_agent.ranking import rank, score_and_explain
from job_agent.sources import ALL_SOURCES
from job_agent.telegram_notifier import send_report

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("job_agent")


def _is_allowed_location(location: str) -> bool:
    if not location:
        return False
    location_lower = location.lower()
    if any(bad in location_lower for bad in REMOTE_EXCLUDE_KEYWORDS):
        return False
    return any(kw.lower() in location_lower for kw in ALLOWED_LOCATION_KEYWORDS)


def collect_vacancies() -> List[Vacancy]:
    seen_in_run: Dict[str, Vacancy] = {}

    for source in ALL_SOURCES:
        for query_en, query_he, weight in SEARCH_QUERIES:
            for query in (query_en, query_he):
                logger.info("Querying %s for %r", source.name, query)
                try:
                    results = source.fetch(query)
                except Exception:
                    logger.exception("Source %s failed for query %r", source.name, query)
                    results = []

                for vacancy in results:
                    if not _is_allowed_location(vacancy.location):
                        continue

                    existing = seen_in_run.get(vacancy.dedup_key)
                    if existing and existing.score >= weight:
                        continue

                    vacancy.matched_query = query_en
                    score_and_explain(vacancy, weight)
                    seen_in_run[vacancy.dedup_key] = vacancy

                time.sleep(1)  # be polite to the source

    return list(seen_in_run.values())


def main() -> None:
    sent = dedup.load_sent()

    all_vacancies = collect_vacancies()
    new_vacancies = dedup.filter_new(all_vacancies, sent)
    ranked = rank(new_vacancies)

    logger.info(
        "Found %d vacancies total, %d new after dedup", len(all_vacancies), len(ranked)
    )

    send_report(ranked)

    updated_sent = dedup.mark_sent(ranked, sent)
    dedup.save_sent(updated_sent)


if __name__ == "__main__":
    main()
