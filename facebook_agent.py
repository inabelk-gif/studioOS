"""
Помощник для групп Facebook: открывает Chrome на этом компьютере,
просматривает свежие посты в группах из facebook_groups.txt, находит
вакансии дизайнера и присылает их в тот же Telegram-бот.

Работает только на компьютере пользователя (не на GitHub): Facebook
требует входа в аккаунт.

Первый запуск — войти в Facebook (один раз, вход запоминается):
    python facebook_agent.py --login
    (в открывшемся окне войдите в Facebook сами, затем закройте окно)

Обычный запуск (отправит новые вакансии в Telegram):
    python facebook_agent.py

Проверка без отправки в Telegram:
    python facebook_agent.py --dry-run
"""
import hashlib
import json
import os
import random
import re
import sys
import time
from datetime import date, timedelta
from html import escape
from pathlib import Path

from playwright.sync_api import sync_playwright

from job_agent.config import (
    ALLOWED_LOCATION_KEYWORDS,
    EXCLUDE_KEYWORDS,
    RELEVANT_JOB_TITLE_KEYWORDS,
)
from job_agent.main import _contains_keyword
from job_agent.telegram_notifier import MAX_MESSAGE_LENGTH, send_message

BASE_DIR = Path(__file__).resolve().parent
GROUPS_FILE = BASE_DIR / "facebook_groups.txt"
# Отдельный профиль Chrome: вход в Facebook хранится здесь, основной
# Chrome пользователя не затрагивается.
PROFILE_DIR = BASE_DIR / "chrome_fb_profile"
SEEN_FILE = BASE_DIR / "data" / "facebook_seen.json"
SEEN_RETENTION_DAYS = 60

# Facebook убирает из страницы пролистанные посты, поэтому лента
# листается короткими шагами (меньше экрана) и читается после каждого.
SCROLLS_PER_GROUP = 30

CHROME_PATHS = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
]

# Пост — вакансия дизайнера, если в нём есть слово про дизайнера...
DESIGN_KEYWORDS = RELEVANT_JOB_TITLE_KEYWORDS + [
    "designer",
    "מעצב",
    "מעצבת",
    "дизайнер",
]

# ...и слово про найм.
HIRING_KEYWORDS = [
    "דרוש", "דרושה", "דרושים", "דרושות",
    "מגייס", "מגייסת", "מגייסים", "מגייסות",
    "מחפשים", "מחפשות", "משרה", "משרת", "קורות חיים", "קו\"ח", "קו״ח",
    "hiring", "we're looking", "we are looking", "looking for a",
    "job opening", "position", "join our team", "cv", "resume",
    "требуется", "ищем", "вакансия",
]

# Люди, которые сами ищут работу или предлагают услуги, — не вакансии.
SEEKER_KEYWORDS = [
    "מחפשת עבודה", "מחפש עבודה", "מחפשת משרה", "מחפש משרה",
    "פנויה לעבודה", "פנוי לעבודה", "פנויה לפרויקטים", "פנוי לפרויקטים",
    "looking for work", "looking for a job", "open to work",
    "ищу работу",
    "האתגר הבא שלי", "מחפש את האתגר הבא", "מחפשת את האתגר הבא",
]

# Вакансии для начинающих — не нужны (дополнение к EXCLUDE_KEYWORDS).
JUNIOR_KEYWORDS = ["בתחילת הדרך", "ללא ניסיון", "entry level", "entry-level"]

# Посты старше этого не присылаются (в группах бывают старые посты).
MAX_POST_AGE_DAYS = 14

_RU_MONTHS = {
    "январ": 1, "феврал": 2, "март": 3, "апрел": 4, "ма": 5, "июн": 6,
    "июл": 7, "август": 8, "сентябр": 9, "октябр": 10, "ноябр": 11,
    "декабр": 12,
}
_DATE_RE = re.compile(
    r"(\d{1,2})\s+(январ|феврал|март|апрел|ма[йя]|июн|июл|август|сентябр"
    r"|октябр|ноябр|декабр)\w*\.?(?:\s+(\d{4}))?",
    re.IGNORECASE,
)
_DAYS_AGO_RE = re.compile(r"(\d+)\s*(?:дн|день|дня|дней|нед)", re.IGNORECASE)

# Выполняется в странице группы: собирает посты ленты.
EXTRACT_POSTS_JS = r"""
() => {
  const feed = document.querySelector('div[role="feed"]');
  let posts = feed ? Array.from(feed.children) : [];
  if (!posts.length) {
    posts = Array.from(document.querySelectorAll('div[role="article"]'))
      .filter(a => !a.parentElement.closest('div[role="article"]'));
  }
  const linkRe = /\/(posts|permalink)\/|story_fbid=|multi_permalinks=/;
  return posts.map(p => {
    const msg = Array.from(p.querySelectorAll(
      '[data-ad-preview="message"], [data-ad-comet-preview="message"]'
    )).map(e => e.innerText).join('\n').trim();
    const text = (msg || p.innerText || '').trim();
    let link = '';
    for (const a of p.querySelectorAll('a[href]')) {
      if (linkRe.test(a.href) && !a.href.includes('comment_id=')) {
        link = a.href; break;
      }
    }
    const author = p.querySelector('h2, h3, h4, strong');
    return {
      text: text.slice(0, 3000),
      link,
      author: author ? author.innerText.trim().split('\n')[0] : '',
      // Шапка поста с датой («9 сентябрь», «1 дн.»).
      header: (p.innerText || '').slice(0, 400),
    };
  }).filter(p => p.text.length > 20);
}
"""

