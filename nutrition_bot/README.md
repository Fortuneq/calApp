# Telegram Nutrition Tracking Bot

AI-powered Telegram bot for tracking nutrition with automatic food recognition via GPT-4 Vision, KBJU calculation, and daily digest generation.

## Features

- **Photo Recognition**: Upload food photos for automatic dish identification using GPT-4 Vision
- **KBJU Calculation**: Automatic calculation of calories, protein, fat, and carbs via GPT-4
- **Manual Entry**: Quick manual food entry with `/v dish grams [time]` command
- **AI Consultant**: Ask nutrition questions and get personalized advice based on your eating history
- **Daily Digest**: Automatic daily nutrition summaries sent at 21:00 MSK
- **Smart FSM**: Interactive dialog for confirming dishes and adjusting portions

## Tech Stack

- **Python 3.11+**
- **aiogram 3.x** - Telegram Bot API framework
- **OpenAI API** - GPT-4o and GPT-4 Vision for AI features
- **PostgreSQL** - Database for storing meals and chat history
- **SQLAlchemy** - Async ORM
- **APScheduler** - Task scheduling for daily digests
- **Docker** - Containerization

## Installation

### Prerequisites

- Python 3.11 or higher
- PostgreSQL 16
- Telegram Bot Token (from [@BotFather](https://t.me/botfather))
- OpenAI API Key

### Local Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd nutrition_bot
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file from example:
```bash
cp .env.example .env
```

5. Configure `.env` with your credentials:
```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
OPENAI_API_KEY=your_openai_key_here
DATABASE_URL=postgresql://user:password@localhost:5432/nutrition_bot
USER_CHAT_ID=your_telegram_chat_id
```

6. Initialize database:
```bash
# Create PostgreSQL database
createdb nutrition_bot

# Run migrations (automatic on first start)
python main.py
```

### Docker Setup

1. Create `.env` file with your credentials

2. Build and run with Docker Compose:
```bash
docker-compose up -d
```

3. View logs:
```bash
docker-compose logs -f bot
```

4. Stop services:
```bash
docker-compose down
```

## Usage

### Commands

- `/start` - Welcome message and instructions
- `/v dish grams [time]` - Manual food entry
  - Example: `/v яблоко 150`
  - Example: `/v греча 200 18:30`

### Photo Upload

1. Send a photo of your food
2. Bot analyzes it with GPT-4 Vision
3. Confirm the dish or choose alternative
4. Select portion weight
5. Bot calculates KBJU and saves to database

### AI Consultant

Simply send any text message (not a command) to ask nutrition questions:
- "Сколько калорий я съел сегодня?"
- "Достаточно ли белка в моем рационе?"
- "Что мне посоветуешь на ужин?"

The bot has context of your last 7 days of meals.

### Daily Digest

Every day at 21:00 MSK, the bot automatically sends a digest with:
- Total KBJU for the day
- List of all meals
- AI-generated analysis and recommendations

## Project Structure

```
nutrition_bot/
├── main.py                 # Entry point
├── config.py              # Configuration
├── requirements.txt       # Dependencies
├── Dockerfile            # Docker image
├── docker-compose.yml    # Docker services
│
├── bot/
│   ├── handlers/         # Message handlers
│   │   ├── start.py      # /start command
│   │   ├── photo.py      # Photo processing
│   │   ├── manual.py     # Manual entry /v
│   │   ├── chat.py       # AI consultant
│   │   └── callbacks.py  # Inline button callbacks
│   │
│   └── keyboards/        # Telegram keyboards
│       └── inline.py     # Inline keyboards
│
├── services/
│   ├── vision.py         # GPT-4 Vision API
│   ├── nutrition.py      # KBJU calculation
│   ├── ai_chat.py        # AI consultant
│   └── digest.py         # Daily digest generation
│
├── database/
│   ├── models.py         # SQLAlchemy models
│   ├── connection.py     # Database connection
│   └── crud.py           # CRUD operations
│
├── scheduler/
│   └── tasks.py          # APScheduler tasks
│
└── utils/
    ├── logger.py         # Logging setup
    ├── time.py           # Time utilities (MSK)
    └── parsers.py        # Text parsers
```

## Database Schema

### Tables

- **meals** - All meal records with KBJU
- **meals_draft** - Temporary storage for FSM states
- **digest** - Daily nutrition summaries
- **chat_logs** - AI consultant conversation history

See `database/models.py` for full schema.

## Development

### Running Tests

```bash
pytest tests/
```

### Code Quality

```bash
# Format code
black .

# Lint
pylint nutrition_bot/

# Type checking
mypy nutrition_bot/
```

### Logging

Logs are stored in `logs/` directory:
- `bot.log` - All logs
- `error.log` - Errors only

## Configuration

Environment variables (`.env`):

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `TELEGRAM_BOT_TOKEN` | Yes | - | Bot token from @BotFather |
| `OPENAI_API_KEY` | Yes | - | OpenAI API key |
| `DATABASE_URL` | Yes | - | PostgreSQL connection URL |
| `USER_CHAT_ID` | Yes | - | Your Telegram chat ID |
| `TIMEZONE` | No | Europe/Moscow | Timezone for digests |
| `DIGEST_TIME` | No | 21:00 | Daily digest time |
| `LOG_LEVEL` | No | INFO | Logging level |

## Troubleshooting

### Bot not responding
- Check bot token is correct
- Verify bot is running: `docker-compose ps`
- Check logs: `docker-compose logs bot`

### Database connection error
- Ensure PostgreSQL is running
- Verify DATABASE_URL is correct
- Check database exists

### OpenAI API errors
- Verify API key is valid
- Check API quota/billing
- Review error logs

## License

MIT License - see LICENSE file

## Author

Developed with Claude Code

## Support

For issues and questions, please open an issue on GitHub.
