# Инструкция по деплою на VPS

Полная пошаговая инструкция для развертывания Nutrition Bot на VPS с использованием Docker.

## Предварительные требования

- VPS с Ubuntu 20.04/22.04 или Debian 11/12
- Root доступ или sudo права
- Минимум 1 GB RAM
- 10 GB свободного места на диске

---

## Шаг 1: Подключение к VPS

```bash
# Подключитесь к серверу
ssh root@your_vps_ip

# Или с использованием пользователя с sudo
ssh username@your_vps_ip
```

---

## Шаг 2: Обновление системы

```bash
# Обновите пакеты
sudo apt update && sudo apt upgrade -y

# Установите необходимые утилиты
sudo apt install -y curl git nano htop
```

---

## Шаг 3: Установка Docker и Docker Compose

```bash
# Установка Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Добавление пользователя в группу docker (опционально)
sudo usermod -aG docker $USER

# Установка Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.24.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Проверка установки
docker --version
docker-compose --version

# Перезапустите сессию (если добавляли в группу docker)
exit
ssh username@your_vps_ip
```

---

## Шаг 4: Создание директории проекта

```bash
# Создайте директорию для проекта
sudo mkdir -p /opt/nutrition_bot
sudo chown $USER:$USER /opt/nutrition_bot
cd /opt/nutrition_bot
```

---

## Шаг 5: Загрузка проекта

### Вариант А: Через Git (если есть репозиторий)

```bash
# Клонируйте репозиторий
git clone https://github.com/your-username/nutrition_bot.git .

# Или если приватный репозиторий
git clone https://your-token@github.com/your-username/nutrition_bot.git .
```

### Вариант Б: Загрузка ZIP файла

```bash
# На локальной машине создайте архив
cd /Users/volkovvladislav/PycharmProjects/calApp
tar -czf nutrition_bot.tar.gz nutrition_bot/

# Загрузите на сервер
scp nutrition_bot.tar.gz username@your_vps_ip:/opt/

# На сервере распакуйте
cd /opt
tar -xzf nutrition_bot.tar.gz
cd nutrition_bot
```

### Вариант В: Через rsync (рекомендуется)

```bash
# На локальной машине
cd /Users/volkovvladislav/PycharmProjects/calApp
rsync -avz --exclude 'venv' --exclude '__pycache__' --exclude '*.pyc' --exclude 'logs' nutrition_bot/ username@your_vps_ip:/opt/nutrition_bot/
```

---

## Шаг 6: Настройка .env файла

```bash
cd /opt/nutrition_bot

# Создайте .env файл
nano .env
```

Вставьте следующее содержимое:

```env
# Telegram
TELEGRAM_BOT_TOKEN=***REMOVED***

# OpenAI
OPENAI_API_KEY=***REMOVED***

# Database (используется внутри Docker)
DATABASE_URL=postgresql://nutrition_user:***REMOVED***@db:5432/nutrition_bot

# Database credentials для Docker Compose
DB_USER=nutrition_user
DB_PASSWORD=***REMOVED***
DB_NAME=nutrition_bot

# Settings
TIMEZONE=Europe/Moscow
DIGEST_TIME=21:00
USER_CHAT_ID=***REMOVED***
LOG_LEVEL=INFO
```

Сохраните: `Ctrl+O`, `Enter`, выход: `Ctrl+X`

**Важно**: Замените `DB_PASSWORD` на надежный пароль!

---

## Шаг 7: Обновление docker-compose.yml

Создайте или обновите `docker-compose.yml`:

```bash
nano docker-compose.yml
```

Вставьте содержимое:

