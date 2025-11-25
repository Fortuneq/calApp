# Deployment Checklist - Nutrition Bot

Complete checklist before deploying to production.

## Pre-Deployment Checklist

### 1. Configuration ✓
- [ ] Create `.env` file from `.env.example`
- [ ] Set `TELEGRAM_BOT_TOKEN` from @BotFather
- [ ] Set `OPENAI_API_KEY` from OpenAI Platform
- [ ] Set `DATABASE_URL` for PostgreSQL
- [ ] Set `USER_CHAT_ID` (your Telegram ID)
- [ ] Verify `TIMEZONE` is correct (default: Europe/Moscow)
- [ ] Verify `DIGEST_TIME` is correct (default: 21:00)
- [ ] Set `LOG_LEVEL` to INFO or WARNING for production

### 2. Database Setup ✓
- [ ] PostgreSQL 16+ installed
- [ ] Database `nutrition_bot` created
- [ ] Database user created (if not using postgres)
- [ ] Grant privileges to user
- [ ] Test connection: `psql -U user -d nutrition_bot -c "SELECT 1;"`
- [ ] Verify DATABASE_URL format: `postgresql://user:pass@host:port/dbname`

### 3. Dependencies ✓
- [ ] Python 3.11+ installed
- [ ] Virtual environment created
- [ ] All requirements installed: `pip install -r requirements.txt`
- [ ] No dependency conflicts: `pip check`
- [ ] OpenAI package version: 1.58.1+
- [ ] aiogram package version: 3.15.0+

### 4. API Access ✓
- [ ] Telegram bot token is valid
- [ ] Bot username is available
- [ ] OpenAI API key is valid
- [ ] OpenAI account has billing enabled
- [ ] OpenAI API quota is sufficient
- [ ] Test Vision API: uncomment test in `main.py`
- [ ] Test Chat API: uncomment test in `main.py`

### 5. File Structure ✓
```
✓ main.py
✓ config.py
✓ requirements.txt
✓ .env
✓ Dockerfile
✓ docker-compose.yml

✓ bot/
  ✓ handlers/
    ✓ start.py
    ✓ photo.py
    ✓ callbacks.py
    ✓ manual.py
    ✓ chat.py
  ✓ keyboards/
    ✓ inline.py

✓ database/
  ✓ models.py
  ✓ connection.py
  ✓ crud.py

✓ services/
  ✓ vision.py
  ✓ nutrition.py
  ✓ ai_chat.py
  ✓ digest.py

✓ scheduler/
  ✓ tasks.py

✓ utils/
  ✓ logger.py
  ✓ time.py
  ✓ parsers.py

✓ tests/
  ✓ test_parsers.py
```

### 6. Code Quality ✓
- [ ] All imports resolve correctly
- [ ] No syntax errors: `python -m py_compile **/*.py`
- [ ] Type hints present
- [ ] Docstrings present
- [ ] Logging configured
- [ ] Error handling in all handlers

### 7. Testing ✓
- [ ] Unit tests pass: `pytest tests/`
- [ ] Bot responds to `/start`
- [ ] Photo upload works
- [ ] Dish confirmation works
- [ ] Alternative selection works
- [ ] Weight selection works
- [ ] KBJU calculation works
- [ ] Meal save works
- [ ] Cancel button works
- [ ] Manual entry `/v` works
- [ ] AI chat responds
- [ ] Scheduler starts without errors

### 8. Security ✓
- [ ] `.env` file in `.gitignore`
- [ ] No secrets in code
- [ ] No secrets in logs
- [ ] Database password is strong
- [ ] OpenAI API key is secure
- [ ] Bot token is secure
- [ ] Input validation present
- [ ] SQL injection protection (ORM)

### 9. Logging ✓
- [ ] Logs directory exists
- [ ] Log rotation configured (10MB, 5 backups)
- [ ] Error logs separate (`error.log`)
- [ ] Log level appropriate for production
- [ ] No sensitive data in logs

### 10. Performance ✓
- [ ] Database indexes created
- [ ] Connection pooling enabled
- [ ] Async operations throughout
- [ ] No blocking calls
- [ ] Memory usage acceptable
- [ ] Response times < 5 seconds

