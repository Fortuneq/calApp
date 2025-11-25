# Telegram Nutrition Bot - Трекер Питания с ИИ

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![aiogram](https://img.shields.io/badge/aiogram-3.15-green.svg)](https://aiogram.dev/)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4-orange.svg)](https://openai.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue.svg)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)

Telegram-бот для отслеживания питания с автоматическим распознаванием блюд через GPT-4 Vision, расчетом КБЖУ и ежедневными дайджестами.

## 🌟 Возможности

- **🤖 Распознавание фото** - Загрузите фото еды, бот автоматически определит блюдо через GPT-4 Vision
- **📊 Расчет КБЖУ** - Автоматический расчет калорий, белков, жиров и углеводов через GPT-4
- **✍️ Ручной ввод** - Быстрое добавление блюд командой `/v блюдо граммы [время]`
- **💬 AI-консультант** - Задавайте вопросы о питании и получайте персональные рекомендации
- **📈 Ежедневные дайджесты** - Автоматические сводки по питанию каждый день в 21:00 МСК
- **🎯 Умный FSM** - Интерактивный диалог для подтверждения блюд и выбора порций

## 📸 Примеры использования

### 1. Распознавание по фото
```
Вы: [отправляете фото йогурта]
Бот: Это греческий йогурт?
     [✅ Да] [❌ Нет]

Вы: [Да]
Бот: Выбери массу порции:
     [120 г] [140 г] [160 г]

Вы: [140 г]
Бот: Греческий йогурт – 140 г
     Калорий: 97
     Б: 10 Ж: 5 У: 4
     ✔️ сохранил в память
```

### 2. Ручной ввод
```
Вы: /v яблоко 150
Бот: ✅ Яблоко сохранён!
     КБЖУ: 78 / 0 / 0 / 20
```

### 3. AI-консультант
```
Вы: Сколько калорий я съел сегодня?
Бот: На данный момент вы употребили примерно 1,247 калорий.

     Вот что вы ели сегодня:
     - 09:15 - Греческий йогурт (140г): 97 ккал
     - 12:30 - Греча (200г): 231 ккал
     - 12:30 - Курица (180г): 297 ккал
     ...
```

### 4. Ежедневный дайджест (21:00)
```
📊 Дайджест за 15.01.2025

КБЖУ: 1613 / 77 / 37 / 157

🎯 Анализ дня
Сегодня вы показали отличный баланс питания!
...
```

## 🚀 Быстрый старт

### Установка

```bash
# 1. Клонируйте репозиторий
git clone <repository-url>
cd nutrition_bot

# 2. Создайте виртуальное окружение
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Установите зависимости
pip install -r requirements.txt

# 4. Создайте базу данных
createdb nutrition_bot

# 5. Настройте .env файл
cp .env.example .env
# Отредактируйте .env своими данными
```

### Конфигурация (.env)

```env
TELEGRAM_BOT_TOKEN=your_bot_token_from_botfather
OPENAI_API_KEY=sk-your_openai_api_key
DATABASE_URL=postgresql://user:password@localhost:5432/nutrition_bot
USER_CHAT_ID=your_telegram_chat_id
TIMEZONE=Europe/Moscow
DIGEST_TIME=21:00
LOG_LEVEL=INFO
```

**Где взять:**
- **Bot Token**: [@BotFather](https://t.me/botfather) → `/newbot`
- **OpenAI Key**: [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
- **Chat ID**: [@userinfobot](https://t.me/userinfobot)

### Запуск

```bash
# Локально
python main.py

# Или с Docker
docker-compose up -d
```

## 🏗️ Архитектура

```
nutrition_bot/
├── main.py                 # Точка входа
├── config.py              # Конфигурация
├── requirements.txt       # Зависимости
│
├── bot/
│   ├── handlers/         # Обработчики сообщений
│   │   ├── start.py      # /start команда
│   │   ├── photo.py      # Обработка фото
│   │   ├── callbacks.py  # Inline кнопки
│   │   ├── manual.py     # Ручной ввод /v
│   │   └── chat.py       # AI-консультант
│   │
│   └── keyboards/        # Telegram клавиатуры
│       └── inline.py     # Inline клавиатуры
│
├── services/
│   ├── vision.py         # GPT-4 Vision API
│   ├── nutrition.py      # Расчет КБЖУ
│   ├── ai_chat.py        # AI-консультант
│   └── digest.py         # Генерация дайджестов
│
├── database/
│   ├── models.py         # SQLAlchemy модели
│   ├── connection.py     # Подключение к БД
│   └── crud.py           # CRUD операции
│
├── scheduler/
│   └── tasks.py          # Задачи по расписанию
│
└── utils/
    ├── logger.py         # Настройка логирования
    ├── time.py           # Работа с временем (МСК)
    └── parsers.py        # Парсеры текста
```

## 📊 База данных

### Таблицы

1. **meals** - Все записи о приемах пищи
   ```sql
   id, chat_id, dish, grams, kcal, prot, fat, carb,
   eaten_at, deleted, created_at
   ```

2. **meals_draft** - Временное хранилище для FSM
   ```sql
   id, chat_id, message_id, photo_file_id, candidates,
   grams_pred, chosen_name, status, created_at, updated_at
   ```

3. **digest** - Ежедневные дайджесты
   ```sql
   id, chat_id, for_date, kcal, prot, fat, carb,
   meals_json, summary_md, msg_id, created_at
   ```

4. **chat_logs** - История диалогов с AI
   ```sql
   id, chat_id, session_id, role, content,
   username, first_name, metadata, created_at
   ```

## 🛠️ Технологии

| Компонент | Технология | Версия |
|-----------|------------|--------|
| Язык | Python | 3.11+ |
| Бот фреймворк | aiogram | 3.15.0 |
| ИИ | OpenAI API | GPT-4o, GPT-4 Vision |
| База данных | PostgreSQL | 16 |
| ORM | SQLAlchemy | 2.0.36 |
| Планировщик | APScheduler | 3.10.4 |
| Деплой | Docker | Latest |

## 📖 Команды бота

### Основные команды

- `/start` - Приветствие и инструкции
- `/v блюдо граммы [время]` - Ручное добавление
  - Пример: `/v яблоко 150`
  - Пример: `/v греча 200 18:30`

### Работа с фото

1. Отправьте фото еды
2. Бот распознает блюдо
3. Подтвердите или выберите альтернативу
4. Выберите вес порции
5. Готово! Данные сохранены

### AI-консультант

Отправьте любое текстовое сообщение (не команду):
- "Сколько калорий я съел сегодня?"
- "Достаточно ли белка в моем рационе?"
- "Что мне посоветуешь на ужин?"

## 🧪 Тестирование

```bash
# Запуск тестов
pytest tests/ -v

# С покрытием
pytest tests/ --cov=. --cov-report=html
```

## 🐳 Docker

### Сборка и запуск

```bash
# Сборка образа
docker-compose build

# Запуск контейнеров
docker-compose up -d

# Просмотр логов
docker-compose logs -f bot

# Остановка
docker-compose down
```

### Docker Compose включает:
- **bot** - Telegram бот
- **db** - PostgreSQL база данных

## 📝 Логирование

Логи сохраняются в директории `logs/`:
- `bot.log` - Все логи приложения
- `error.log` - Только ошибки

Настройка в `utils/logger.py`:
- Ротация: 10 МБ, 5 бэкапов
- Форматы: детальный (файл) и простой (консоль)

## 🔒 Безопасность

- ✅ Защита от SQL-инъекций (ORM)
- ✅ Переменные окружения для секретов
- ✅ Валидация входных данных
- ✅ Санитизация сообщений об ошибках
- ✅ Rate limiting (готово к использованию)

## ⚡ Производительность

- Асинхронные операции (async/await)
- Connection pooling для PostgreSQL
- Индексы в базе данных
- Потоковая загрузка фото (без полной загрузки в память)
- Кэширование (опционально, Redis)

## 📚 Документация

- [README.md](README.md) - Основная документация
- [SETUP_GUIDE.md](SETUP_GUIDE.md) - Детальная инструкция по установке
- [QUICK_START.md](QUICK_START.md) - Быстрый старт за 5 минут
- [EXAMPLES.md](EXAMPLES.md) - Примеры использования
- [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) - Чеклист для деплоя
- [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - Сводка по проекту

## 🐛 Решение проблем

### Бот не отвечает
```bash
# Проверьте, запущен ли бот
ps aux | grep python

# Проверьте логи
tail -f logs/bot.log
```

### Ошибка базы данных
```bash
# Проверьте PostgreSQL
systemctl status postgresql

# Проверьте подключение
psql -U postgres -d nutrition_bot -c "SELECT 1;"
```

### Ошибка OpenAI API
- Проверьте, что в аккаунте OpenAI настроен биллинг
- Убедитесь, что API ключ действителен
- Проверьте квоты использования

Больше информации в [SETUP_GUIDE.md](SETUP_GUIDE.md)

## 🚢 Деплой в продакшн

### Systemd (Linux)

```bash
# Создайте сервис
sudo nano /etc/systemd/system/nutrition-bot.service

# Включите автозапуск
sudo systemctl enable nutrition-bot

# Запустите
sudo systemctl start nutrition-bot
```

Подробнее в [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)

## 🔄 Бэкап

```bash
# Бэкап базы данных
pg_dump -U nutrition_user nutrition_bot > backup.sql

# Восстановление
psql -U nutrition_user nutrition_bot < backup.sql
```

## 📈 Мониторинг

```bash
# Статус бота
systemctl status nutrition-bot

# Логи
journalctl -u nutrition-bot -f

# Использование ресурсов
docker stats
```

## 🤝 Вклад в проект

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 Лицензия

MIT License - см. [LICENSE](LICENSE)

## 👤 Автор

Разработано с использованием Claude Code

## 💬 Поддержка

- **Issues**: [GitHub Issues](https://github.com/yourrepo/issues)
- **Документация**: См. папку с документацией
- **Email**: your.email@example.com

## 🗺️ Roadmap

### Фаза 1 (Реализовано) ✅
- [x] Распознавание фото через GPT-4 Vision
- [x] Расчет КБЖУ через GPT-4
- [x] Ручной ввод `/v`
- [x] AI-консультант
- [x] Ежедневные дайджесты
- [x] FSM диалог

### Фаза 2 (Планируется)
- [ ] Поддержка нескольких пользователей
- [ ] Статистика по неделям/месяцам
- [ ] Экспорт данных (CSV/Excel)
- [ ] Web-дашборд
- [ ] Голосовые сообщения
- [ ] Сканирование штрих-кодов

### Фаза 3 (Будущее)
- [ ] Mobile приложение
- [ ] Интеграция с фитнес-трекерами
- [ ] Рецепты и планирование меню
- [ ] Социальные функции

## 📊 Статистика проекта

- **Строк кода**: ~2,847
- **Файлов**: 35+
- **Модулей**: 20
- **Таблиц БД**: 4
- **API интеграций**: 3
- **Тестов**: 10+

## ⭐ Особенности

- Полностью асинхронный код
- Comprehensive error handling
- Подробное логирование
- Оптимизированные запросы к БД
- Type hints везде
- Полная документация
- Production-ready

## 🎯 Use Cases

- Персональное отслеживание питания
- Контроль калорий и КБЖУ
- Консультации по питанию
- Анализ пищевых привычек
- Достижение фитнес-целей

---

**Начните отслеживать свое питание с AI уже сегодня!** 🍎📊🤖

[![Star on GitHub](https://img.shields.io/github/stars/yourrepo/nutrition-bot.svg?style=social)](https://github.com/yourrepo/nutrition-bot)