```yaml
version: '3.8'

services:
  db:
    image: postgres:16-alpine
    container_name: nutrition_db
    restart: unless-stopped
    environment:
      POSTGRES_DB: ${DB_NAME:-nutrition_bot}
      POSTGRES_USER: ${DB_USER:-nutrition_user}
      POSTGRES_PASSWORD: ${DB_PASSWORD:-nutrition_password}
    volumes:
      - pgdata:/var/lib/postgresql/data
    networks:
      - nutrition_network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER:-nutrition_user} -d ${DB_NAME:-nutrition_bot}"]
      interval: 10s
      timeout: 5s
      retries: 5

  bot:
    build: .
    container_name: nutrition_bot
    restart: unless-stopped
    env_file:
      - .env
    depends_on:
      db:
        condition: service_healthy
    volumes:
      - ./logs:/app/logs
    networks:
      - nutrition_network

volumes:
  pgdata:
    driver: local

networks:
  nutrition_network:
    driver: bridge
```

Сохраните файл.

---

## Шаг 8: Запуск проекта

```bash
# Убедитесь, что находитесь в директории проекта
cd /opt/nutrition_bot

# Сборка образов
docker-compose build

# Запуск контейнеров
docker-compose up -d

# Проверка статуса
docker-compose ps
```

Вы должны увидеть:
```
NAME            IMAGE               STATUS         PORTS
nutrition_bot   nutrition_bot-bot   Up 10 seconds
nutrition_db    postgres:16-alpine  Up 10 seconds  5432/tcp
```

---

## Шаг 9: Проверка логов

```bash
# Логи бота
docker-compose logs -f bot

# Логи базы данных
docker-compose logs -f db

# Все логи
docker-compose logs -f

# Выход из логов: Ctrl+C
```

Вы должны увидеть:
```
nutrition_bot  | [INFO] Database initialized successfully
nutrition_bot  | [INFO] All handlers registered successfully
nutrition_bot  | [INFO] Scheduler started - Daily digest at 21:00 Europe/Moscow
nutrition_bot  | [INFO] Starting bot polling...
```

---

## Шаг 10: Проверка базы данных

```bash
# Подключитесь к контейнеру PostgreSQL
docker-compose exec db psql -U nutrition_user -d nutrition_bot

# Проверьте таблицы
\dt

# Должны увидеть:
#  public | chat_logs    | table | nutrition_user
#  public | digest       | table | nutrition_user
#  public | meals        | table | nutrition_user
#  public | meals_draft  | table | nutrition_user

# Выход из psql
\q
```

---

## Шаг 11: Тестирование бота

1. Откройте Telegram
2. Найдите своего бота по username
3. Отправьте `/start`
4. Проверьте, что бот отвечает

```bash
# Если бот не отвечает, проверьте логи
docker-compose logs bot | tail -50
```

---

## Шаг 12: Настройка автозапуска при перезагрузке

Docker Compose с `restart: unless-stopped` автоматически перезапустит контейнеры.

Дополнительно создайте systemd service:

```bash
sudo nano /etc/systemd/system/nutrition-bot.service
```

Вставьте:

```ini
[Unit]
Description=Nutrition Bot Docker Compose
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/nutrition_bot
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down
User=root

[Install]
WantedBy=multi-user.target
```

Активируйте:

```bash
sudo systemctl daemon-reload
sudo systemctl enable nutrition-bot.service
sudo systemctl start nutrition-bot.service
```

---

## Управление ботом на VPS

### Остановка

```bash
cd /opt/nutrition_bot
docker-compose stop
```

### Запуск

```bash
cd /opt/nutrition_bot
docker-compose start
```

### Перезапуск

```bash
cd /opt/nutrition_bot
docker-compose restart
```

### Полная остановка с удалением контейнеров

```bash
cd /opt/nutrition_bot
docker-compose down
```

### Остановка с удалением volumes (удалит БД!)

```bash
cd /opt/nutrition_bot
docker-compose down -v
```

---

## Обновление бота

```bash
cd /opt/nutrition_bot

# Остановите контейнеры
docker-compose down

# Обновите код (если через git)
git pull

# Или загрузите новые файлы через rsync
# rsync -avz ... (см. Шаг 5)

# Пересоберите образы
docker-compose build

# Запустите
docker-compose up -d

# Проверьте логи
docker-compose logs -f bot
```

---

## Мониторинг и обслуживание

### Просмотр логов