---

## Deployment Methods

### Method 1: Local Development

```bash
# 1. Activate virtual environment
source venv/bin/activate

# 2. Run tests
pytest tests/ -v

# 3. Start bot
python main.py

# 4. Monitor logs
tail -f logs/bot.log
```

**Checklist:**
- [ ] Virtual environment activated
- [ ] Tests pass
- [ ] Bot starts without errors
- [ ] Database connection successful
- [ ] Scheduler starts
- [ ] Bot responds in Telegram

---

### Method 2: Docker Compose

```bash
# 1. Build images
docker-compose build

# 2. Start services
docker-compose up -d

# 3. Check status
docker-compose ps

# 4. View logs
docker-compose logs -f bot

# 5. Check database
docker-compose exec db psql -U nutrition_user -d nutrition_bot -c "SELECT COUNT(*) FROM meals;"
```

**Checklist:**
- [ ] Docker and Docker Compose installed
- [ ] `.env` file created
- [ ] Images build successfully
- [ ] Containers start
- [ ] Bot container running
- [ ] Database container running
- [ ] Network connectivity between containers
- [ ] Bot logs show no errors
- [ ] Database is accessible

---

### Method 3: Production Server (Systemd)

**1. Setup on Server**
```bash
# Clone repository
git clone <repo-url> /opt/nutrition_bot
cd /opt/nutrition_bot

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Create .env file
nano .env
# (paste configuration)

# Test run
python main.py
# (Ctrl+C to stop)
```

**2. Create Systemd Service**

File: `/etc/systemd/system/nutrition-bot.service`
```ini
[Unit]
Description=Telegram Nutrition Bot
After=network.target postgresql.service
Requires=postgresql.service

[Service]
Type=simple
User=botuser
Group=botuser
WorkingDirectory=/opt/nutrition_bot
Environment="PATH=/opt/nutrition_bot/venv/bin"
ExecStart=/opt/nutrition_bot/venv/bin/python main.py
Restart=always
RestartSec=10
StandardOutput=append:/var/log/nutrition-bot/stdout.log
StandardError=append:/var/log/nutrition-bot/stderr.log

[Install]
WantedBy=multi-user.target
```

**3. Enable and Start**
```bash
# Create log directory
sudo mkdir -p /var/log/nutrition-bot
sudo chown botuser:botuser /var/log/nutrition-bot

# Reload systemd
sudo systemctl daemon-reload

# Enable service (auto-start on boot)
sudo systemctl enable nutrition-bot

# Start service
sudo systemctl start nutrition-bot

# Check status
sudo systemctl status nutrition-bot

# View logs
sudo journalctl -u nutrition-bot -f
```

**Checklist:**
- [ ] Service file created
- [ ] Service enabled
- [ ] Service starts successfully
- [ ] Service restarts on failure
- [ ] Auto-starts on server reboot
- [ ] Logs are being written
- [ ] No errors in journal
- [ ] Bot responds in Telegram

---

## Post-Deployment Verification

### Functional Testing
```
✓ Test Sequence:

1. /start command
   Expected: Welcome message with instructions

2. Send food photo
   Expected: Recognition and confirmation

3. Confirm dish
   Expected: Weight selection

4. Select weight
   Expected: KBJU calculation and save

5. Click cancel button
   Expected: Meal deleted

6. /v яблоко 150
   Expected: Manual entry saved

7. Send text question
   Expected: AI consultant response

8. Wait until 21:00
   Expected: Daily digest arrives
```

### Performance Testing
- [ ] Photo processing < 5 seconds
- [ ] KBJU calculation < 3 seconds
- [ ] AI chat response < 5 seconds
- [ ] Database queries < 1 second
- [ ] No memory leaks after 24 hours

### Monitoring
- [ ] Logs are rotating
- [ ] No error spikes
- [ ] Database size is growing normally
- [ ] API calls within quota
- [ ] Bot uptime > 99%

---

## Rollback Plan

If deployment fails:

**1. Stop Service**
```bash
# Systemd
sudo systemctl stop nutrition-bot

# Docker
docker-compose down

# Manual
pkill -f "python main.py"
```

