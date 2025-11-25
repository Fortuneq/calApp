#!/bin/bash

###############################################################################
# Nutrition Bot - VPS Deployment Script
# Автоматический скрипт для развертывания на VPS
###############################################################################

set -e  # Остановка при ошибке

echo "=========================================="
echo "Nutrition Bot - VPS Deployment"
echo "=========================================="
echo ""

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Функция для логирования
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}


# Проверка версий
docker --version
docker compose --version

###############################################################################
# Шаг 5: Создание директории проекта
###############################################################################

log_info "Создание директории проекта..."
 mkdir -p /opt/nutrition_bot
 chown $USER:$USER /opt/nutrition_bot
cd /opt/nutrition_bot

###############################################################################
# Шаг 6: Проверка .env файла
###############################################################################

if [ ! -f .env ]; then
    log_error ".env файл не найден!"
    log_info "Создайте .env файл перед запуском скрипта"
    log_info "Пример:"
    echo ""
    cat << 'EOF'
TELEGRAM_BOT_TOKEN=your_token_here
OPENAI_API_KEY=your_key_here
DATABASE_URL=postgresql://nutrition_user:your_password@db:5432/nutrition_bot
DB_USER=nutrition_user
DB_PASSWORD=your_password
DB_NAME=nutrition_bot
TIMEZONE=Europe/Moscow
DIGEST_TIME=21:00
USER_CHAT_ID=your_chat_id
LOG_LEVEL=INFO
EOF
    echo ""
    exit 1
else
    log_info ".env файл найден"
fi

###############################################################################
# Шаг 7: Проверка docker compose.yml
###############################################################################

if [ ! -f docker compose.yml ]; then
    log_error "docker compose.yml не найден!"
    exit 1
else
    log_info "docker compose.yml найден"
fi

###############################################################################
# Шаг 8: Создание директорий
###############################################################################

log_info "Создание необходимых директорий..."
mkdir -p logs
mkdir -p backups
chmod 755 logs backups

###############################################################################
# Шаг 9: Сборка образов
###############################################################################

log_info "Сборка Docker образов (это может занять несколько минут)..."
docker compose build

###############################################################################
# Шаг 10: Запуск контейнеров
###############################################################################

log_info "Запуск контейнеров..."
docker compose up -d

###############################################################################
# Шаг 11: Ожидание запуска
###############################################################################

log_info "Ожидание запуска контейнеров..."
sleep 10

###############################################################################
# Шаг 12: Проверка статуса
###############################################################################

log_info "Проверка статуса контейнеров..."
docker compose ps

###############################################################################
# Шаг 13: Проверка логов
###############################################################################

log_info "Проверка логов бота..."
docker compose logs --tail=20 bot

###############################################################################
# Шаг 14: Проверка базы данных
###############################################################################

log_info "Проверка базы данных..."
sleep 5
docker compose exec -T db psql -U nutrition_user -d nutrition_bot -c "\dt" || log_warn "Не удалось подключиться к БД"

###############################################################################
# Шаг 15: Создание systemd service
###############################################################################

log_info "Создание systemd service для автозапуска..."
 tee /etc/systemd/system/nutrition-bot.service > /dev/null << 'EOF'
[Unit]
Description=Nutrition Bot Docker Compose
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/nutrition_bot
ExecStart=/usr/local/bin/docker compose up -d
ExecStop=/usr/local/bin/docker compose down
User=root

[Install]
WantedBy=multi-user.target
EOF

 systemctl daemon-reload
 systemctl enable nutrition-bot.service
log_info "Systemd service создан и активирован"

###############################################################################
# Шаг 16: Создание скрипта бэкапа
###############################################################################

log_info "Создание скрипта бэкапа..."
cat > /opt/nutrition_bot/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/opt/nutrition_bot/backups"
DATE=$(date +%Y%m%d_%H%M%S)
docker compose -f /opt/nutrition_bot/docker compose.yml exec -T db pg_dump -U nutrition_user nutrition_bot | gzip > $BACKUP_DIR/backup_$DATE.sql.gz
echo "Backup created: $BACKUP_DIR/backup_$DATE.sql.gz"
# Удаление бэкапов старше 7 дней
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +7 -delete
EOF

chmod +x /opt/nutrition_bot/backup.sh
log_info "Скрипт бэкапа создан: /opt/nutrition_bot/backup.sh"

###############################################################################
# Шаг 17: Настройка cron для бэкапов
###############################################################################

log_info "Настройка автоматических бэкапов (cron)..."
(crontab -l 2>/dev/null; echo "0 3 * * * /opt/nutrition_bot/backup.sh >> /opt/nutrition_bot/logs/backup.log 2>&1") | crontab -
log_info "Автоматические бэкапы настроены (ежедневно в 3:00)"

###############################################################################
# Шаг 18: Создание health check скрипта
###############################################################################

log_info "Создание health check скрипта..."
cat > /opt/nutrition_bot/health_check.sh << 'EOF'
#!/bin/bash
echo "=== Nutrition Bot Health Check ==="
echo ""
echo "1. Docker Containers:"
docker compose -f /opt/nutrition_bot/docker compose.yml ps
echo ""
echo "2. Recent Errors:"
docker compose -f /opt/nutrition_bot/docker compose.yml logs --tail=20 bot | grep -i error || echo "No errors"
echo ""
echo "3. Database:"
docker compose -f /opt/nutrition_bot/docker compose.yml exec -T db psql -U nutrition_user -d nutrition_bot -c "SELECT COUNT(*) FROM meals;" 2>/dev/null || echo "DB Error"
echo ""
echo "4. Disk Usage:"
df -h /opt/nutrition_bot
echo ""
echo "Health check completed."
EOF

chmod +x /opt/nutrition_bot/health_check.sh
log_info "Health check скрипт создан: /opt/nutrition_bot/health_check.sh"

###############################################################################
# Завершение
###############################################################################

echo ""
echo "=========================================="
log_info "Деплой завершен успешно! ✅"
echo "=========================================="
echo ""
echo "Полезные команды:"
echo ""
echo "  Просмотр логов:       docker compose logs -f bot"
echo "  Перезапуск:           docker compose restart"
echo "  Остановка:            docker compose stop"
echo "  Статус:               docker compose ps"
echo "  Проверка здоровья:    ./health_check.sh"
echo "  Бэкап БД:             ./backup.sh"
echo ""
echo "Проверьте бота в Telegram:"
echo "  1. Найдите бота по username"
echo "  2. Отправьте /start"
echo "  3. Попробуйте отправить фото еды"
echo ""
log_info "Логи бота в реальном времени:"
docker compose logs -f bot
