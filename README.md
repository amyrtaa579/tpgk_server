# Anmicius API

API для колледжа Anmicius на FastAPI с использованием PostgreSQL и MinIO.

## 📋 Описание

REST API для предоставления информации о колледже, специальностях, приёмной кампании, новостях и профориентационном тестировании.

### Доступные домены

- `anmicius.ru` — основной сайт
- `api.anmicius.ru` — API
- `admin.anmicius.ru` — админ-панель
- `minio.anmicius.ru` — хранилище файлов (MinIO)

### HTTPS/SSL

Проект поддерживает автоматическое получение SSL-сертификатов через Let's Encrypt.

**Для production с HTTPS:**

1. Убедитесь, что домены указывают на ваш сервер:
   - `anmicius.ru`
   - `www.anmicius.ru`
   - `api.anmicius.ru`
   - `admin.anmicius.ru`
   - `minio.anmicius.ru`

2. Получите SSL-сертификаты:
```bash
./scripts/ssl-cert.sh your-email@example.com
```

3. Запустите все сервисы:
```bash
docker-compose up -d
```

4. Примените миграции:
```bash
docker-compose exec api alembic upgrade head
```

После настройки все домены будут доступны по HTTPS:
- `https://anmicius.ru` — основной сайт
- `https://api.anmicius.ru` — API (Swagger: `/docs`)
- `https://admin.anmicius.ru` — админ-панель
- `https://minio.anmicius.ru` — MinIO консоль (`/admin`)

## 🏗️ Архитектура

Проект использует **чистую архитектуру** (Clean Architecture) с разделением на слои:

```
app/
├── core/           # Конфигурация, исключения, утилиты
├── domain/         # Бизнес-модели и интерфейсы репозиториев
├── application/    # Use Cases (бизнес-логика)
├── infrastructure/ # Реализации репозиториев, ORM модели, БД
└── presentation/   # API роутеры и Pydantic схемы
```

### Слои

1. **Domain** — бизнес-модели и интерфейсы (не зависят от фреймворков)
2. **Application** — use cases (бизнес-правила)
3. **Infrastructure** — работа с БД, внешними сервисами
4. **Presentation** — HTTP API (FastAPI)

## 🚀 Быстрый старт

### Требования

- Docker и Docker Compose
- Или Python 3.11+ для локальной разработки

### Запуск через Docker

1. Клонируйте репозиторий:
```bash
cd anmicius-api
```

2. Создайте файл `.env` (опционально):
```bash
cp .env.example .env
```

3. Запустите контейнеры:
```bash
docker-compose up -d
```

4. Примените миграции:
```bash
docker-compose exec api alembic upgrade head
```

### Локальная разработка

1. Установите зависимости:
```bash
pip install -r requirements.txt
```

2. Создайте `.env` файл:
```bash
cp .env.example .env
```

3. Запустите PostgreSQL и MinIO (через Docker):
```bash
docker-compose up -d postgres minio minio-init
```

4. Примените миграции:
```bash
alembic upgrade head
```

5. Запустите сервер разработки:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 📚 API Документация

После запуска API документация доступна по адресам:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## 🔌 Эндпоинты API v1

Базовый URL: `/api/v1`

### Информация о колледже

| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| GET | `/about` | Информация о колледже |
| GET | `/admission` | Информация о приёмной кампании |

### Специальности

| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| GET | `/specialties` | Список специальностей (с пагинацией) |
| GET | `/specialties/{code}` | Детали специальности |
| GET | `/specialties/{code}/facts` | Заголовки фактов специальности |
| GET | `/facts/{fact_id}` | Детали факта |

### Новости

| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| GET | `/news` | Список новостей (с пагинацией) |
| GET | `/news/{slug}` | Детали новости |

### FAQ и документы

| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| GET | `/faq` | Часто задаваемые вопросы |
| GET | `/documents` | Документы для скачивания |
| GET | `/images` | Галерея изображений |

### Профориентационный тест

| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| GET | `/test/questions` | Вопросы теста |
| POST | `/test/results` | Отправка ответов и получение рекомендации |

### Health check

| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| GET | `/health` | Проверка статуса API |
| GET | `/` | Информация о сервисе |

## 📝 Примеры запросов

### Получить список специальностей

```bash
curl http://localhost:8000/api/v1/specialties?page=1&limit=10
```

### Получить детали специальности

