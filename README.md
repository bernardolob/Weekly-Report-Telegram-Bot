# Weekly Report Telegram Bot

A Telegram bot that automates the weekly report workflow for a group: it sends reminders to fill in a Google Form, posts the compiled weekly report, and tracks who's responsible for the TWIL ("Today/This Week I Learned") segment — all pulled live from a Google Sheet.

## Features

- **`/startwr`** — schedules the weekly cycle of reminders and reports for a chat
- **`/stopwr`** — cancels the scheduled jobs for a chat
- **`/sendnow`** — sends the weekly report immediately, on demand
- **`/twilresponsible`** — shows who's responsible for TWIL this week
- **`/listtwil`** — lists upcoming TWIL responsibles
- **`/help`** — lists all available commands
- Automatic **first warning**, **second warning**, and **weekly report** messages, sent and pinned on a schedule
- Access restricted to a whitelist of chat IDs
- Data (report content, TWIL responsible, TWIL order) is read live from a Google Sheet via a service account

## Tech stack

- Python 3
- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) — Telegram Bot API wrapper and job scheduling
- [gspread](https://github.com/burnash/gspread) + `google-auth` — read access to Google Sheets
- [python-dotenv](https://github.com/theskumar/python-dotenv) — environment variable management

## Project structure

```
telegram-bot/
├── main.py            # Long-running bot: handles commands + scheduled jobs
├── wr.py               # One-shot script: sends & pins the weekly report
├── warning1.py          # One-shot script: sends the first warning message
├── sheetsReader.py       # Google Sheets integration (cached reads)
├── timeStructure.py       # Helper for scheduling times/days
├── .env.example           # Template for required environment variables
├── .gitignore
└── secrets/                # Service account JSON goes here (gitignored)
```

## Setup

### 1. Clone and install dependencies

```bash
git clone <this-repo-url>
cd telegram-bot
python -m venv .venv
source .venv/bin/activate  # on Windows: .venv\Scripts\activate
pip install python-telegram-bot gspread google-auth python-dotenv
```

### 2. Create a Telegram bot

- Talk to [@BotFather](https://t.me/BotFather) on Telegram, run `/newbot`, and copy the token it gives you.

### 3. Set up the Google service account

- Create a service account in [Google Cloud Console](https://console.cloud.google.com/) with access to the Sheets and Drive APIs.
- Download its JSON key and place it somewhere **outside version control**, e.g. `secrets/service-account.json`.
- Open your Google Sheet and **share it** with the service account's `client_email` (found inside the JSON file), giving it at least Viewer/Editor access.

### 4. Configure environment variables

Copy the example file and fill in your real values:

```bash
cp .env.example .env
```

```env
TELEGRAM_TOKEN=your-telegram-bot-token
GOOGLE_APPLICATION_CREDENTIALS=secrets/service-account.json
BOT_USERNAME=@your_bot_username
TELEGRAM_WHITELIST=-1001234567890,-1009876543210
FORMS_LINK=https://forms.gle/your-form-id
```

`.env` is gitignored and should **never** be committed, along with anything in `secrets/`.

### 5. Run it

For the long-running bot (handles commands and auto-scheduling):

```bash
python main.py
```

For one-shot scripts (useful for cron jobs or manual triggers):

```bash
python warning1.py   # sends the first warning message
python wr.py          # sends and pins the weekly report
```

## Notes

- Logs are written to `logs/telegrambot.log`.
- Only chat IDs listed in `TELEGRAM_WHITELIST` can use the bot's commands.
- This bot expects specific cell/column layouts in the connected Google Sheet (see `sheetsReader.py`); adapt those references if you use it with a different sheet structure.