```bash
# Логи бота в реальном времени
docker-compose logs -f bot

# Последние 100 строк
docker-compose logs --tail=100 bot

# Логи с временными метками
docker-compose logs -t bot
```

### Использование ресурсов

```bash
# Мониторинг ресурсов Docker
docker stats

# Использование диска
df -h
du -sh /opt/nutrition_bot/
docker system df
```

### Очистка Docker

```bash
# Удаление неиспользуемых образов
docker image prune -a

# Удаление неиспользуемых volumes
docker volume prune

# Полная очистка (осторожно!)
docker system prune -a --volumes
```

---

## Бэкап базы данных

### Создание бэкапа

```bash
# Создайте директорию для бэкапов
mkdir -p /opt/nutrition_bot/backups

# Создайте бэкап
docker-compose exec -T db pg_dump -U nutrition_user nutrition_bot > /opt/nutrition_bot/backups/backup_$(date +%Y%m%d_%H%M%S).sql

# Или с сжатием
docker-compose exec -T db pg_dump -U nutrition_user nutrition_bot | gzip > /opt/nutrition_bot/backups/backup_$(date +%Y%m%d_%H%M%S).sql.gz
```

### Восстановление из бэкапа

```bash
# Из обычного файла
docker-compose exec -T db psql -U nutrition_user nutrition_bot < /opt/nutrition_bot/backups/backup_20240115_120000.sql

# Из сжатого файла
gunzip -c /opt/nutrition_bot/backups/backup_20240115_120000.sql.gz | docker-compose exec -T db psql -U nutrition_user nutrition_bot
```

### Автоматический бэкап (cron)

```bash
# Откройте crontab
crontab -e

# Добавьте строку для ежедневного бэкапа в 3:00
0 3 * * * docker-compose -f /opt/nutrition_bot/docker-compose.yml exec -T db pg_dump -U nutrition_user nutrition_bot | gzip > /opt/nutrition_bot/backups/backup_$(date +\%Y\%m\%d_\%H\%M\%S).sql.gz

# Добавьте очистку старых бэкапов (старше 7 дней)
0 4 * * * find /opt/nutrition_bot/backups -name "backup_*.sql.gz" -mtime +7 -delete
```

---

## Проверка здоровья системы

### Скрипт health check

```bash
nano /opt/nutrition_bot/health_check.sh
```

Вставьте:

```bash
#!/bin/bash

echo "=== Nutrition Bot Health Check ==="
echo ""

# Проверка контейнеров
echo "1. Docker Containers:"
docker-compose -f /opt/nutrition_bot/docker-compose.yml ps
echo ""

# Проверка логов (последние ошибки)
echo "2. Recent Errors in Logs:"
docker-compose -f /opt/nutrition_bot/docker-compose.yml logs --tail=20 bot | grep -i error || echo "No errors found"
echo ""

# Проверка базы данных
echo "3. Database Connection:"
docker-compose -f /opt/nutrition_bot/docker-compose.yml exec -T db psql -U nutrition_user -d nutrition_bot -c "SELECT COUNT(*) as meals_count FROM meals;" 2>/dev/null || echo "Database connection failed"
echo ""

# Использование диска
echo "4. Disk Usage:"
df -h /opt/nutrition_bot
echo ""

# Использование памяти
echo "5. Memory Usage:"
free -h
echo ""

echo "Health check completed."
```

Сделайте исполняемым:

```bash
chmod +x /opt/nutrition_bot/health_check.sh

# Запуск
/opt/nutrition_bot/health_check.sh
```

---

## Решение проблем

### Проблема: Бот не отвечает

```bash
# 1. Проверьте контейнеры
docker-compose ps

# 2. Проверьте логи
docker-compose logs bot | tail -50

# 3. Проверьте переменные окружения
docker-compose exec bot env | grep TELEGRAM

# 4. Перезапустите
docker-compose restart bot
```

### Проблема: Ошибка подключения к БД