```bash
curl http://localhost:8000/api/v1/specialties/15.02.19
```

### Пройти профориентационный тест

```bash
curl -X POST http://localhost:8000/api/v1/test/results \
  -H "Content-Type: application/json" \
  -d '{
    "answers": [
      {"question_id": 1, "selected": "Разбирать и собирать технику"},
      {"question_id": 2, "selected": "Связанную с физическим трудом"},
      {"question_id": 3, "selected": "Да, мне это интересно"},
      {"question_id": 4, "selected": "Высокая зарплата"},
      {"question_id": 5, "selected": "Готов учиться постоянно"},
      {"question_id": 6, "selected": "Физика/Математика"},
      {"question_id": 7, "selected": "Работаю на заводе/предприятии"},
      {"question_id": 8, "selected": "Способ зарабатывать деньги"},
      {"question_id": 9, "selected": "Да, я не боюсь трудностей"},
      {"question_id": 10, "selected": "Да, это моя мечта"}
    ]
  }'
```

## 🗄️ База данных

### Миграции

Создание новой миграции:
```bash
alembic revision --autogenerate -m "Описание миграции"
```

Применение миграций:
```bash
alembic upgrade head
```

Откат миграций:
```bash
alembic downgrade -1
```

## ⚙️ Конфигурация

Переменные окружения (файл `.env`):

| Переменная | Описание | По умолчанию |
|------------|----------|--------------|
| `POSTGRES_USER` | Пользователь PostgreSQL | `anmicius` |
| `POSTGRES_PASSWORD` | Пароль PostgreSQL | `anmicius_secret_password` |
| `POSTGRES_DB` | Имя базы данных | `anmicius_db` |
| `POSTGRES_HOST` | Хост PostgreSQL | `postgres` |
| `POSTGRES_PORT` | Порт PostgreSQL | `5432` |
| `MINIO_ENDPOINT` | Хост MinIO | `minio:9000` |
| `MINIO_ACCESS_KEY` | Access key MinIO | `minioadmin` |
| `MINIO_SECRET_KEY` | Secret key MinIO | `minioadmin` |
| `MINIO_BUCKET` | Имя бакета | `anmicius-media` |
| `DEBUG` | Режим отладки | `false` |
| `CORS_ORIGINS` | Разрешённые CORS домены | `https://anmicius.ru,...` |

## 🧪 Тестирование

Запуск тестов:
```bash
pytest
```

Запуск с покрытием:
```bash
pytest --cov=app --cov-report=html
```

## 📦 Docker контейнеры

| Контейнер | Порт | Описание |
|-----------|------|----------|
| `anmicius-api` | 8000 | FastAPI приложение |
| `anmicius-postgres` | 5432 | PostgreSQL база данных |
| `anmicius-minio` | 9000, 9001 | MinIO (S3-совместимое хранилище) |
| `anmicius-nginx` | 80, 443 | Nginx reverse proxy + SSL |
| `anmicius-certbot` | — | Автоматическое обновление SSL-сертификатов |

## 🔧 Разработка

### Структура проекта

```
anmicius-api/
├── alembic/              # Миграции БД
│   ├── versions/         # Файлы миграций
│   └── env.py
├── app/
│   ├── core/             # Конфигурация, исключения
│   ├── domain/           # Бизнес-модели
│   ├── application/      # Use Cases
│   ├── infrastructure/   # Репозитории, ORM
│   ├── presentation/     # API роутеры, схемы
│   └── main.py           # Точка входа
├── nginx/                # Конфигурация Nginx + SSL
│   ├── nginx.conf        # Конфиг Nginx для доменов
│   ├── www               # Webroot для Certbot
│   └── logs              # Логи Nginx
├── scripts/
│   └── ssl-cert.sh       # Скрипт получения SSL-сертификатов
├── admin-panel/          # Админ-панель (Vue/React)
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
```

### Добавление нового эндпоинта

1. Создайте модель в `app/domain/models.py`
2. Добавьте интерфейс репозитория в `app/domain/repositories.py`
3. Реализуйте репозиторий в `app/infrastructure/repositories.py`
4. Создайте Use Case в `app/application/use_cases.py`
5. Добавьте схему в `app/presentation/schemas.py`
6. Создайте роут в `app/presentation/routes.py`

## 📄 Лицензия

Проект создан для образовательных целей.
