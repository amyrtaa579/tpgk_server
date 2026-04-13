# Anmicius API — Обзор

REST API для филиала Томского индустриально-гуманитарного колледжа «Anmicius». Предоставляет публичный доступ к информации о специальностях, новостях, FAQ, документах, фотогалерее и профориентационном тесте. Админ-панель с JWT-аутентификацией позволяет управлять контентом.

## Базовая информация

| Параметр | Значение |
|----------|----------|
| **Базовый URL** | `https://api.anmicius.ru` |
| **Версия API** | v1 |
| **Фреймворк** | FastAPI 0.109.2 |
| **Swagger UI** | `/docs` |
| **ReDoc** | `/redoc` |
| **OpenAPI спецификация** | `/openapi.json` |

## Префиксы маршрутов

| Префикс | Назначение |
|---------|-----------|
| `/` | Корень, health-check |
| `/auth` | Аутентификация (регистрация, вход, обновление токена) |
| `/api/v1` | Публичное API v1 |
| `/admin` | Администрирование (JWT required) |

## Ключевые эндпоинты

### Публичные (без аутентификации)

```
GET  /                     — Информация о сервисе
GET  /health               — Проверка состояния (БД, Redis, MinIO)
GET  /api/v1/about         — Информация о колледже
GET  /api/v1/admission     — Приёмная кампания
GET  /api/v1/specialties   — Список специальностей (пагинация)
GET  /api/v1/specialties/{code} — Детали специальности
GET  /api/v1/news          — Список новостей
GET  /api/v1/news/{slug}   — Детали новости
GET  /api/v1/faq           — Часто задаваемые вопросы
GET  /api/v1/documents     — Документы
GET  /api/v1/images        — Фотогалерея
GET  /api/v1/test/questions — Вопросы профтеста
POST /api/v1/test/results  — Отправить ответы теста
```

### Аутентификация

```
POST /auth/register        — Регистрация
POST /auth/login           — Вход
POST /auth/refresh         — Обновление токена
POST /auth/logout          — Выход
GET  /auth/me              — Текущий пользователь
```

### Администрирование (JWT required)

```
GET    /admin/users                — Список пользователей
POST   /admin/specialties          — Создать специальность
POST   /admin/news                 — Создать новость
POST   /admin/upload/image         — Загрузить изображение
POST   /admin/upload/document      — Загрузить документ
GET    /admin/cache/stats          — Статистика кэша
POST   /admin/cache/clear          — Очистить кэш
... и более 50 CRUD эндпоинтов
```

## Стек технологий

| Компонент | Технология | Версия |
|-----------|-----------|--------|
| **Backend** | Python + FastAPI | 3.11 / 0.109.2 |
| **База данных** | PostgreSQL | 15 |
| **ORM** | SQLAlchemy (async) | 2.0.25 |
| **Валидация** | Pydantic v2 | 2.5.3 |
| **Миграции** | Alembic | 1.13.1 |
| **Кэш** | Redis | 7 |
| **Хранилище** | MinIO (S3-совместимое) | latest |
| **Аутентификация** | JWT (HS256) | PyJWT 2.8.0 |
| **Rate Limiting** | SlowAPI | 0.1.8 |
| **Логирование** | Structlog | 24.1.0 |
| **Тесты** | pytest + httpx | 7.4.4 / 0.26.0 |
| **Реверс-прокси** | Nginx + Let's Encrypt | Alpine |
| **Контейнеризация** | Docker Compose | — |

## Архитектура

Проект следует **Clean Architecture** с пятью слоями:

```
app/
├── core/           # Конфигурация, JWT, исключения, rate limiter
├── domain/         # Бизнес-модели (dataclass) и интерфейсы репозиториев (ABC)
├── application/    # Use Cases (бизнес-логика) и зависимости аутентификации
├── infrastructure/ # Реализации репозиториев, ORM, БД, MinIO, Redis
└── presentation/   # FastAPI роутеры и Pydantic схемы
```

**Поток зависимостей:** Domain ← Application ← Infrastructure/Presentation

Запрос проходит: `HTTP Request → Router → Use Case → Repository → Database`

## Формат запросов и ответов

### Заголовки

```
Content-Type: application/json
Authorization: Bearer <JWT_TOKEN>
```

### Формат ответа

Все ответы возвращаются в формате JSON. Пример успешного ответа:

```json
{
  "id": 1,
  "title": "Информационные системы и программирование",
  "code": "09.02.07",
  "short_description": "Подготовка программистов..."
}
```

### Формат ошибки