# Раскрывает длинные посты («Ещё» / «See more» / «ראה עוד»).
EXPAND_JS = r"""
() => {
  const labels = ['see more', 'ראה עוד', 'עוד', 'ещё', 'еще'];
  let n = 0;
  for (const b of document.querySelectorAll('div[role="feed"] div[role="button"]')) {
    const t = (b.innerText || '').trim().toLowerCase();
    if (labels.includes(t)) { b.click(); n++; }
  }
  return n;
}
"""


def _find_chrome() -> str:
    for path in CHROME_PATHS:
        if os.path.exists(path):
            return path
    raise RuntimeError("Не найден Google Chrome.")


def load_groups() -> list:
    if not GROUPS_FILE.exists():
        return []
    groups = []
    for line in GROUPS_FILE.read_text(encoding="utf-8").splitlines():
        line = line.split("#", 1)[0].strip()
        if line.startswith("http"):
            groups.append(line)
    return groups


def load_seen() -> dict:
    try:
        return json.loads(SEEN_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def save_seen(seen: dict) -> None:
    cutoff = (date.today() - timedelta(days=SEEN_RETENTION_DAYS)).isoformat()
    seen = {k: v for k, v in seen.items() if v >= cutoff}
    SEEN_FILE.parent.mkdir(parents=True, exist_ok=True)
    SEEN_FILE.write_text(
        json.dumps(seen, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )


def post_key(post: dict) -> str:
    """Ссылка на пост, а если её нет — отпечаток текста."""
    link = post["link"]
    if link:
        m = re.search(r"/(?:posts|permalink)/(\d+)", link) or re.search(
            r"(?:story_fbid|multi_permalinks)=(\d+)", link
        )
        if m:
            return "fb:" + m.group(1)
    return "fbtext:" + _text_fingerprint(post["text"])


def _text_fingerprint(text: str) -> str:
    # Без шапки «Автор 2 дн. ·»: один пост в разных группах имеет разную шапку.
    head, sep, body = text.partition("·")
    if sep and len(head) < 200:
        text = body
    text = re.sub(r"\s+", " ", text.lower()).strip()[:300]
    return hashlib.sha1(text.encode("utf-8")).hexdigest()[:16]


def post_age_days(header: str):
    """Возраст поста по шапке («9 сентябрь», «3 дн.»); None — не понять
    (например «5 ч.» или «вчера» — такие посты свежие)."""
    m = _DATE_RE.search(header)
    if m:
        month_word = m.group(2).lower()
        month = next(v for k, v in _RU_MONTHS.items() if month_word.startswith(k))
        today = date.today()
        year = int(m.group(3)) if m.group(3) else today.year
        try:
            posted = date(year, month, int(m.group(1)))
        except ValueError:
            return None
        if posted > today:  # «20 декабрь» в январе — прошлый год
            posted = posted.replace(year=year - 1)
        return (today - posted).days
    m = _DAYS_AGO_RE.search(header)
    if m:
        days = int(m.group(1))
        return days * 7 if "нед" in m.group(0).lower() else days
    return None


def clean_link(link: str) -> str:
    return link.split("?")[0] if link else link


def is_design_vacancy(text: str) -> bool:
    if _contains_keyword(text, SEEKER_KEYWORDS):
        return False
    if _contains_keyword(text, EXCLUDE_KEYWORDS + JUNIOR_KEYWORDS):
        return False
    return _contains_keyword(text, DESIGN_KEYWORDS) and _contains_keyword(
        text, HIRING_KEYWORDS
    )


def _pause(low: float = 2.0, high: float = 5.0) -> None:
    # Человеческий темп, чтобы не нагружать Facebook.
    time.sleep(random.uniform(low, high))


def _open_browser(p):
    return p.chromium.launch_persistent_context(
        str(PROFILE_DIR),
        executable_path=_find_chrome(),
        headless=False,
        no_viewport=True,
        args=["--start-maximized"],
    )


def _is_logged_out(page) -> bool:
    return "login" in page.url or page.locator(
        'input[name="email"], input[name="pass"]'
    ).count() > 0


def _chronological(url: str) -> str:
    url = url.split("?")[0].rstrip("/")
    return url + "/?sorting_setting=CHRONOLOGICAL"


def scan_group(page, url: str) -> tuple:
    try:
        page.goto(_chronological(url), wait_until="domcontentloaded", timeout=60000)
    except Exception:  # Facebook иногда долго отвечает — вторая попытка
        _pause(10, 15)
        page.goto(_chronological(url), wait_until="domcontentloaded", timeout=90000)
    _pause(4, 7)
    if _is_logged_out(page):
        raise PermissionError("Facebook просит войти в аккаунт.")

    name = re.sub(r"^\(\d+\)\s*", "", page.title()).split("|")[0].strip()

    found = {}
    for _ in range(SCROLLS_PER_GROUP):
        if page.evaluate(EXPAND_JS):
            _pause(0.8, 1.5)
        for post in page.evaluate(EXTRACT_POSTS_JS):
            key = post_key(post)
            # Раскрытый («Ещё») вариант поста длиннее — берём его.
            if len(post["text"]) > len(found.get(key, {}).get("text", "")):
                found[key] = post
        page.mouse.wheel(0, random.randint(500, 750))
        _pause(1.2, 2.5)

    return name or url, found


def is_nearby(text: str) -> bool:
    return _contains_keyword(text, ALLOWED_LOCATION_KEYWORDS + ["jlm"])


def build_messages(results: list) -> list:
    """Сначала посты с Иерусалимом и окрестностями, затем остальные."""
    nearby = [(name, url, post) for name, url, posts in results
              for post in posts if is_nearby(post["text"])]
    other = [(name, url, post) for name, url, posts in results
             for post in posts if not is_nearby(post["text"])]
    total = len(nearby) + len(other)
    if not total:
        return []

    sections = [
        ("🟢 <b>ИЕРУСАЛИМ И ОКРЕСТНОСТИ</b>", nearby),
        ("🟡 <b>ГОРОД НЕ УКАЗАН ИЛИ ДРУГОЙ</b>", other),
    ]
    chunks = []
    current = f"👥 <b>FACEBOOK-ГРУППЫ: новые вакансии — {total}</b>\n\n"
    index = 0
    for heading, posts in sections:
        if not posts:
            continue
        current += heading + "\n\n"
        for name, url, post in posts:
            index += 1
            snippet = re.sub(r"\s+", " ", post["text"]).strip()
            if len(snippet) > 400:
                snippet = snippet[:400] + "…"
            link = post["link"] or url
            link_text = "Открыть пост" if post["link"] else "Открыть группу"
            entry = (
                f"<b>{index}.</b> {escape(snippet)}\n"
                + (f"👤 {escape(post['author'])}\n" if post["author"] else "")
                + f"👥 {escape(name)}\n"
                + f"🔗 <a href=\"{escape(link)}\">{link_text}</a>"
            )
            if len(current) + len(entry) + 2 > MAX_MESSAGE_LENGTH:
                chunks.append(current.strip())
                current = ""
            current += entry + "\n\n"
    if current.strip():
        chunks.append(current.strip())
    return chunks


def login() -> None:
    with sync_playwright() as p:
        context = _open_browser(p)
        page = context.pages[0] if context.pages else context.new_page()
        page.goto("https://www.facebook.com/")
        print("Войдите в Facebook в открывшемся окне, затем закройте окно.")
        try:
            page.wait_for_event("close", timeout=0)
        except Exception:
            pass
        try:
            context.close()
        except Exception:
            pass


def run(dry_run: bool) -> None:
    groups = load_groups()
    if not groups:
        print(f"Нет групп. Добавьте ссылки в {GROUPS_FILE.name}.")
        return

    seen = load_seen()
    today = date.today().isoformat()
    results = []
    errors = []
    sent_texts = set()

    with sync_playwright() as p:
        context = _open_browser(p)
        page = context.pages[0] if context.pages else context.new_page()
        try:
            for url in groups:
                try:
                    name, posts = scan_group(page, url)
                except PermissionError:
                    msg = (
                        "⚠️ Помощник Facebook: нужно заново войти в Facebook. "
                        "Запустите: python facebook_agent.py --login"
                    )
                    print(msg)
                    if not dry_run:
                        send_message(msg)
                    return
                except Exception as exc:  # одна группа не должна ломать остальные
                    errors.append(f"{url}: {exc}")
                    continue

                new = []
                for key, post in posts.items():
                    if key in seen or not is_design_vacancy(post["text"]):
                        continue
                    age = post_age_days(post.get("header", ""))
                    if age is not None and age > MAX_POST_AGE_DAYS:
                        continue
                    # Один пост часто публикуют в нескольких группах.
                    fingerprint = _text_fingerprint(post["text"])
                    if fingerprint in sent_texts:
                        continue
                    sent_texts.add(fingerprint)
                    post["link"] = clean_link(post["link"])
                    new.append(post)
                print(f"{name}: постов {len(posts)}, новых вакансий {len(new)}")
                results.append((name, url, new))
                for key in posts:
                    seen.setdefault(key, today)
                _pause(5, 10)
        finally:
            context.close()

    for err in errors:
        print("Ошибка:", err)

    messages = build_messages(results)
    if dry_run:
        print("\n\n".join(messages) or "Новых вакансий нет.")
        return

    for message in messages:
        send_message(message)
    # Запоминаем просмотренные посты только после успешной отправки.
    save_seen(seen)


if __name__ == "__main__":
    if "--login" in sys.argv:
        login()
    else:
        run(dry_run="--dry-run" in sys.argv)
