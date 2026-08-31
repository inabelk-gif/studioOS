"""Telegram report formatting and Bot API client."""

from typing import List

import requests

from job_agent.config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
from job_agent.models import Vacancy


TELEGRAM_API_URL = (
    "https://api.telegram.org/bot{token}/sendMessage"
)

MAX_MESSAGE_LENGTH = 4000


def _format_vacancy(
    index: int,
    vacancy: Vacancy,
) -> str:

    location = vacancy.location or "не указано"

    lines = [
        f"<b>{index}. {vacancy.title} — {vacancy.company}</b>",
        f"📍 {location}",
        f"⭐ Почему подходит: {vacancy.why_matches}",
        f"🔗 <a href=\"{vacancy.url}\">Ссылка на вакансию</a>",
    ]

    return "\n".join(lines)


def build_report(
    nearby_vacancies: List[Vacancy],
    other_vacancies: List[Vacancy],
) -> List[str]:
    """Build Telegram messages with nearby jobs first."""

    total = len(nearby_vacancies) + len(other_vacancies)

    if total == 0:
        return [
            "Сегодня новых релевантных вакансий не найдено."
        ]

    chunks: List[str] = []

    header = (
        f"📋 <b>Новые вакансии на сегодня: {total}</b>\n\n"
    )

    current = header

    if nearby_vacancies:
        current += (
            "🟢 <b>ИЕРУСАЛИМ И ОКРЕСТНОСТИ</b>\n\n"
        )

        for i, vacancy in enumerate(
            nearby_vacancies,
            start=1,
        ):
            entry = _format_vacancy(i, vacancy)

            if (
                len(current)
                + len(entry)
                + 2
                > MAX_MESSAGE_LENGTH
            ):
                chunks.append(current.strip())
                current = ""

            current += entry + "\n\n"

    if other_vacancies:
        current += (
            "🟡 <b>РЕЛЕВАНТНЫЕ, НО ДРУГИЕ ГОРОДА</b>\n\n"
        )

        offset = len(nearby_vacancies)

        for i, vacancy in enumerate(
            other_vacancies,
            start=offset + 1,
        ):
            entry = _format_vacancy(i, vacancy)

            if (
                len(current)
                + len(entry)
                + 2
                > MAX_MESSAGE_LENGTH
            ):
                chunks.append(current.strip())
                current = ""

            current += entry + "\n\n"

    if current.strip():
        chunks.append(current.strip())

    return chunks


def send_message(text: str) -> None:

    if (
        not TELEGRAM_BOT_TOKEN
        or not TELEGRAM_CHAT_ID
    ):
        raise RuntimeError(
            "TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID "
            "is not set. See README.md for setup instructions."
        )

    response = requests.post(
        TELEGRAM_API_URL.format(
            token=TELEGRAM_BOT_TOKEN
        ),
        data={
            "chat_id": TELEGRAM_CHAT_ID,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": True,
        },
        timeout=30,
    )

    response.raise_for_status()


def send_report(
    nearby_vacancies: List[Vacancy],
    other_vacancies: List[Vacancy],
) -> None:

    for chunk in build_report(
        nearby_vacancies,
        other_vacancies,
    ):
        send_message(chunk)
