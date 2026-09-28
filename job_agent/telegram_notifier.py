"""Telegram report formatting and Bot API client."""

from html import escape
from typing import List, Sequence

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
    source = f" ({vacancy.source})" if vacancy.source else ""

    lines = [
        f"<b>{index}. {escape(vacancy.title)} — {escape(vacancy.company)}</b>",
        f"📍 {escape(location)}",
        f"⭐ Почему подходит: {escape(vacancy.why_matches)}",
        f"🔗 <a href=\"{escape(vacancy.url)}\">Ссылка на вакансию</a>{escape(source)}",
    ]

    return "\n".join(lines)


def build_report(
    nearby_vacancies: List[Vacancy],
    other_vacancies: List[Vacancy],
    watched_vacancies: Sequence[Vacancy] = (),
) -> List[str]:
    """Build Telegram messages: watched companies, then nearby jobs,
    then other cities."""

    sections = [
        ("🏢 <b>КОМПАНИИ ИЗ ВАШЕГО СПИСКА</b>", list(watched_vacancies)),
        ("🟢 <b>ИЕРУСАЛИМ И ОКРЕСТНОСТИ</b>", nearby_vacancies),
        ("🟡 <b>РЕЛЕВАНТНЫЕ, НО ДРУГИЕ ГОРОДА</b>", other_vacancies),
    ]

    total = sum(len(vacancies) for _, vacancies in sections)

    if total == 0:
        return [
            "Сегодня новых релевантных вакансий не найдено."
        ]

    chunks: List[str] = []

    current = (
        f"📋 <b>Новые вакансии на сегодня: {total}</b>\n\n"
    )

    index = 0

    for heading, vacancies in sections:

        if not vacancies:
            continue

        current += heading + "\n\n"

        for vacancy in vacancies:
            index += 1
            entry = _format_vacancy(index, vacancy)

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
    watched_vacancies: Sequence[Vacancy] = (),
) -> None:

    for chunk in build_report(
        nearby_vacancies,
        other_vacancies,
        watched_vacancies,
    ):
        send_message(chunk)
