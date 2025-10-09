# Telegram Bot Template

Базовый шаблон проекта на основе Aiogram 3.x + FastAPI для создания Telegram ботов с админ-панелью.

## Системные зависимости

- Python 3.12+
- Docker и docker-compose
- make
- uv (Python package manager)

## Быстрый старт с Docker

1. Создайте `.env` файл на основе примера и настройте переменные окружения:
```bash
cp .env.example .env
```

2. Основные переменные для настройки:
```env
# Telegram
TELEGRAM_LOCALES=ru,en
TELEGRAM_BOT_TOKEN=42:ABC
TELEGRAM_DROP_PENDING_UPDATES=False

# Database
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=bot_db
POSTGRES_USER=bot_user
POSTGRES_PASSWORD=your_password

# Server (для админ-панели)
SERVER_HOST=0.0.0.0
SERVER_PORT=8081
SERVER_URL=http://localhost:8081

# Middleware
MIDDLEWARE_SESSION_SECRET_KEY=some
MIDDLEWARE_SESSION_HTTPS_ONLY=True
MIDDLEWARE_CORS_ORIGINS=localhost
MIDDLEWARE_CORS_ALLOW_METHODS=GET,POST,PUT,PATCH,DELETE,OPTIONS
MIDDLEWARE_CORS_ALLOW_HEADERS=Authorization,Content-Type,X-CSRF-TokenSSION_HTTPS_ONLY=True
MIDDLEWARE_SESSION_SECRET_KEY=your_secret_key_here
```

3. Запустите приложение:
```bash
make app-build
make app-run
```

или напрямую через docker compose:
```bash
docker compose up --build -d
```

4. Создайте пользователя-администратора:
```bash
make create-admin
```

Используйте `make` для просмотра всех доступных команд.

## Разработка

### Установка окружения

```bash
uv sync
```

### Работа с миграциями базы данных

**Создать миграцию:**
```bash
make migration message="описание изменений"
```

**Применить миграции:**
```bash
make migrate
```

### Локальный запуск

**Вариант 1: Запуск всего через Docker**
```bash
docker compose up --build
```

**Вариант 2: БД в Docker, приложение локально**
```bash
# Terminal 1 - База данных
docker compose up postgres

# Terminal 2 - Бот с админ-панелью (polling mode)
uv run python -m app
```

Админ-панель будет доступна по адресу: `http://localhost:8080/admin`

**Вариант 3: Webhook режим**

Настройте в `.env`:
```env
TELEGRAM_USE_WEBHOOK=true
TELEGRAM_WEBHOOK_PATH=/webhook/telegram
TELEGRAM_WEBHOOK_SECRET=your_webhook_secret
TELEGRAM_RESET_WEBHOOK=true
SERVER_URL=https://your-domain.com
```

### Запуск тестов

**Локально:**
```bash
alembic upgrade head
pytest -v -s tests
```

**В Docker:**
```bash
make test
```

## Используемые технологии

- [uv](https://docs.astral.sh/uv/) - быстрый менеджер пакетов Python
- [Aiogram 3.x](https://github.com/aiogram/aiogram) - фреймворк для Telegram ботов
- [FastAPI](https://fastapi.tiangolo.com/) - веб-фреймворк для создания API
- [PostgreSQL](https://www.postgresql.org/) - реляционная база данных
- [SQLAlchemy 2.0](https://docs.sqlalchemy.org/en/20/) - ORM для работы с БД
- [Alembic](https://alembic.sqlalchemy.org/en/latest/) - инструмент для миграций БД
- [Starlette Admin](https://jowilf.github.io/starlette-admin/) - админ-панель для FastAPI
- [Pydantic v2](https://docs.pydantic.dev/) - валидация данных и настроек

## Структура проекта

### Основные модули

```
app/
├── admin/                 # Админ-панель (Starlette Admin)
│   ├── auth.py            # Аутентификация
│   ├── middlewares/       # Middleware для админки
│   └── views/             # Представления моделей
├── const.py               # Константы приложения
├── endpoints/             # API endpoints
│   ├── healthcheck.py     # Health checks
│   └── telegram.py        # Webhook handler
├── factory/               # Фабрики создания объектов
│   ├── admin.py           # Настройка админ-панели
│   ├── app_config.py      # Создание конфигурации
│   ├── services.py        # Создание сервисов
│   ├── session_pool.py    # Создание пула сессий БД
│   └── telegram/          # Настройка бота
│       ├── bot.py         # Создание Bot
│       ├── dispatcher.py  # Создание Dispatcher
│       └── fastapi.py     # Настройка FastAPI
├── models/                # Модели данных
│   ├── config/            # Конфигурация приложения
│   ├── dto/               # Data Transfer Objects
│   └── sql/               # SQLAlchemy модели
├── runners/               # Режимы запуска
│   ├── app.py             # Основной runner
│   ├── lifespan.py        # Lifespan managers
│   ├── polling.py         # Polling режим
│   └── webhook.py         # Webhook режим
├── services/              # Бизнес-логика
│   ├── base.py            # Базовый сервис
│   ├── postgres/          # Работа с PostgreSQL
│   │   ├── context.py     # SQLAlchemy context
│   │   └── repositories/  # Репозитории
│   └── user.py            # Сервис пользователей
├── telegram/              # Telegram бот
│   ├── handlers/          # Обработчики команд
│   │   └── main/          # Основные handlers
│   └── middlewares/       # Middleware для бота
│       ├── db.py          # DB session middleware
│       ├── event_typed.py # Базовый typed middleware
│       └── user.py        # User middleware
└── utils/                 # Утилиты
    ├── custom_types.py    # Кастомные типы
    ├── logging/           # Настройка логирования
    └── time.py            # Утилиты для работы со временем
```

### Модели данных

**User** - пользователи Telegram бота
- `telegram_id` - ID пользователя в Telegram
- `name` - имя пользователя
- `username` - username в Telegram
- `language` - язык интерфейса
- `language_code` - код языка от Telegram
- `bot_blocked` - заблокировал ли пользователь бота

Автоматически создается при первом взаимодействии с ботом.

**AdminUser** - администраторы системы
- `username` - логин администратора
- `password` - хеш пароля (bcrypt)
- `name` - отображаемое имя

Используется для входа в админ-панель.

## Основные возможности

### Telegram Bot

- Автоматическая регистрация пользователей при взаимодействии
- Middleware для обработки пользователей
- Поддержка нескольких языков
- Команда `/start` с приветствием
- Поддержка polling и webhook режимов

### Админ-панель

Доступна по адресу `http://localhost:8080/admin` после запуска приложения.
