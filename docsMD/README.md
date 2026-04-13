# Документация Anmicius API

Полная документация для REST API филиала Томского индустриально-гуманитарного колледжа «Anmicius».

## Структура документации

### [API Documentation](./api/README.md)

Полное описание REST API, включая:

| Документ | Описание |
|----------|----------|
| [Обзор API](./api/README.md) | Введение, базовый URL, технологии, архитектура |
| [Архитектура](./api/architecture.md) | Clean Architecture, слои приложения |
| [Аутентификация](./api/authentication.md) | JWT, OAuth2, scopes, регистрация, вход |
| [Публичные эндпоинты](./api/public-endpoints.md) | Специальности, новости, FAQ, документы, тесты |
| [Админ-эндпоинты](./api/admin-endpoints.md) | CRUD операции для всех сущностей |
| [Модели и схемы](./api/models-schemas.md) | Pydantic схемы, доменные модели |
| [Загрузка файлов и MinIO](./api/upload-storage.md) | S3-хранилище, загрузка, типы файлов |
| [Кэширование](./api/caching.md) | Redis, версионирование, инвалидация |
| [Rate Limiting](./api/rate-limiting.md) | Ограничение запросов, SlowAPI |
| [Обработка ошибок](./api/errors.md) | Исключения, коды ответов, валидация |
| [Миграции БД](./api/migrations.md) | Alembic, история схемы данных |
| [Тестирование](./api/testing.md) | Pytest, unit-тесты, интеграционные тесты |
| [Развёртывание](./api/deployment.md) | Docker Compose, Nginx, SSL |
| [Админ-панель](./api/admin-panel.md) | React-панель управления |
| [Примеры запросов](./api/postman-collection.md) | cURL и примеры HTTP-запросов |

### [Подготовка к конференции](./conference-prep.md)

Руководство для подготовки к конференции по бережливому производству:
- Описание проекта и его ценности
- Архитектурные решения и их обоснование
- Оптимизация затрат и ресурсов
- Масштабируемость и производительность
- Возможные вопросы и ответы

## Быстрый старт

```bash
# Клонировать репозиторий
git clone https://github.com/anmicius/anmicius-api.git

# Настроить окружение
cp .env.example .env

# Запустить сервисы
docker-compose up -d

# Применить миграции
docker-compose exec api alembic upgrade head
```

API доступен по адресу: `http://localhost:8000`
Swagger UI: `http://localhost:8000/docs`
ReDoc: `http://localhost:8000/redoc`

## Технологии

| Компонент | Технология |
|-----------|-----------|
| Фреймворк | FastAPI 0.109.2 |
| База данных | PostgreSQL 15 |
| ORM | SQLAlchemy 2.0 |
| Кэш | Redis 7 |
| Хранилище | MinIO (S3-совместимое) |
| Аутентификация | JWT (HS256) |
| Миграции | Alembic |
| Реверс-прокси | Nginx + SSL |

## Лицензия

© 2024-2026 Anmicius College. Все права защищены.
