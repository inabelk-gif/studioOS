"""Scoring and 'why it matches' explanations for found vacancies."""
from datetime import datetime, timezone
from typing import List

from job_agent.config import ALLOWED_LOCATION_KEYWORDS, RELEVANT_SKILLS
from job_agent.models import Vacancy


def _matched_skills(text: str) -> List[str]:
    text_lower = text.lower()
    return [skill for skill in RELEVANT_SKILLS if skill.lower() in text_lower]


def _is_jerusalem(location: str) -> bool:
    location_lower = location.lower()
    return "jerusalem" in location_lower or "ירושלים" in location


def _days_since_published(published_at: str) -> float:
    try:
        published = datetime.fromisoformat(published_at).replace(tzinfo=timezone.utc)
        return (datetime.now(timezone.utc) - published).total_seconds() / 86400
    except (TypeError, ValueError):
        return 999


def score_and_explain(vacancy: Vacancy, query_weight: float) -> Vacancy:
    score = query_weight

    if _is_jerusalem(vacancy.location):
        score += 3

    if vacancy.published_at:
        age_days = _days_since_published(vacancy.published_at)
        if age_days <= 2:
            score += 2
        elif age_days <= 7:
            score += 1

    skills = _matched_skills(f"{vacancy.title} {vacancy.description}")
    if skills:
        score += min(len(skills), 3)

    vacancy.score = score

    reasons = [
        f"Позиция близка к «{vacancy.matched_query}», что соответствует вашему опыту "
        f"Senior Graphic Designer, переходящего в UI/UX и Product Design."
    ]
    if skills:
        reasons.append("Упоминаются релевантные навыки/инструменты: " + ", ".join(skills) + ".")
    if _is_jerusalem(vacancy.location):
        reasons.append("Расположение — Иерусалим.")
    else:
        matched_city = next(
            (kw for kw in ALLOWED_LOCATION_KEYWORDS if kw.lower() in vacancy.location.lower()),
            None,
        )
        if matched_city:
            reasons.append(f"Расположение в радиусе ~30 км от Иерусалима ({matched_city}).")

    vacancy.why_matches = " ".join(reasons)
    return vacancy


def rank(vacancies: List[Vacancy]) -> List[Vacancy]:
    return sorted(vacancies, key=lambda v: v.score, reverse=True)
