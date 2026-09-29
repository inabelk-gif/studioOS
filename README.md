# Job Search Agent

Ежедневно ищет вакансии, подходящие для Senior Graphic Designer, переходящего
в UI/UX и Product Design, в Иерусалиме и населённых пунктах в радиусе ~30 км
от него, и присылает отчёт в Telegram.

## Как это устроено

- `job_agent/sources/` — источники вакансий, все без логина и без
  платного API:
  - LinkedIn Jobs (радиус ~80 км от Иерусалима);
  - Drushim (drushim.co.il);
  - AllJobs (alljobs.co.il) — подписка AllJobs для поиска не нужна;
  - JobMaster (jobmaster.co.il);
  - раздел «Дизайн» Drushim в радиусе 30 км от Иерусалима и раздел
    Graphic design на Janglo (janglo.net) — эти страницы читаются один
    раз за запуск, см. `job_agent/sources/listings.py`.

  Drushim, AllJobs и JobMaster ищут по всему Израилю, поэтому из их
  результатов остаются только города из `ALLOWED_LOCATION_KEYWORDS` и
  `EXCLUDED_LOCATION_KEYWORDS` (`job_agent/config.py`). Одинаковые
  вакансии (то же название, компания и город) с разных сайтов
  присылаются один раз. Добавить новый источник: см.
  `job_agent/sources/base.py`.
- `job_agent/companies.py` — список отслеживаемых компаний Иерусалима
  (из таблицы «Компании по районам»). Для части компаний агент каждый
  день сам проверяет их сайт вакансий (Lever, Greenhouse, Workday или
  обычная страница «Карьера»); остальные узнаются по названию в
  вакансиях с LinkedIn/AllJobs/Drushim/JobMaster. Вакансии этих компаний
  идут в отчёте первым разделом «🏢 Компании из вашего списка».
  Чтобы добавить компанию — допишите строку `Company(...)` в этот файл.
- `job_agent/company_watch.py` — проверка сайтов компаний и
  распознавание компаний из списка.
- `job_agent/config.py` — список должностей для поиска (англ/иврит), список
  разрешённых локаций (Иерусалим + ~30 км), список ключевых навыков для
  объяснения "почему подходит".
- `job_agent/ranking.py` — оценка и сортировка найденных вакансий.
- `job_agent/dedup.py` — хранит `data/sent_vacancies.json` со списком уже
  отправленных вакансий, чтобы не присылать одно и то же дважды.
- `job_agent/telegram_notifier.py` — отправка отчёта в Telegram.
- `job_agent/main.py` — точка входа, весь цикл целиком.
- `.github/workflows/daily-job-search.yml` — ежедневный автозапуск через
  GitHub Actions (бесплатно, без сервера).

Никаких платных API и сервисов не используется.

## Настройка Telegram (обязательно)

1. Создайте бота через [@BotFather](https://t.me/BotFather): команда
   `/newbot`, следуйте инструкциям — вы получите `TELEGRAM_BOT_TOKEN`
   (строка вида `123456789:AAExampleTokenValue`).
2. Узнайте свой `TELEGRAM_CHAT_ID`:
   - напишите вашему новому боту любое сообщение,
   - откройте в браузере
     `https://api.telegram.org/bot<ВАШ_ТОКЕН>/getUpdates`,
   - найдите в ответе `"chat":{"id": ЧИСЛО, ...}` — это и есть chat id
     (можно также воспользоваться ботом [@userinfobot](https://t.me/userinfobot)
     — он сразу пришлёт ваш id).

Токен и chat id **никогда не хранятся в коде**, только в переменных
окружения `TELEGRAM_BOT_TOKEN` и `TELEGRAM_CHAT_ID`.

### Локальный запуск

```bash
cp .env.example .env
```

Откройте `.env` и впишите значения:

```
TELEGRAM_BOT_TOKEN=123456789:AAExampleTokenValue
TELEGRAM_CHAT_ID=123456789
```

Затем:

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m job_agent.main
```

### Автоматический ежедневный запуск (GitHub Actions)

1. В репозитории на GitHub: **Settings → Secrets and variables → Actions →
   New repository secret**. Добавьте два секрета:
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_CHAT_ID`
2. Важно: запланированные (`schedule`) workflow в GitHub Actions
   запускаются только для **default branch** репозитория. Если сейчас
   default branch другой — смержите эту ветку в default branch (или
   назначьте текущую ветку default branch) в Settings → Branches.
3. Готово — workflow `.github/workflows/daily-job-search.yml` будет
   запускаться каждый день (06:00 UTC) и присылать отчёт в Telegram. Можно
   также запустить вручную: вкладка **Actions → Daily job search → Run
   workflow**.

## Формат отчёта

```
1. Job title — Company
📍 Location
⭐ Почему подходит: ...
🔗 Ссылка на вакансию
```

Если новых подходящих вакансий нет — присылается сообщение "Сегодня новых
подходящих вакансий не найдено."

## Ограничения и что можно улучшить

- Все источники читают обычные публичные страницы поиска, а не
  официальные API: сайт может изменить разметку или временно
  ограничивать частые запросы. Сломанный источник не останавливает
  остальные. В журнале запуска GitHub Actions для каждого сайта есть
  строка вида `AllJobs: 24 relevant vacancies` — если у какого-то сайта
  там постоянно 0 или `fetch failed`, проверьте его файл в
  `job_agent/sources/`.
- Радиус "30 км от Иерусалима" реализован как список конкретных
  населённых пунктов в `ALLOWED_LOCATION_KEYWORDS` (`job_agent/config.py`)
  — при необходимости список легко расширить.

## Помощник для групп Facebook (запускается на компьютере)

`facebook_agent.py` открывает Google Chrome с отдельным профилем
(`chrome_fb_profile/`, в git не попадает), просматривает свежие посты
групп из `facebook_groups.txt` и присылает в тот же Telegram-бот посты,
где ищут дизайнера. Уже присланные посты помнятся в
`data/facebook_seen.json` (тоже только на компьютере).

1. Один раз войти в Facebook: `python facebook_agent.py --login`,
   войти в открывшемся окне и закрыть его.
2. Добавить ссылки на группы в `facebook_groups.txt`.
3. Проверка без отправки: `python facebook_agent.py --dry-run`.
4. Обычный запуск: `python facebook_agent.py` (нужен файл `.env`
   с `TELEGRAM_BOT_TOKEN` и `TELEGRAM_CHAT_ID`, см. `.env.example`).
5. Ежедневный запуск: задача «Facebook job helper» в Планировщике
   заданий Windows (каждый день в 10:00, если компьютер был выключен —
   при следующем включении) запускает `run_facebook_agent.bat`.
   Журнал запусков — `data/facebook_agent.log`.
