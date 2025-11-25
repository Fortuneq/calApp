# Nutrition Bot - Setup Guide

Complete step-by-step guide for setting up and running the Telegram Nutrition Bot.

## Prerequisites

Before you begin, ensure you have:

1. **Python 3.11+** installed
2. **PostgreSQL 16** installed and running
3. **Telegram Bot Token** from [@BotFather](https://t.me/botfather)
4. **OpenAI API Key** from [OpenAI Platform](https://platform.openai.com)
5. **Your Telegram Chat ID** (get it from [@userinfobot](https://t.me/userinfobot))

## Step 1: Get Telegram Bot Token

1. Open Telegram and find [@BotFather](https://t.me/botfather)
2. Send `/newbot` command
3. Follow the instructions:
   - Choose a name for your bot (e.g., "My Nutrition Bot")
   - Choose a username (must end in "bot", e.g., "mynutrition_bot")
4. Save the token (looks like `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`)

## Step 2: Get OpenAI API Key

1. Go to [OpenAI Platform](https://platform.openai.com)
2. Sign up or log in
3. Navigate to API Keys section
4. Click "Create new secret key"
5. Save the key (starts with `sk-...`)
6. **Important**: Add billing information to avoid rate limits

## Step 3: Get Your Telegram Chat ID

1. Open Telegram and find [@userinfobot](https://t.me/userinfobot)
2. Start the bot
3. It will send you your chat ID (a number like `***REMOVED***`)
4. Save this ID

## Step 4: Install PostgreSQL

### macOS (using Homebrew)
```bash
brew install postgresql@16
brew services start postgresql@16
```

### Ubuntu/Debian
```bash
sudo apt update
sudo apt install postgresql-16
sudo systemctl start postgresql
```

### Windows
Download and install from [PostgreSQL Downloads](https://www.postgresql.org/download/windows/)

### Create Database
```bash
# Connect to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE nutrition_bot;

# Create user (optional)
CREATE USER nutrition_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE nutrition_bot TO nutrition_user;

# Exit
\q
```

## Step 5: Clone and Setup Project

```bash
# Clone repository (or download ZIP)
git clone <repository-url>
cd nutrition_bot

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Step 6: Configure Environment

Create `.env` file in project root:

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```env
# Telegram Bot Token from @BotFather
TELEGRAM_BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11

# OpenAI API Key
OPENAI_API_KEY=sk-...your_key_here...

# Database URL
# Format: postgresql://user:password@host:port/database
DATABASE_URL=postgresql://nutrition_user:your_password@localhost:5432/nutrition_bot

# Your Telegram Chat ID (from @userinfobot)
USER_CHAT_ID=***REMOVED***

# Timezone (default: Europe/Moscow)
TIMEZONE=Europe/Moscow

# Daily digest time (default: 21:00)
DIGEST_TIME=21:00

# Logging level (DEBUG, INFO, WARNING, ERROR)
LOG_LEVEL=INFO
```

## Step 7: Run the Bot

### Local Development

```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Run the bot
python main.py
```

You should see:
```
[2024-01-15 10:30:00] INFO - Logger initialized (level: INFO)
[2024-01-15 10:30:00] INFO - Database initialized successfully
[2024-01-15 10:30:00] INFO - All handlers registered successfully
[2024-01-15 10:30:00] INFO - Scheduler started - Daily digest at 21:00 Europe/Moscow
[2024-01-15 10:30:00] INFO - Starting bot polling...
```

### Using Docker

```bash
# Build and start services
docker-compose up -d

# View logs
docker-compose logs -f bot

# Stop services
docker-compose down
```

## Step 8: Test the Bot

1. **Open Telegram** and find your bot by username
2. **Send `/start`** - You should get a welcome message
3. **Send a photo of food** - Bot should analyze it
4. **Try manual entry**: `/v яблоко 150`
5. **Ask a question**: "Сколько калорий я съел?"

## Common Issues

### Issue: "Database connection error"
**Solution**: Check PostgreSQL is running:
```bash
# macOS/Linux
ps aux | grep postgres

# Check service
brew services list  # macOS
sudo systemctl status postgresql  # Linux
```

### Issue: "Invalid bot token"
**Solution**:
- Verify token in `.env` is correct
- Make sure no extra spaces
- Token should be one line

### Issue: "OpenAI API rate limit"
**Solution**:
- Add billing information in OpenAI account
- Check API quota: https://platform.openai.com/usage
- Wait if rate limited (usually resets hourly)

### Issue: "Bot not responding to messages"
**Solution**:
- Check bot is running: `ps aux | grep python`
- Check logs in `logs/bot.log`
- Verify USER_CHAT_ID matches your Telegram ID
- Make sure no other instance is running

### Issue: "Import errors"
**Solution**:
```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt

# Check Python version
python --version  # Should be 3.11+
```

## Verification Checklist

- [ ] PostgreSQL is running
- [ ] Database `nutrition_bot` exists
- [ ] `.env` file has all required variables
- [ ] Virtual environment is activated
- [ ] All dependencies installed
- [ ] Bot responds to `/start` command
- [ ] Photo recognition works
- [ ] Manual entry works
- [ ] AI consultant responds
- [ ] No errors in logs

## Next Steps

1. **Customize digest time**: Change `DIGEST_TIME` in `.env`
2. **Add more users**: Modify code to support multiple users
3. **Setup monitoring**: Add logging tools like Sentry
4. **Deploy to server**: Use VPS with Docker
5. **Add features**: Extend functionality as needed

## Getting Help

If you encounter issues:

1. Check `logs/bot.log` for errors
2. Run with DEBUG level: `LOG_LEVEL=DEBUG` in `.env`
3. Test API connections:
   - Uncomment API tests in `main.py` `on_startup()`
4. Create GitHub issue with:
   - Error message
   - Steps to reproduce
   - Log output

## Deployment to Production

### Using Systemd (Linux)

Create `/etc/systemd/system/nutrition-bot.service`:

```ini
[Unit]
Description=Telegram Nutrition Bot
After=network.target postgresql.service

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/nutrition_bot
Environment="PATH=/path/to/nutrition_bot/venv/bin"
ExecStart=/path/to/nutrition_bot/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable nutrition-bot
sudo systemctl start nutrition-bot
sudo systemctl status nutrition-bot
```

### Using Docker in Production

```bash
# Build image
docker-compose build

# Start in detached mode
docker-compose up -d

# Auto-restart on server reboot
docker update --restart unless-stopped nutrition_bot
```

## Backup and Maintenance

### Database Backup
```bash
# Backup
pg_dump -U nutrition_user nutrition_bot > backup.sql

# Restore
psql -U nutrition_user nutrition_bot < backup.sql
```

### Log Rotation
Logs are automatically rotated (10MB max, 5 backups).

### Updates
```bash
# Pull latest code
git pull

# Update dependencies
pip install --upgrade -r requirements.txt

# Restart bot
sudo systemctl restart nutrition-bot  # systemd
docker-compose restart bot  # docker
```

## Security Best Practices

1. **Never commit `.env` file** to Git
2. **Use strong database passwords**
3. **Keep API keys secret**
4. **Regularly update dependencies**:
   ```bash
   pip list --outdated
   pip install --upgrade <package>
   ```
5. **Monitor logs** for suspicious activity
6. **Backup database** regularly

## Performance Tips

1. **Use Redis** for caching (optional):
   - Add Redis to docker-compose.yml
   - Cache frequent queries

2. **Database indexes** are already optimized
3. **Connection pooling** is enabled by default
4. **Log level** in production should be INFO or WARNING

---

Congratulations! Your Nutrition Bot should now be up and running. Enjoy tracking your nutrition with AI! 🍎🤖