```bash
# 1. Проверьте, что БД запущена
docker-compose ps db

# 2. Проверьте логи БД
docker-compose logs db

# 3. Проверьте healthcheck
docker inspect nutrition_db | grep -A 10 Health

# 4. Подключитесь вручную
docker-compose exec db psql -U nutrition_user -d nutrition_bot
```

### Проблема: Ошибки OpenAI API

```bash
# 1. Проверьте API ключ в .env
cat .env | grep OPENAI_API_KEY

# 2. Проверьте квоту на https://platform.openai.com/usage

# 3. Проверьте логи на ошибки API
docker-compose logs bot | grep -i openai
```

### Проблема: Контейнер постоянно перезапускается

```bash
# Посмотрите причину
docker-compose logs bot --tail=100

# Остановите автоперезапуск временно
docker update --restart=no nutrition_bot

# Запустите вручную для отладки
docker-compose up bot
```

---

## Мониторинг производительности

### Установка monitoring tools

```bash
# Установка htop
sudo apt install htop

# Мониторинг в реальном времени
htop

# Docker stats
docker stats nutrition_bot nutrition_db
```

---

## Безопасность

### Настройка файрвола (ufw)

```bash
# Установка ufw (если нет)
sudo apt install ufw

# Разрешить SSH
sudo ufw allow ssh

# Разрешить HTTP/HTTPS (если нужен web dashboard)
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Включить файрвол
sudo ufw enable

# Проверить статус
sudo ufw status
```

### Обновление системы

```bash
# Регулярно обновляйте систему
sudo apt update && sudo apt upgrade -y

# Автоматические обновления безопасности
sudo apt install unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades
```

---

## Чеклист успешного деплоя

- [ ] VPS настроен и доступен
- [ ] Docker и Docker Compose установлены
- [ ] Проект загружен в `/opt/nutrition_bot`
- [ ] `.env` файл создан с реальными ключами
- [ ] `docker-compose build` выполнен успешно
- [ ] Контейнеры запущены: `docker-compose ps`
- [ ] База данных создана и таблицы существуют
- [ ] Логи не показывают ошибок
- [ ] Бот отвечает на `/start` в Telegram
- [ ] Тест фото работает
- [ ] Тест `/v яблоко 150` работает
- [ ] Systemd service настроен (опционально)
- [ ] Бэкап настроен

---

## Быстрые команды (шпаргалка)

```bash
# Перейти в директорию
cd /opt/nutrition_bot

# Посмотреть логи
docker-compose logs -f bot

# Перезапустить
docker-compose restart

# Остановить
docker-compose stop

# Запустить
docker-compose start

# Пересобрать и перезапустить
docker-compose down && docker-compose build && docker-compose up -d

# Бэкап БД
docker-compose exec -T db pg_dump -U nutrition_user nutrition_bot | gzip > backups/backup_$(date +%Y%m%d).sql.gz

# Проверка здоровья
docker-compose ps && docker-compose logs --tail=20 bot

# Статистика ресурсов
docker stats nutrition_bot nutrition_db
```

---

## Полная последовательность команд для деплоя

Скопируйте и выполните по порядку:

```bash
# 1. Подключение и обновление системы
ssh root@your_vps_ip
apt update && apt upgrade -y
apt install -y curl git nano htop

# 2. Установка Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
curl -L "https://github.com/docker/compose/releases/download/v2.24.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# 3. Создание директории
mkdir -p /opt/nutrition_bot
cd /opt/nutrition_bot

# 4. Загрузка проекта (выполните на локальной машине)
# rsync -avz --exclude 'venv' --exclude '__pycache__' nutrition_bot/ root@your_vps_ip:/opt/nutrition_bot/

# 5. Создание .env (на сервере)
nano .env
# Вставьте содержимое из Шага 6

# 6. Запуск
docker-compose build
docker-compose up -d

# 7. Проверка
docker-compose ps
docker-compose logs -f bot

# 8. Тест в Telegram
# Отправьте /start боту

# Готово! ✅
```

---

**Время деплоя: ~15 минут**

**Поддержка**: Если возникли проблемы, проверьте логи: `docker-compose logs bot`