**2. Restore Database** (if needed)
```bash
psql -U nutrition_user nutrition_bot < backup.sql
```

**3. Revert Code** (if needed)
```bash
git checkout <previous-commit>
```

**4. Restart with Old Version**
```bash
# Systemd
sudo systemctl start nutrition-bot

# Docker
docker-compose up -d

# Manual
python main.py
```

---

## Monitoring Commands

### Check Bot Status
```bash
# Systemd
sudo systemctl status nutrition-bot

# Docker
docker-compose ps

# Process
ps aux | grep "python main.py"
```

### View Logs
```bash
# Application logs
tail -f logs/bot.log
tail -f logs/error.log

# Systemd logs
sudo journalctl -u nutrition-bot -f

# Docker logs
docker-compose logs -f bot
```

### Database Status
```bash
# Connect to database
psql -U nutrition_user nutrition_bot

# Check tables
\dt

# Count records
SELECT COUNT(*) FROM meals;
SELECT COUNT(*) FROM meals_draft;
SELECT COUNT(*) FROM digest;
SELECT COUNT(*) FROM chat_logs;

# Recent meals
SELECT dish, grams, kcal, eaten_at
FROM meals
WHERE deleted = false
ORDER BY eaten_at DESC
LIMIT 10;
```

### Resource Usage
```bash
# Memory usage
ps aux | grep python | awk '{print $6}'

# CPU usage
top -p $(pgrep -f "python main.py")

# Disk usage
df -h
du -sh /opt/nutrition_bot/logs
```

---

## Maintenance Schedule

### Daily
- [ ] Check bot is running
- [ ] Review error logs
- [ ] Verify digest was sent at 21:00

### Weekly
- [ ] Review API usage
- [ ] Check database size
- [ ] Backup database
- [ ] Review performance metrics

### Monthly
- [ ] Update dependencies: `pip list --outdated`
- [ ] Clean old logs: `find logs/ -mtime +30 -delete`
- [ ] Optimize database: `VACUUM ANALYZE;`
- [ ] Review and archive old data

### Quarterly
- [ ] Security audit
- [ ] Performance optimization
- [ ] Feature review
- [ ] User feedback review

---

## Troubleshooting

### Bot Not Responding
```bash
# 1. Check if running
systemctl status nutrition-bot

# 2. Check logs
tail -50 logs/error.log

# 3. Test Telegram API
curl https://api.telegram.org/bot<TOKEN>/getMe

# 4. Restart
systemctl restart nutrition-bot
```

### Database Issues
```bash
# 1. Check PostgreSQL
systemctl status postgresql

# 2. Test connection
psql -U nutrition_user -d nutrition_bot -c "SELECT 1;"

# 3. Check connections
SELECT count(*) FROM pg_stat_activity WHERE datname = 'nutrition_bot';

# 4. Restart PostgreSQL
systemctl restart postgresql
```

### High Memory Usage
```bash
# 1. Check memory
free -h

# 2. Check bot memory
ps aux | grep python

# 3. Restart bot
systemctl restart nutrition-bot

# 4. If persistent, check for memory leaks
```

### API Errors
```bash
# 1. Check OpenAI status
curl https://status.openai.com/api/v2/status.json

# 2. Verify API key
# Check OpenAI dashboard

# 3. Check rate limits
# Review API usage in OpenAI dashboard

# 4. Add retry logic if needed
```

---

## Success Criteria

Deployment is successful when:

- [x] Bot responds to all commands
- [x] Photo recognition works
- [x] Manual entry works
- [x] AI chat works
- [x] Daily digest sends at correct time
- [x] No errors in logs for 24 hours
- [x] Database is populated correctly
- [x] Service auto-restarts on failure
- [x] Service auto-starts on server reboot
- [x] All tests pass
- [x] Performance is acceptable
- [x] Resource usage is normal

---

## Contact & Support

**Issues:** Create GitHub issue
**Logs:** Include error.log and bot.log
**Questions:** Check SETUP_GUIDE.md

---

**Deployment Date:** ___________
**Deployed By:** ___________
**Version:** 1.0.0
**Status:** □ Success  □ Rollback  □ In Progress
