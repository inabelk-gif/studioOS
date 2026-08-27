# Job Search Agent

Ежедневно ищет вакансии, подходящие для Senior Graphic Designer, переходящего
в UI/UX и Product Design, в Иерусалиме и населённых пунктах в радиусе ~30 км
от него, и присылает отчёт в Telegram.

## Как это устроено

- `job_agent/sources/` — источники вакансий (сейчас: публичный поиск
  LinkedIn Jobs, без логина и без платного API). Легко добавить новый
  источник: см. `job_agent/sources/base.py`.
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

- Источник вакансий сейчас один — публичный (без логина) поиск LinkedIn
  Jobs через их "guest"-эндпоинт. Это не официальный документированный
  API: LinkedIn может изменить разметку страницы или временно
  ограничивать частые запросы. Если отчёты перестанут приходить —
  проверьте вначале `job_agent/sources/linkedin.py` (CSS-селекторы) и
  журнал запуска в GitHub Actions.
- Можно добавить другие источники (например, Drushim, AllJobs, Jooble).
  Часть из них требует бесплатной регистрации ради API-ключа — я не
  подключал их сам, так как это отдельный внешний сервис; скажите, если
  хотите, чтобы я добавил такой источник, и уточните, какой.
- Радиус "30 км от Иерусалима" реализован как список конкретных
  населённых пунктов в `ALLOWED_LOCATION_KEYWORDS` (`job_agent/config.py`)
  — при необходимости список легко расширить.
