"""Minimal Telegram Bot API client (no extra SDK dependency needed)."""
from typing import List

import requests

from job_agent.config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
from job_agent.models import Vacancy

TELEGRAM_API_URL = "https://api.telegram.org/bot{token}/sendMessage"
MAX_MESSAGE_LENGTH = 4000  # Telegram's hard limit is 4096; leave headroom.


def _format_vacancy(index: int, v: Vacancy) -> str:
    location = v.location or "не указано"
    lines = [
        f"<b>{index}. {v.title} — {v.company}</b>",
        f"📍 {location}",
        f"⭐ Почему подходит: {v.why_matches}",
        f"🔗 <a href=\"{v.url}\">Ссылка на вакансию</a>",
    ]
    return "\n".join(lines)


def build_report(vacancies: List[Vacancy]) -> List[str]:
    """Builds one or more message chunks (Telegram has a message length limit)."""
    if not vacancies:
        return ["Сегодня новых подходящих вакансий не найдено."]

    header = f"📋 Новые вакансии на сегодня: {len(vacancies)}\n"
    chunks: List[str] = []
    current = header

    for i, v in enumerate(vacancies, start=1):
        entry = _format_vacancy(i, v)
        if len(current) + len(entry) + 2 > MAX_MESSAGE_LENGTH:
            chunks.append(current.strip())
            current = ""
        current += entry + "\n\n"

    if current.strip():
        chunks.append(current.strip())

    return chunks


def send_message(text: str) -> None:
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        raise RuntimeError(
            "TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID is not set. "
            "See README.md for setup instructions."
        )

    response = requests.post(
        TELEGRAM_API_URL.format(token=TELEGRAM_BOT_TOKEN),
        data={
            "chat_id": TELEGRAM_CHAT_ID,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": True,
        },
        timeout=30,
    )
    response.raise_for_status()


def send_report(vacancies: List[Vacancy]) -> None:
    for chunk in build_report(vacancies):
        send_message(chunk)
