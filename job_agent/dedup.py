"""Persistence of previously-sent vacancies, so the daily report never
repeats a job that was already sent."""
import json
from datetime import datetime, timedelta, timezone
from typing import Dict, Iterable

from job_agent.config import DEDUP_FILE, DEDUP_RETENTION_DAYS
from job_agent.models import Vacancy


def load_sent() -> Dict[str, str]:
    """Returns {dedup_key: date_sent_iso}."""
    if not DEDUP_FILE.exists():
        return {}
    try:
        with open(DEDUP_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def save_sent(sent: Dict[str, str]) -> None:
    DEDUP_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(DEDUP_FILE, "w", encoding="utf-8") as f:
        json.dump(sent, f, ensure_ascii=False, indent=2, sort_keys=True)


def filter_new(vacancies: Iterable[Vacancy], sent: Dict[str, str]) -> list:
    return [v for v in vacancies if v.dedup_key not in sent]


def mark_sent(vacancies: Iterable[Vacancy], sent: Dict[str, str]) -> Dict[str, str]:
    today = datetime.now(timezone.utc).date().isoformat()
    for v in vacancies:
        sent[v.dedup_key] = today
    return prune_old(sent)


def prune_old(sent: Dict[str, str]) -> Dict[str, str]:
    cutoff = datetime.now(timezone.utc).date() - timedelta(days=DEDUP_RETENTION_DAYS)
    pruned = {}
    for key, date_str in sent.items():
        try:
            if datetime.fromisoformat(date_str).date() >= cutoff:
                pruned[key] = date_str
        except ValueError:
            pruned[key] = date_str
    return pruned
