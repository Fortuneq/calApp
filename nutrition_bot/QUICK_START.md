# Quick Start Guide - Nutrition Bot

Get your Telegram Nutrition Bot running in 5 minutes!

## Prerequisites

✅ Python 3.11+
✅ PostgreSQL 16
✅ Telegram Bot Token
✅ OpenAI API Key

## 1. Install Dependencies

```bash
cd nutrition_bot
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## 2. Setup Database

```bash
# Create PostgreSQL database
createdb nutrition_bot
```

## 3. Configure Environment

Create `.env` file:

```env
TELEGRAM_BOT_TOKEN=your_bot_token_from_botfather
OPENAI_API_KEY=sk-your_openai_api_key
DATABASE_URL=postgresql://postgres:password@localhost:5432/nutrition_bot
USER_CHAT_ID=your_telegram_chat_id
```

**Get these values:**
- Bot Token: [@BotFather](https://t.me/botfather) → `/newbot`
- OpenAI Key: [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
- Chat ID: [@userinfobot](https://t.me/userinfobot)

## 4. Run the Bot

```bash
python main.py
```

You should see:
```
[INFO] Database initialized successfully
[INFO] Scheduler started - Daily digest at 21:00
[INFO] Starting bot polling...
```

## 5. Test in Telegram

1. Find your bot in Telegram
2. Send `/start`
3. Upload a food photo 📸
4. Or try: `/v яблоко 150`

## Docker Alternative

```bash
# 1. Create .env file (same as above)

# 2. Run with Docker
docker-compose up -d

# 3. Check logs
docker-compose logs -f bot
```

## Troubleshooting

**Bot not responding?**
```bash
# Check if running
ps aux | grep python

# Check logs
tail -f logs/bot.log
```

**Database error?**
```bash
# Check PostgreSQL
psql -U postgres -c "SELECT version();"
```

**API error?**
- Verify OpenAI key has billing enabled
- Check token is correct (no spaces)

## What's Next?

- Read full [README.md](README.md) for details
- Check [SETUP_GUIDE.md](SETUP_GUIDE.md) for troubleshooting
- Customize digest time in `.env`

## Usage Examples

**Photo Upload:**
- Take a photo of your food
- Bot recognizes dish
- Confirm or select alternative
- Choose weight
- Done! ✅

**Manual Entry:**
```
/v яблоко 150
/v греча 200 18:30
/v курица 180г
```

**AI Consultant:**
Just send any question:
- "Сколько калорий сегодня?"
- "Достаточно ли белка?"
- "Что посоветуешь на ужин?"

## Features

- 🤖 GPT-4 Vision for food recognition
- 📊 Automatic KBJU calculation
- 💬 AI nutrition consultant
- 📈 Daily digests at 21:00 MSK
- ⚡ Fast and easy to use

---

Need help? Check the full documentation or create an issue on GitHub.