```json
{
  "detail": "Not found",
  "status_code": 404
}
```

## Пагинация

Большинство списков поддерживают пагинацию:

| Параметр | Тип | По умолчанию | Описание |
|----------|-----|-------------|----------|
| `page` | int | 1 | Номер страницы |
| `limit` | int | 10 | Элементов на странице (1-50) |

```json
{
  "items": [...],
  "total": 42,
  "page": 1,
  "limit": 10,
  "pages": 5
}
```

## Аутентификация

API использует **JWT-токены** (JSON Web Tokens):

- **Access Token** — 24 часа
- **Refresh Token** — 30 дней
- **Алгоритм** — HS256

Получение токена через `/auth/login`:

```bash
curl -X POST https://api.anmicius.ru/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "secret"}'
```

Ответ:

```json
{
  "access_token": "eyJhbGci...",
  "refresh_token": "eyJhbGci...",
  "token_type": "bearer"
}
```

## Scopes (области доступа)

| Scope | Описание |
|-------|----------|
| `users:read` | Просмотр пользователей |
| `users:write` | Редактирование пользователей |
| `specialties:read` | Просмотр специальностей (admin) |
| `specialties:write` | Редактирование специальностей |
| `news:read` | Просмотр контента |
| `news:write` | Редактирование контента |
| `facts:read` | Просмотр фактов |
| `facts:write` | Редактирование фактов |
| `upload:write` | Загрузка файлов |

**Суперпользователи** получают все scopes автоматически.
**Обычные пользователи** получают только `*:read` scopes.

## Кэширование

Все публичные эндпоинты кэшируются в **Redis**:

| Эндпоинт | TTL |
|----------|-----|
| Специальности (список) | 5 минут |
| Специальность (детали) | 10 минут |
| Новости (список) | 5 минут |
| Новости (детали) | 1 час |
| FAQ | 1 час |
| Документы | 1 час |
| О колледже | 1 час |

Кэш автоматически инвалидируется при изменении данных через админ-панель.

## Health Check

```bash
curl https://api.anmicius.ru/health
```

```json
{
  "status": "healthy",
  "database": "connected",
  "redis": "connected",
  "minio": "connected"
}
```

## Ограничение запросов (Rate Limiting)

| Эндпоинт | Лимит |
|----------|-------|
| `/auth/login`, `/auth/register` | 10/мин, 30/час |
| Остальные | 60/мин, 1000/час |

При превышении возвращается код **429 Too Many Requests**.

## Переменные окружения

Ключевые параметры конфигурации (`.env`):

| Переменная | Описание | По умолчанию |
|------------|----------|-------------|
| `APP_NAME` | Имя приложения | Anmicius API |
| `APP_VERSION` | Версия | 1.0.0 |
| `DEBUG` | Режим отладки | false |
| `POSTGRES_HOST` | Хост БД | postgres |
| `POSTGRES_DB` | Имя БД | anmicius_db |
| `MINIO_ENDPOINT` | Хост MinIO | minio:9000 |
| `MINIO_BUCKET` | Bucket | anmicius-media |
| `REDIS_HOST` | Хост Redis | redis |
| `JWT_SECRET_KEY` | Секретный ключ JWT | (обязательно изменить) |
| `CORS_ORIGINS` | Разрешённые origins | * |

Полный список — в [`.env.example`](../.env.example).

## Связанные документы

- [Архитектура](./architecture.md) — подробное описание Clean Architecture
- [Аутентификация](./authentication.md) — JWT, OAuth2, scopes
- [Публичные эндпоинты](./public-endpoints.md) — полное описание
- [Админ-эндпоинты](./admin-endpoints.md) — CRUD операции
- [Модели и схемы](./models-schemas.md) — Pydantic схемы, доменные модели
- [Загрузка файлов и MinIO](./upload-storage.md) — S3-хранилище, загрузка, типы файлов
- [Кэширование](./caching.md) — Redis, версионирование, инвалидация
- [Rate Limiting](./rate-limiting.md) — Ограничение запросов, SlowAPI
- [Обработка ошибок](./errors.md) — Исключения, коды ответов, валидация
- [Миграции БД](./migrations.md) — Alembic, история схемы данных
- [Тестирование](./testing.md) — Pytest, unit-тесты, интеграционные тесты
- [Развёртывание](./deployment.md) — Docker Compose, Nginx, SSL
- [Админ-панель](./admin-panel.md) — React-панель управления
- [Примеры запросов](./postman-collection.md) — cURL и примеры HTTP-запросов
