# calApp — AI nutrition tracking bot

A Telegram bot for tracking nutrition. Send a photo of your meal and the bot recognises the dish, estimates the portion and calculates calories and macros (KBJU). It keeps a food diary, answers nutrition questions based on your eating history and sends a daily digest.

## Features

- **Photo recognition** — dish identification from a photo with GPT-4 Vision
- **Calories and macros** — automatic calculation of calories, protein, fat and carbs
- **Manual entry** — quick logging with `/v <dish> <grams> [time]`
- **AI consultant** — ask nutrition questions and get advice based on your history
- **Daily digest** — a nutrition summary sent automatically every evening (21:00 MSK)
- **Interactive confirmation** — FSM dialog to confirm dishes and adjust portions

## Tech stack

Python 3.11+, aiogram 3, OpenAI API (GPT-4o, GPT-4 Vision), PostgreSQL, SQLAlchemy (async), APScheduler, Docker.

## Project structure

```
nutrition_bot/
├── main.py              — entry point
├── config.py            — settings from environment
├── bot/handlers/        — start, photo, manual entry, AI chat, callbacks
├── services/            — vision, nutrition maths, AI chat, daily digest
├── database/            — models, connection, CRUD
├── scheduler/           — scheduled digest jobs
├── utils/               — parsers, time helpers, logging
└── tests/
```

## Getting started

```bash
cd nutrition_bot
cp .env.example .env     # Telegram bot token, OpenAI key, PostgreSQL URL
make docker-up           # bot + PostgreSQL in Docker
make logs
```

Without Docker:

```bash
make install
make run
make test
```

Detailed guides: [`nutrition_bot/README.md`](nutrition_bot/README.md), [`SETUP_GUIDE.md`](nutrition_bot/SETUP_GUIDE.md), [`VPS_DEPLOY.md`](nutrition_bot/VPS_DEPLOY.md).
