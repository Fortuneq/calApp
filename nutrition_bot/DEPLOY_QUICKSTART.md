# Быстрый деплой на VPS - Шпаргалка

## 🚀 Вариант 1: Автоматический деплой (рекомендуется)

### На локальной машине:

```bash
# 1. Загрузите проект на VPS
cd /Users/volkovvladislav/PycharmProjects/calApp
rsync -avz --exclude 'venv' --exclude '__pycache__' --exclude '*.pyc' --exclude 'logs' nutrition_bot/ root@YOUR_VPS_IP:/opt/nutrition_bot/
```

### На VPS:

```bash
# 2. Подключитесь к VPS
ssh root@YOUR_VPS_IP

# 3. Перейдите в директорию
cd /opt/nutrition_bot

# 4. Запустите автоматический деплой
chmod +x DEPLOY_COMMANDS.sh
./DEPLOY_COMMANDS.sh
```

**Время: ~5 минут**

---

## ⚡ Вариант 2: Ручной деплой (пошагово)

### Подготовка на локальной машине:

```bash
# Создайте архив проекта
cd /Users/volkovvladislav/PycharmProjects/calApp
tar -czf nutrition_bot.tar.gz nutrition_bot/

# Загрузите на VPS
scp nutrition_bot.tar.gz root@YOUR_VPS_IP:/root/
```

### На VPS выполните команды:

```bash
# 1. Подключитесь к VPS
ssh root@YOUR_VPS_IP

# 2. Установите Docker и Docker Compose
curl -fsSL https://get.docker.com | sh
curl -L "https://github.com/docker/compose/releases/download/v2.24.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# 3. Распакуйте проект
cd /root
tar -xzf nutrition_bot.tar.gz
mv nutrition_bot /opt/
cd /opt/nutrition_bot

# 4. Создайте .env файл
nano .env
```

Вставьте в `.env`:
```env
TELEGRAM_BOT_TOKEN=***REMOVED***
OPENAI_API_KEY=***REMOVED***
DATABASE_URL=postgresql://nutrition_user:nutrition_password@db:5432/nutrition_bot
DB_USER=nutrition_user
DB_PASSWORD=nutrition_password
DB_NAME=nutrition_bot
TIMEZONE=Europe/Moscow
DIGEST_TIME=21:00
USER_CHAT_ID=***REMOVED***
LOG_LEVEL=INFO
```

**⚠️ ВАЖНО: Замените `nutrition_password` на надежный пароль!**

```bash
# 5. Запустите Docker Compose
docker-compose build
docker-compose up -d

# 6. Проверьте статус
docker-compose ps
docker-compose logs -f bot
```

**Время: ~10 минут**

---

## 📦 Вариант 3: Через rsync (самый быстрый)

### На локальной машине (одна команда):

```bash
# Загрузка проекта и автоматический деплой
cd /Users/volkovvladislav/PycharmProjects/calApp && \
rsync -avz --exclude 'venv' --exclude '__pycache__' nutrition_bot/ root@YOUR_VPS_IP:/opt/nutrition_bot/ && \
ssh root@YOUR_VPS_IP "cd /opt/nutrition_bot && curl -fsSL https://get.docker.com | sh && curl -L 'https://github.com/docker/compose/releases/download/v2.24.0/docker-compose-$(uname -s)-$(uname -m)' -o /usr/local/bin/docker-compose && chmod +x /usr/local/bin/docker-compose && docker-compose build && docker-compose up -d"
```

**⚠️ Не забудьте создать .env на VPS перед запуском!**

**Время: ~3 минуты**

---

## 🔧 Управление ботом

```bash
# Перейти в директорию проекта
cd /opt/nutrition_bot

# Просмотр логов в реальном времени
docker-compose logs -f bot

# Проверка статуса
docker-compose ps

# Перезапуск
docker-compose restart

# Остановка
docker-compose stop

# Запуск
docker-compose start

# Полный перезапуск с пересборкой
docker-compose down && docker-compose build && docker-compose up -d
```

