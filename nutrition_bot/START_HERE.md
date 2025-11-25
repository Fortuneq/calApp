# 🚀 НАЧНИТЕ ОТСЮДА - Деплой на VPS

## Что нужно сделать (3 шага):

### 1️⃣ Загрузите проект на VPS

**На вашем компьютере:**
```bash
cd /Users/volkovvladislav/PycharmProjects/calApp
rsync -avz --exclude 'venv' --exclude '__pycache__' nutrition_bot/ root@YOUR_VPS_IP:/opt/nutrition_bot/
```

*Замените `YOUR_VPS_IP` на реальный IP вашего VPS*

---

### 2️⃣ Подключитесь к VPS и запустите

**На VPS:**
```bash
ssh root@YOUR_VPS_IP
cd /opt/nutrition_bot
./DEPLOY_COMMANDS.sh
```

Скрипт автоматически:
- ✅ Установит Docker и Docker Compose
- ✅ Создаст базу данных PostgreSQL
- ✅ Соберет и запустит бота
- ✅ Настроит автозапуск
- ✅ Настроит автоматические бэкапы

**Время: ~5 минут**

---

### 3️⃣ Проверьте работу бота

1. Откройте Telegram
2. Найдите своего бота по username
3. Отправьте `/start`
4. Попробуйте отправить фото еды

✅ **Готово!**

---

## ⚙️ Альтернатива: Ручной деплой

Если автоматический скрипт не работает, следуйте пошаговой инструкции:

### Шаг 1: Установите Docker

```bash
ssh root@YOUR_VPS_IP
curl -fsSL https://get.docker.com | sh
curl -L "https://github.com/docker/compose/releases/download/v2.24.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
```

### Шаг 2: Перейдите в директорию проекта

```bash
cd /opt/nutrition_bot
```

### Шаг 3: Проверьте .env файл

```bash
cat .env
```

Убедитесь, что все переменные заполнены:
- `TELEGRAM_BOT_TOKEN` - ваш токен от BotFather
- `OPENAI_API_KEY` - ваш ключ OpenAI
- `USER_CHAT_ID` - ваш Telegram ID

**⚠️ ВАЖНО:** Смените пароль БД в `.env`:
```bash
nano .env
# Найдите DB_PASSWORD и замените на надежный пароль
```

### Шаг 4: Запустите бота

```bash
docker-compose build
docker-compose up -d
```

### Шаг 5: Проверьте статус

```bash
docker-compose ps
docker-compose logs -f bot
```

Вы должны увидеть:
```
[INFO] Database initialized successfully
[INFO] Starting bot polling...
```

---

## 📚 Документация

После успешного деплоя ознакомьтесь с документацией:

| Файл | Описание |
|------|----------|
| [DEPLOY_QUICKSTART.md](DEPLOY_QUICKSTART.md) | Шпаргалка с командами |
| [VPS_DEPLOY.md](VPS_DEPLOY.md) | Подробная инструкция |
| [README.md](README.md) | Общая документация |
| [EXAMPLES.md](EXAMPLES.md) | Примеры использования |

---

## 🔧 Полезные команды

```bash
# Просмотр логов
docker-compose logs -f bot

# Перезапуск
docker-compose restart

# Остановка
docker-compose stop

# Статус
docker-compose ps

# Бэкап БД
./backup.sh

# Проверка здоровья
./health_check.sh
```

---

## 🆘 Что-то пошло не так?

### Проблема: Скрипт не запускается
```bash
chmod +x DEPLOY_COMMANDS.sh
./DEPLOY_COMMANDS.sh
```

### Проблема: Бот не отвечает
```bash
docker-compose logs bot | tail -50
docker-compose restart bot
```

### Проблема: Ошибка подключения к БД
```bash
docker-compose logs db
docker-compose restart db
```

### Проблема: "Permission denied"
```bash
# Запустите от root
sudo su
cd /opt/nutrition_bot
./DEPLOY_COMMANDS.sh
```

---

## ✅ Контрольный список

После деплоя убедитесь:

- [ ] Контейнеры запущены: `docker-compose ps`
- [ ] Логи без ошибок: `docker-compose logs bot`
- [ ] База данных работает: `docker-compose exec db psql -U nutrition_user -d nutrition_bot -c "\dt"`
- [ ] Бот отвечает в Telegram на `/start`
- [ ] Распознавание фото работает
- [ ] Команда `/v яблоко 150` работает

---

## 📞 Поддержка

Если возникли проблемы:

1. Проверьте логи: `docker-compose logs bot`
2. Проверьте статус: `docker-compose ps`
3. Прочитайте [VPS_DEPLOY.md](VPS_DEPLOY.md)
4. Проверьте [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)

---

## 🎉 Успешный деплой!

После успешного запуска:

1. ✅ Бот работает 24/7
2. ✅ Автоматический перезапуск при сбоях
3. ✅ Ежедневные бэкапы базы данных (3:00)
4. ✅ Дайджесты отправляются в 21:00 МСК

**Наслаждайтесь использованием! 🍎📊🤖**

---

**Время установки: 5-10 минут**
**Версия: 1.0.0**
**Дата: 2025-01-15**