---

## 🩺 Проверка работоспособности

```bash
# 1. Проверьте контейнеры
docker-compose ps
# Оба контейнера должны быть "Up"

# 2. Проверьте логи бота
docker-compose logs bot | tail -30
# Должно быть: "Starting bot polling..."

# 3. Проверьте базу данных
docker-compose exec db psql -U nutrition_user -d nutrition_bot -c "\dt"
# Должны быть 4 таблицы: meals, meals_draft, digest, chat_logs

# 4. Проверьте бота в Telegram
# Отправьте /start - бот должен ответить
```

---

## 💾 Бэкап базы данных

```bash
# Создать бэкап
docker-compose exec -T db pg_dump -U nutrition_user nutrition_bot | gzip > backup_$(date +%Y%m%d).sql.gz

# Восстановить из бэкапа
gunzip -c backup_20240115.sql.gz | docker-compose exec -T db psql -U nutrition_user nutrition_bot
```

---

## 🔄 Обновление бота

```bash
cd /opt/nutrition_bot

# Остановить
docker-compose down

# Обновить код (загрузите новые файлы через rsync или git pull)

# Пересобрать и запустить
docker-compose build
docker-compose up -d

# Проверить логи
docker-compose logs -f bot
```

---

## 🆘 Решение проблем

### Бот не отвечает:
```bash
docker-compose logs bot | grep -i error
docker-compose restart bot
```

### База данных не подключается:
```bash
docker-compose logs db
docker-compose restart db
```

### Нет места на диске:
```bash
df -h
docker system prune -a
```

### Проверить переменные окружения:
```bash
cat .env
docker-compose exec bot env | grep TELEGRAM
```

---

## 📊 Мониторинг

```bash
# Использование ресурсов
docker stats nutrition_bot nutrition_db

# Использование диска
du -sh /opt/nutrition_bot

# Системный мониторинг
htop
```

---

## 🔐 Безопасность

```bash
# Настройка файрвола
sudo ufw allow ssh
sudo ufw enable
sudo ufw status

# Смена пароля БД (если нужно)
# 1. Измените в .env
# 2. docker-compose down
# 3. docker volume rm nutrition_bot_pgdata
# 4. docker-compose up -d
```

---

## ✅ Чеклист после деплоя

- [ ] Docker и Docker Compose установлены
- [ ] Проект в `/opt/nutrition_bot`
- [ ] `.env` файл создан с реальными ключами
- [ ] `docker-compose ps` показывает оба контейнера "Up"
- [ ] Логи не показывают ошибок
- [ ] База данных создана (4 таблицы)
- [ ] Бот отвечает на `/start` в Telegram
- [ ] Тест фото работает
- [ ] Бэкап настроен (опционально)

---

## 📞 Полезные ссылки

- Полная инструкция: `VPS_DEPLOY.md`
- Документация: `README.md`
- Примеры: `EXAMPLES.md`
- Деплой чеклист: `DEPLOYMENT_CHECKLIST.md`

---

## 🎯 Самая быстрая установка (Copy-Paste)

**На локальной машине:**
```bash
cd /Users/volkovvladislav/PycharmProjects/calApp
rsync -avz --exclude 'venv' --exclude '__pycache__' nutrition_bot/ root@YOUR_VPS_IP:/opt/nutrition_bot/
```

**На VPS:**
```bash
ssh root@YOUR_VPS_IP
cd /opt/nutrition_bot
curl -fsSL https://get.docker.com | sh
curl -L "https://github.com/docker/compose/releases/download/v2.24.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose && chmod +x /usr/local/bin/docker-compose
nano .env  # Вставьте конфигурацию
docker-compose build && docker-compose up -d
docker-compose logs -f bot
```

**Время: 5 минут ⚡**

---

**IP вашего VPS:** `___________________`
**Дата деплоя:** `___________________`
**Статус:** ☐ Успешно  ☐ Требует проверки
