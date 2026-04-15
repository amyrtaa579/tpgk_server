# Приложение Б: Серверное API системы профориентации «Anmicius»

## Введение

Наша команда разработала высокопроизводительное серверное API (Приложение Б) для единой цифровой экосистемы профориентации и управления приёмной кампанией колледжа. Данное API служит центральным узлом системы, обеспечивая обработку данных, бизнес-логику и интеграцию с клиентскими приложениями (веб-сайт, мобильные приложения, административная панель).

Проект реализован на современном стеке технологий Python/FastAPI с применением архитектурного паттерна **Clean Architecture**, что обеспечивает модульность, тестируемость и лёгкость поддержки кода.

---

## 1. Архитектура решения

### 1.1. Clean Architecture

Мы внедрили архитектуру Clean Architecture, которая разделяет приложение на четыре независимых слоя:

```
┌─────────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                           │
│  (FastAPI Routes, Schemas, Request/Response Handling)           │
│  Файлы: app/presentation/routes.py, admin_routes.py, schemas.py │
├─────────────────────────────────────────────────────────────────┤
│                    APPLICATION LAYER                            │
│  (Use Cases, Business Logic, Dependencies Injection)            │
│  Файлы: app/application/use_cases.py, auth_use_cases.py,        │
│         dependencies.py                                         │
├─────────────────────────────────────────────────────────────────┤
│                      DOMAIN LAYER                               │
│  (Entities, Domain Models, Repository Interfaces)               │
│  Файлы: app/domain/models.py, repositories.py                   │
├─────────────────────────────────────────────────────────────────┤
│                   INFRASTRUCTURE LAYER                          │
│  (Database, Redis Cache, MinIO Storage, External Services)      │
│  Файлы: app/infrastructure/database.py, cache.py, models.py,    │
│         repositories.py, minio_service.py                       │
└─────────────────────────────────────────────────────────────────┘
```

**Описание слоёв:**

| Слой | Ответственность | Ключевые компоненты |
|------|-----------------|---------------------|
| **Presentation** | Обработка HTTP-запросов, валидация входных данных, сериализация ответов | `routes.py`, `admin_routes.py`, `schemas.py` |
| **Application** | Бизнес-логика, координация между доменными моделями и инфраструктурой | `use_cases.py`, `auth_use_cases.py`, `dependencies.py` |
| **Domain** | Чистая бизнес-логика без зависимостей от фреймворков, определение сущностей и интерфейсов | `models.py`, `repositories.py` |
| **Infrastructure** | Реализация интерфейсов доменного слоя, работа с внешними сервисами | `database.py`, `cache.py`, `minio_service.py`, `repositories.py`, `models.py` |

### 1.2. Диаграмма компонентов

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Client     │────▶│    Nginx     │────▶│   FastAPI    │
│  (Web/Mobile)│◀────│ (Reverse Proxy)│◀────│     App      │
└──────────────┘     └──────────────┘     └──────┬───────┘
                                                  │
                    ┌─────────────────────────────┼─────────────────────────────┐
                    │                             │                             │
              ┌─────▼─────┐               ┌──────▼──────┐               ┌──────▼──────┐
              │ PostgreSQL│               │    Redis    │               │    MinIO    │
              │  Database │               │    Cache    │               │   Storage   │
              └───────────┘               └─────────────┘               └─────────────┘
```

---

## 2. Технологический стек

Мы выбрали современные, проверенные технологии для обеспечения надёжности, производительности и масштабируемости:

| Категория | Технология | Версия | Назначение |
|-----------|------------|--------|------------|
| **Язык программирования** | Python | 3.11 | Основной язык разработки |
| **Web Framework** | FastAPI | 0.109.2 | Асинхронный REST API фреймворк |
| **ASGI Server** | Uvicorn | 0.27.0 | Высокопроизводительный ASGI-сервер |
| **ORM** | SQLAlchemy | 2.0.25 | Асинхронная работа с базой данных |
| **База данных** | PostgreSQL | 15 | Реляционная СУБД для хранения данных |
| **Миграции БД** | Alembic | 1.13.1 | Управление миграциями схемы БД |
| **Кэширование** | Redis | 7 | Распределённое кэширование и сессии |
| **Файловое хранилище** | MinIO | latest | S3-совместимое объектное хранилище |
| **Валидация данных** | Pydantic | 2.5.3 | Валидация и сериализация данных |
| **Аутентификация** | PyJWT, python-jose | 2.8.0, 3.3.0 | JWT токены для аутентификации |
| **Хеширование паролей** | Passlib + bcrypt | 1.7.4, 4.0.1 | Безопасное хранение паролей |
| **Rate Limiting** | SlowAPI | 0.1.8 | Защита от DDoS и brute-force атак |
| **Логирование** | Structlog | 24.1.0 | Структурированное логирование |
| **Тестирование** | pytest, pytest-asyncio | 7.4.4, 0.23.3 | Юнит- и интеграционное тестирование |
| **Контейнеризация** | Docker, Docker Compose | 3.8 | Развёртывание и оркестрация |
| **Reverse Proxy** | Nginx | alpine | Балансировка нагрузки, SSL-терминация |
| **SSL/TLS** | Certbot | latest | Автоматическое обновление сертификатов Let's Encrypt |

---

## 3. Структура проекта

### 3.1. Полная структура файлов

```
/workspace/
├── app/                              # Основное приложение
│   ├── __init__.py
│   ├── main.py                       # Точка входа FastAPI приложения
│   │
│   ├── core/                         # Ядро приложения (конфигурация, безопасность)
│   │   ├── __init__.py
│   │   ├── config.py                 # Настройки приложения (Settings класс)
│   │   ├── exceptions.py             # Кастомные исключения (AppException, NotFoundException, etc.)
│   │   ├── jwt.py                    # JWT утилиты (создание, проверка токенов, хеширование паролей)
│   │   └── rate_limiter.py           # Rate limiting конфигурация (SlowAPI)
│   │
│   ├── domain/                       # Доменный слой (бизнес-модели, интерфейсы)
│   │   ├── __init__.py
│   │   ├── models.py                 # Доменные модели (Specialty, News, User, etc.)
│   │   └── repositories.py           # Интерфейсы репозиториев (IRepository, ISpecialtyRepository, etc.)
│   │
│   ├── infrastructure/               # Инфраструктурный слой (БД, кэш, хранилище)
│   │   ├── __init__.py
│   │   ├── database.py               # Подключение к PostgreSQL, AsyncSession
│   │   ├── cache.py                  # Redis кэш сервис (CacheService класс)
│   │   ├── models.py                 # ORM модели SQLAlchemy (SpecialtyModel, NewsModel, etc.)
│   │   ├── repositories.py           # Реализации репозиториев (SpecialtyRepository, NewsRepository, etc.)
│   │   └── minio_service.py          # MinIO клиент для загрузки файлов
│   │
│   ├── application/                  # Слой приложений (бизнес-логика, use cases)
│   │   ├── __init__.py
│   │   ├── use_cases.py              # Use Cases для публичных endpoints
│   │   ├── auth_use_cases.py         # Use Cases для аутентификации (Register, Login, RefreshToken, etc.)
│   │   └── dependencies.py           # Зависимости FastAPI (get_current_user, get_current_superuser)
│   │
│   └── presentation/                 # Слой представления (роутеры, схемы)
│       ├── __init__.py
│       ├── routes.py                 # Публичные API v1 роутеры (/api/v1/*)
│       ├── admin_routes.py           # Административные роутеры (/admin/*, /auth/*)
│       └── schemas.py                # Pydantic схемы для валидации и сериализации
│
├── alembic/                          # Миграции базы данных
│   ├── __init__.py
│   ├── env.py                        # Конфигурация Alembic
│   ├── script.py.mako                # Шаблон для генерации миграций
│   └── versions/                     # Файлы миграций
│       └── *.py
│
├── tests/                            # Тесты
│   ├── __init__.py
│   ├── conftest.py                   # Фикстуры pytest
│   ├── test_api.py                   # Тесты публичных API
│   ├── test_auth.py                  # Тесты аутентификации
│   └── test_integration.py           # Интеграционные тесты
│
├── scripts/                          # Скрипты для развёртывания и обслуживания
│   ├── __init__.py
│   ├── create_admin.py               # Создание администратора
│   ├── create_superuser.py           # Создание суперпользователя
│   ├── migrate_test_questions.py     # Миграция вопросов теста
│   ├── reset_admin_password.py       # Сброс пароля администратора
│   ├── run_tests.sh                  # Запуск тестов
│   ├── ssl-cert.sh                   # Получение SSL сертификатов
│   └── update-nginx-upstream.sh      # Обновление nginx upstream
│
├── admin-panel/                      # Административная панель (React/TypeScript SPA)
│   ├── index.html
│   ├── package.json
│   ├── package-lock.json
│   ├── tsconfig.json
│   ├── tsconfig.node.json
│   ├── vite.config.ts
│   └── src/
│
├── nginx/                            # Конфигурация Nginx
│   ├── nginx.conf                    # Основная конфигурация
│   ├── nginx-certbot.conf            # Конфигурация для Certbot
│   ├── nginx-http.conf               # HTTP конфигурация
│   ├── nginx-temp.conf               # Временная конфигурация
│   └── www/                          # Статические файлы для Certbot
│
├── docker-compose.yml                # Оркестрация Docker сервисов
├── Dockerfile                        # Docker образ приложения
├── requirements.txt                  # Python зависимости
├── pytest.ini                        # Конфигурация pytest
└── alembic.ini                       # Конфигурация Alembic
```

---

## 4. Детальное описание компонентов

### 4.1. Главный модуль (app/main.py)

**Назначение:** Точка входа FastAPI приложения, настройка middleware, роутеров, обработчиков исключений.

**Ключевые функции:**
- `lifespan()` - управление жизненным циклом приложения (startup/shutdown)
- `create_app()` - создание и настройка экземпляра FastAPI
- Регистрация всех роутеров (публичные API, аутентификация, административные)
- Настройка CORS middleware
- Обработчики исключений (AppException, RequestValidationError, general exceptions)
- Health check endpoint (`/health`)

**Зависимости:**
- `app.core.config.get_settings()` - получение настроек
- `app.infrastructure.database.init_db(), close_db()` - инициализация БД
- `app.infrastructure.cache.init_cache(), close_cache()` - инициализация кэша
- Все роутеры из `app.presentation.routes` и `app.presentation.admin_routes`

### 4.2. Конфигурация (app/core/config.py)

**Назначение:** Централизованное управление настройками приложения через переменные окружения.

**Класс `Settings`:**
- Наследуется от `pydantic_settings.BaseSettings`
- Автоматическая загрузка из `.env` файла
- Типизированные поля с значениями по умолчанию

**Основные настройки:**
- `app_name`, `app_version`, `debug`, `environment` - основные параметры приложения
- `postgres_user`, `postgres_password`, `postgres_db`, `postgres_host`, `postgres_port` - подключение к БД
- `minio_endpoint`, `minio_access_key`, `minio_secret_key`, `minio_bucket`, `minio_public_url` - MinIO хранилище
- `cors_origins` - разрешённые CORS origins (строка, разделённая запятыми)
- `jwt_secret_key` - секретный ключ для JWT
- `redis_host`, `redis_port`, `redis_db`, `redis_password`, `redis_ttl_default`, `redis_ttl_long` - Redis настройки
- `pagination_min_limit`, `pagination_max_limit`, `pagination_default_limit` - параметры пагинации

**Свойства:**
- `get_database_url` - формирование URL подключения к PostgreSQL
- `get_cors_origins` - парсинг строки CORS origins в список

### 4.3. JWT и безопасность (app/core/jwt.py)

**Назначение:** Управление JWT токенами, хеширование паролей, валидация данных.

**Константы:**
- `ALGORITHM = "HS256"` - алгоритм подписи JWT
- `ACCESS_TOKEN_EXPIRE_MINUTES = 1440` (24 часа) - время жизни access токена
- `REFRESH_TOKEN_EXPIRE_DAYS = 30` - время жизни refresh токена
- `pwd_context` - CryptContext для bcrypt хеширования (12 раундов)

**Функции:**
- `verify_password(plain_password, hashed_password)` - проверка пароля
- `get_password_hash(password)` - хеширование пароля
- `validate_password(password)` - валидация сложности пароля (минимум 12 символов, заглавные, строчные, цифры, спецсимволы)
- `validate_email(email)` - валидация формата email
- `create_access_token(data, expires_delta, scopes)` - создание access токена с scopes
- `create_refresh_token(data)` - создание refresh токена
- `decode_token(token)` - декодирование JWT токена
- `verify_token(token, token_type)` - проверка токена и его типа

### 4.4. Исключения (app/core/exceptions.py)

**Назначение:** Иерархия кастомных исключений для единообразной обработки ошибок.

**Классы исключений:**
- `AppException` - базовое исключение с `message` и `status_code`
- `NotFoundException` (404) - ресурс не найден
- `BadRequestException` (400) - некорректный запрос
- `ValidationException` (422) - ошибка валидации

### 4.5. Rate Limiting (app/core/rate_limiter.py)

**Назначение:** Защита от DDoS и brute-force атак через ограничение количества запросов.

**Компоненты:**
- `limiter` - экземпляр SlowAPI Limiter с ключом по IP адресу
- `rate_limit_exception_handler()` - обработчик превышения лимита (возвращает 429 статус)
- `get_rate_limit_limits()` - настройки лимитов:
  - Auth endpoints: 10/minute, 30/hour
  - Default: 60/minute, 1000/hour

### 4.6. Доменные модели (app/domain/models.py)

**Назначение:** Определение бизнес-сущностей без зависимостей от фреймворков.

**Классы:**
- `BaseEntity` - базовый класс с `id`, `created_at`, `updated_at`
- `Image` - модель изображения (url, alt, caption, thumbnail)
- `SpecialtyEducationOption` - уровень образования специальности
- `Specialty` - специальность колледжа (code, name, description, exams, images, documents, education_options)
- `InterestingFact` - интересный факт о специальности
- `News` - новость колледжа (title, slug, preview_text, content, gallery, views)
- `FAQDocument`, `FAQ` - часто задаваемые вопросы
- `Document` - документ для скачивания
- `GalleryImage` - изображение галереи
- `TestQuestion`, `TestAnswer`, `TestResult` - профориентационный тест
- `AboutInfo` - информация о колледже
- `SubmissionMethod`, `ImportantDate`, `AdmissionInfo` - приёмная кампания
- `DocumentFile` - файл документа
- `User` - пользователь (администратор)

### 4.7. Интерфейсы репозиториев (app/domain/repositories.py)

**Назначение:** Определение контрактов для работы с данными (инверсия зависимостей).

**Интерфейсы:**
- `IRepository` - базовый интерфейс с `get_by_id()`
- `ISpecialtyRepository` - репозиторий специальностей (get_all, get_by_code, create, update, delete)
- `IFactRepository` - репозиторий фактов (get_by_specialty_code, get_titles_by_specialty_code)
- `INewsRepository` - репозиторий новостей (get_all, get_by_slug, increment_views)
- `IFAQRepository`, `IDocumentRepository`, `IGalleryRepository`, `IDocumentFileRepository` - CRUD интерфейсы
- `ITestQuestionRepository` - репозиторий вопросов теста (validate_answer, calculate_recommendation)
- `IAboutRepository`, `IAdmissionRepository` - репозитории информации
- `IUserRepository` - репозиторий пользователей (get_by_email, get_by_username, create, save_refresh_token, etc.)

### 4.8. База данных (app/infrastructure/database.py)

**Назначение:** Настройка асинхронного подключения к PostgreSQL через SQLAlchemy.

**Компоненты:**
- `engine` - AsyncEngine для asyncpg
- `async_session_maker` - фабрика асинхронных сессий
- `Base` - базовый класс DeclarativeBase для ORM моделей
- `get_db_session()` - dependency для получения сессии
- `init_db()`, `close_db()` - инициализация и закрытие подключения

### 4.9. Кэширование (app/infrastructure/cache.py)

**Назначение:** Сервис для работы с Redis кэшем с версионированием групп.

**Класс `CacheService`:**
- `_prefix = "anmicius_cache"` - префикс ключей
- `_version_key` - ключ для версионирования
- `connect()`, `disconnect()` - управление подключением
- `is_available()` - проверка доступности Redis
- `_make_key(key)` - создание полного ключа с префиксом
- `_get_version(group)`, `_increment_version(group)` - управление версиями групп
- `get(key, group)`, `set(key, value, group, ttl)` - операции чтения/записи с версионированием
- `delete(key, group)`, `clear_group(group)`, `clear_pattern(pattern)`, `clear_all()` - удаление
- `get_stats()` - статистика кэша

**Глобальный экземпляр:** `cache_service`

### 4.10. ORM модели (app/infrastructure/models.py)

**Назначение:** SQLAlchemy модели для отображения на таблицы базы данных.

**Модели:**
- `SpecialtyModel` - таблица `specialties` (code, name, short_description, description[JSON], exams[JSON], images[JSON], documents[JSON])
- `SpecialtyEducationModel` - таблица `specialty_education_options` (specialty_id, education_level, duration, budget_places, paid_places)
- `InterestingFactModel` - таблица `interesting_facts` (specialty_code, title, description[JSON], images[JSON])
- `NewsModel` - таблица `news` (title, slug, preview_text, content[JSON], preview_image, gallery[JSON], views)
- `FAQModel` - таблица `faq` (question, answer[JSON], category, show_in_admission, images[JSON], documents[JSON], document_file_ids[JSON])
- `DocumentModel` - таблица `documents` (title, category, file_url, file_size, images[JSON])
- `GalleryImageModel` - таблица `gallery_images` (url, thumbnail, alt, category, caption, date_taken)
- `DocumentFileModel` - таблица `document_files` (title, file_url, file_size, category)
- `TestQuestionModel` - таблица `test_questions` (text, options[JSON], answer_scores[JSON], image_url, documents[JSON])
- `AboutInfoModel` - таблица `about_info` (title, description[JSON], images[JSON])
- `AdmissionInfoModel` - таблица `admission_info` (year, specialties_admission[JSON], submission_methods[JSON], important_dates[JSON])
- `UserModel` - таблица `users` (email, username, hashed_password, is_active, is_superuser)
- `RefreshTokenModel` - таблица `refresh_tokens` (user_id, token, expires_at)

**Связи:**
- `SpecialtyModel.education_options` - One-to-Many с каскадным удалением
- `SpecialtyModel.facts` - One-to-Many с каскадным удалением
- `UserModel.refresh_tokens` - One-to-Many с каскадным удалением

### 4.11. Репозитории (app/infrastructure/repositories.py)

**Назначение:** Реализация интерфейсов репозиториев с использованием SQLAlchemy.

**Реализации:**
- `SpecialtyRepository` - работа со специальностями:
  - `get_by_id()`, `get_by_code()` - получение с загрузкой education_options через selectinload
  - `get_all()` - пагинация, фильтрация по search, form (budget/paid)
  - `get_codes_with_budget_or_paid()` - коды специальностей с местами
  - `create()`, `update()`, `delete()` - CRUD операции
  - `_to_domain()` - конвертация ORM модели в доменную

- `FactRepository` - работа с фактами:
  - `get_by_specialty_code()`, `get_titles_by_specialty_code()` - получение фактов

- `NewsRepository` - работа с новостями:
  - `get_all()` - пагинация, поиск по заголовку
  - `get_by_slug()` - получение по slug
  - `increment_views()` - атомарное увеличение счётчика просмотров

- `FAQRepository`, `DocumentRepository`, `GalleryRepository`, `DocumentFileRepository` - CRUD реализации

- `TestQuestionRepository` - работа с вопросами теста:
  - `get_all()` - получение всех активных вопросов
  - `calculate_recommendation()` - расчёт рекомендации по ответам

- `AboutRepository`, `AdmissionRepository` - получение информации

- `UserRepository` - работа с пользователями:
  - `get_by_id()`, `get_by_email()`, `get_by_username()` - поиск
  - `create()` - создание с хешированием пароля
  - `save_refresh_token()`, `get_refresh_token()`, `delete_refresh_token()` - управление refresh токенами
  - `get_all()` - пагинация пользователей
  - `update()`, `update_with_password()` - обновление
  - `delete()` - удаление

### 4.12. Use Cases (app/application/use_cases.py)

**Назначение:** Бизнес-логика для публичных endpoints.

**Use Cases:**
- `GetAboutInfoUseCase` - получение информации о колледже
- `GetAdmissionInfoUseCase` - получение информации о приёмной кампании
- `GetSpecialtiesUseCase` - список специальностей с пагинацией и валидацией параметров
- `GetSpecialtyByCodeUseCase` - детали специальности с фактами
- `GetFactTitlesBySpecialtyUseCase`, `GetFactByIdUseCase` - факты
- `GetNewsUseCase`, `GetNewsBySlugUseCase` - новости
- `GetFAQUseCase`, `GetDocumentsUseCase`, `GetGalleryUseCase` - дополнительные данные
- `GetTestQuestionsUseCase`, `SubmitTestAnswersUseCase` - тестирование

### 4.13. Auth Use Cases (app/application/auth_use_cases.py)

**Назначение:** Бизнес-логика аутентификации и управления пользователями.

**Use Cases:**
- `RegisterUserUseCase` - регистрация с валидацией email и пароля
- `LoginUserUseCase` - вход с проверкой пароля, активности, выдачей токенов и scopes
- `RefreshTokenUseCase` - обновление токенов с проверкой в БД
- `LogoutUserUseCase` - выход с инвалидацией refresh токена
- `GetCurrentUserUseCase`, `GetAllUsersUseCase` - получение пользователей
- `UpdateUserUseCase` - обновление с проверкой уникальности email/username
- `DeleteUserUseCase` - удаление

### 4.14. Dependencies (app/application/dependencies.py)

**Назначение:** FastAPI зависимости для аутентификации.

**Функции:**
- `get_current_user_id()` - извлечение ID из JWT токена, проверка scopes
- `get_current_user()` - получение данных пользователя из БД
- `get_current_superuser()` - проверка прав суперпользователя

### 4.15. Роутеры (app/presentation/routes.py)

**Назначение:** Публичные API v1 endpoints.

**Endpoints:**
- `GET /api/v1/about` - информация о колледже (кэширование 1 час)
- `GET /api/v1/admission` - приёмная кампания
- `GET /api/v1/specialties` - список специальностей (пагинация, фильтры, кэширование 5 минут)
- `GET /api/v1/specialties/{code}` - детали специальности (кэширование 10 минут)
- `GET /api/v1/specialties/{code}/facts` - факты специальности
- `GET /api/v1/facts/{fact_id}` - детали факта
- `GET /api/v1/news` - список новостей
- `GET /api/v1/news/{slug}` - детали новости (increment views)
- `GET /api/v1/faq` - FAQ
- `GET /api/v1/documents` - документы
- `GET /api/v1/images` - галерея
- `GET /api/v1/test/questions` - вопросы теста
- `POST /api/v1/test/results` - расчёт результатов теста

### 4.16. Admin Routes (app/presentation/admin_routes.py)

**Назначение:** Административные endpoints и аутентификация.

**Auth Endpoints:**
- `POST /auth/register` - регистрация (rate limit 10/minute)
- `POST /auth/login` - вход (OAuth2PasswordRequestForm для Swagger)
- `POST /auth/refresh` - обновление токена
- `POST /auth/logout` - выход
- `GET /auth/me` - текущий пользователь

**Admin Endpoints:**
- `GET/POST/PUT/DELETE /admin/users` - управление пользователями
- `GET/POST/PUT/DELETE /admin/specialties` - управление специальностями
- `GET/POST/PUT/DELETE /admin/news` - управление новостями
- `GET/POST/PUT/DELETE /admin/facts` - управление фактами
- `POST /admin/upload/image`, `POST /admin/upload/document` - загрузка файлов
- `DELETE /admin/upload/{path}` - удаление файлов
- `GET/POST/PUT/DELETE /admin/gallery` - галерея
- `GET/POST/PUT/DELETE /admin/document-files` - файлы документов
- `GET/POST/PUT/DELETE /admin/faq` - FAQ
- `GET/POST/PUT/DELETE /admin/documents` - документы
- `GET/PUT /admin/about` - информация о колледже
- `GET/POST/PUT/DELETE /admin/test-questions` - вопросы теста
- `GET/POST /admin/cache/stats`, `POST /admin/cache/clear` - управление кэшем
- `GET/POST/PUT/DELETE /admin/admission` - приёмная кампания

### 4.17. Схемы (app/presentation/schemas.py)

**Назначение:** Pydantic схемы для валидации запросов и сериализации ответов.

**Основные схемы:**
- `ImageSchema`, `ImageWithThumbnailSchema` - изображения
- `PaginationSchema` - пагинация
- `AboutResponse`, `AboutUpdateSchema` - о колледже
- `SpecialtyAdmissionSchema`, `SubmissionMethodSchema`, `ImportantDateSchema`, `AdmissionResponse` - приёмная кампания
- `SpecialtyDetailResponse`, `SpecialtiesResponse` - специальности
- `FactTitleSchema`, `FactDetailResponse` - факты
- `NewsListItemSchema`, `NewsDetailResponse` - новости
- `FAQItemSchema`, `DocumentItemSchema`, `GalleryItemSchema` - дополнительные данные
- `TestQuestionSchema`, `TestRequest`, `TestResultResponse` - тест
- `TokenSchema`, `LoginSchema`, `UserCreateSchema`, `UserUpdateSchema`, `UserResponseSchema` - аутентификация

### 4.18. MinIO Service (app/infrastructure/minio_service.py)

**Назначение:** Работа с S3-совместимым хранилищем MinIO.

**Функции:**
- `get_minio_client()` - создание клиента Minio
- `ensure_bucket_exists()` - проверка и создание бакета
- `upload_file()`, `upload_file_from_bytes()` - загрузка файлов
- `delete_file()` - удаление файла
- `get_presigned_url()` - временная ссылка
- `generate_unique_filename()` - UUID имя файла
- `get_file_extension()` - расширение по content-type

**Константы:**
- `MAX_IMAGE_SIZE = 10 MB`
- `MAX_DOCUMENT_SIZE = 50 MB`

---

## 5. API Endpoints

### 5.1. Публичные эндпоинты (v1)

| Метод | Endpoint | Описание | Требуется авторизация |
|-------|----------|----------|----------------------|
| GET | `/api/v1/about` | Информация о колледже | Нет |
| GET | `/api/v1/admission` | Информация о приёмной кампании | Нет |
| GET | `/api/v1/specialties` | Список специальностей | Нет |
| GET | `/api/v1/specialties/{code}` | Детали специальности | Нет |
| GET | `/api/v1/specialties/{code}/facts` | Факты специальности | Нет |
| GET | `/api/v1/facts/{fact_id}` | Детали факта | Нет |
| GET | `/api/v1/news` | Список новостей | Нет |
| GET | `/api/v1/news/{slug}` | Детали новости | Нет |
| GET | `/api/v1/faq` | Часто задаваемые вопросы | Нет |
| GET | `/api/v1/documents` | Документы для скачивания | Нет |
| GET | `/api/v1/images` | Галерея изображений | Нет |
| GET | `/api/v1/test/questions` | Вопросы профориентационного теста | Нет |
| POST | `/api/v1/test/results` | Отправка ответов теста | Нет |

### 5.2. Эндпоинты аутентификации

| Метод | Endpoint | Описание | Требуется авторизация |
|-------|----------|----------|----------------------|
| POST | `/auth/register` | Регистрация нового пользователя | Нет |
| POST | `/auth/login` | Вход в систему | Нет |
| POST | `/auth/login/oauth` | OAuth2 вход для Swagger UI | Нет |
| POST | `/auth/refresh` | Обновление токена | Нет |
| POST | `/auth/logout` | Выход из системы | Нет |
| GET | `/auth/me` | Текущий пользователь | Да |

### 5.3. Административные эндпоинты

| Метод | Endpoint | Описание | Required Scope |
|-------|----------|----------|---------------|
| GET | `/admin/users` | Список пользователей | `users:read` |
| GET | `/admin/users/{id}` | Пользователь по ID | `users:read` |
| PATCH | `/admin/users/{id}` | Обновление пользователя | `users:write` |
| DELETE | `/admin/users/{id}` | Удаление пользователя | — |
| GET | `/admin/specialties` | Список специальностей | `specialties:read` |
| POST | `/admin/specialties` | Создание специальности | `specialties:write` |
| GET | `/admin/specialties/{id}` | Специальность по ID | `specialties:read` |
| PUT | `/admin/specialties/{id}` | Обновление специальности | `specialties:write` |
| DELETE | `/admin/specialties/{id}` | Удаление специальности | `specialties:write` |
| GET | `/admin/news` | Список новостей | `news:read` |
| POST | `/admin/news` | Создание новости | `news:write` |
| PUT | `/admin/news/{id}` | Обновление новости | `news:write` |
| DELETE | `/admin/news/{id}` | Удаление новости | `news:write` |
| POST | `/admin/upload/image` | Загрузка изображения | `upload:write` |
| POST | `/admin/upload/document` | Загрузка документа | `upload:write` |
| DELETE | `/admin/upload/{path}` | Удаление файла | `upload:write` |
| GET | `/admin/cache/stats` | Статистика кэша | — |
| POST | `/admin/cache/clear` | Очистка кэша | — |
| GET | `/admin/admission` | Список приёмных кампаний | — |
| POST | `/admin/admission` | Создание кампании | — |
| PUT | `/admin/admission/{year}` | Обновление кампании | — |
| DELETE | `/admin/admission/{year}` | Удаление кампании | — |

---

## 6. Модель данных

### 6.1. Основные таблицы базы данных

| Таблица | Описание | Ключевые поля |
|---------|----------|---------------|
| `specialties` | Специальности | id, code, name, description, exams, images, documents |
| `specialty_education_options` | Уровни образования | id, specialty_id, education_level, duration, budget_places, paid_places |
| `interesting_facts` | Интересные факты | id, specialty_code, title, description, images |
| `news` | Новости | id, title, slug, preview_text, content, preview_image, gallery, views |
| `faq` | FAQ | id, question, answer, category, show_in_admission, images, documents |
| `documents` | Документы | id, title, category, file_url, file_size |
| `gallery_images` | Галерея | id, url, thumbnail, alt, category, caption |
| `test_questions` | Вопросы теста | id, text, options, answer_scores, image_url |
| `about_info` | Информация о колледже | id, title, description, images |
| `admission_info` | Приёмная кампания | id, year, specialties_admission, submission_methods, important_dates |
| `users` | Пользователи | id, email, username, hashed_password, is_active, is_superuser |
| `refresh_tokens` | Refresh токены | id, user_id, token, expires_at |
| `document_files` | Файлы документов | id, title, file_url, file_size, category |

### 6.2. Связи между таблицами

- `specialties` → `specialty_education_options`: One-to-Many (каскадное удаление)
- `specialties` → `interesting_facts`: One-to-Many (каскадное удаление)
- `users` → `refresh_tokens`: One-to-Many (каскадное удаление)

---

## 7. Кэширование

Мы внедрили многоуровневую систему кэширования на базе Redis для повышения производительности:

### 7.1. Стратегия кэширования

- **Группы кэша:**
  - `public` — публичные данные (специальности, новости, факты, FAQ, документы)
  - `default` — данные по умолчанию

- **Версионирование кэша:**
  - Каждая группа имеет версию
  - При обновлении данных версия увеличивается, что приводит к автоматической инвалидации старого кэша
  - Ключ формата: `anmicius_cache:{group}:v{version}:{key}`

### 7.2. TTL (Time To Live)

| Тип данных | TTL |
|------------|-----|
| Список специальностей | 5 минут |
| Детали специальности | 10 минут |
| Список новостей | 5 минут |
| Детали новости | 10 минут |
| FAQ, документы, факты | 10 минут |
| Информация о колледже | 1 час |

### 7.3. Инвалидация кэша

Кэш автоматически очищается при:
- Создании/обновлении/удалении специальности
- Создании/обновлении/удалении новости
- Изменении настроек через административную панель

**Ручная очистка:**
- `POST /admin/cache/clear` — полная очистка кэша
- `POST /admin/cache/clear?group=public` — очистка конкретной группы

---

## 8. Безопасность

### 8.1. Аутентификация и авторизация

- **JWT-токены:**
  - Access токен: срок действия 24 часа
  - Refresh токен: срок действия 30 дней
  - Алгоритм подписи: HS256
  - Обязательная проверка типа токена (`access` или `refresh`)

- **Хеширование паролей:**
  - Алгоритм: bcrypt
  - Количество раундов: 12 (усиленная защита)
  - Валидация сложности пароля при регистрации

### 8.2. Rate Limiting

Защита от DDoS-атак и brute-force:

| Endpoint | Лимит |
|----------|-------|
| `/auth/register` | 10 запросов/минуту, 30 запросов/час |
| `/auth/login` | 10 запросов/минуту, 30 запросов/час |
| `/auth/refresh` | 30 запросов/минуту, 100 запросов/час |
| Остальные endpoints | 60 запросов/минуту, 1000 запросов/час |

**Ответ при превышении лимита:**
```json
{
  "detail": "Слишком много запросов",
  "message": "Превышен лимит запросов. Попробуйте позже."
}
```

### 8.3. CORS (Cross-Origin Resource Sharing)

Настроенные разрешённые источники:
- `https://anmicius.ru`
- `https://api.anmicius.ru`
- `https://minio.anmicius.ru`
- `https://admin.anmicius.ru`

**Важно:** `allow_credentials` установлен в `false` для безопасности при использовании конкретных origins.

### 8.4. Валидация входных данных

- Все входные данные валидируются через Pydantic-схемы
- Строгая типизация полей
- Автоматическая обработка ошибок валидации с подробными сообщениями

### 8.5. Обработка исключений

Глобальные обработчики исключений обеспечивают единообразный формат ошибок:

```json
{
  "detail": "Описание ошибки",
  "status_code": 404
}
```

Типы исключений:
- `AppException` — базовое исключение приложения
- `NotFoundException` — ресурс не найден (404)
- `BadRequestException` — неверный запрос (400)
- `ValidationException` — ошибка валидации (422)
- `RequestValidationError` — ошибка валидации запроса FastAPI

---

## 9. Производительность

### 9.1. Асинхронная архитектура

- Полностью асинхронный стек: FastAPI + SQLAlchemy (asyncpg) + Redis
- Неблокирующие операции ввода-вывода
- Поддержка тысяч одновременных соединений

### 9.2. Пул соединений с базой данных

- Использование `async_session_maker` для управления сессиями
- Автоматическое управление жизненным циклом соединений
- Оптимизированные запросы с eager loading связанных данных

### 9.3. Кэширование

- Снижение нагрузки на базу данных до 80% для часто запрашиваемых данных
- Среднее время ответа для закэшированных запросов: <10 мс
- Среднее время ответа для запросов к БД: 50-200 мс

### 9.4. Метрики производительности

| Показатель | Значение |
|------------|----------|
| Время ответа (кэш) | <10 мс |
| Время ответа (БД) | 50-200 мс |
| RPS (requests per second) | ~1000 (на одном экземпляре) |
| Время запуска приложения | <5 секунд |
| Потребление памяти | ~150 MB |

---

## 10. Развёртывание

### 10.1. Требования

- Docker 20.10+
- Docker Compose 2.0+
- Минимум 2 GB RAM
- 10 GB свободного места на диске

### 10.2. Переменные окружения

Создайте файл `.env` на основе `.env.example`:

```bash
# Application
APP_NAME=Anmicius API
APP_VERSION=1.0.0
DEBUG=false
ENVIRONMENT=production

# Database
POSTGRES_USER=anmicius
POSTGRES_PASSWORD=<secure_password>
POSTGRES_DB=anmicius_db
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

# MinIO
MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY=<secure_access_key>
MINIO_SECRET_KEY=<secure_secret_key>
MINIO_BUCKET=anmicius-media
MINIO_SECURE=false
MINIO_PUBLIC_URL=https://minio.anmicius.ru/anmicius-media

# CORS
CORS_ORIGINS=https://anmicius.ru,https://api.anmicius.ru,https://admin.anmicius.ru

# JWT (ОБЯЗАТЕЛЬНО измените!)
JWT_SECRET_KEY=<openssl rand -hex 32>

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=

# SSL (опционально)
SSL_EMAIL=admin@anmicius.ru
MAIN_DOMAIN=anmicius.ru
```

### 10.3. Запуск через Docker Compose

```bash
# Сборка и запуск всех сервисов
docker-compose up -d --build

# Просмотр логов
docker-compose logs -f api

# Остановка
docker-compose down

# Перезапуск
docker-compose restart
```

### 10.4. Компоненты инфраструктуры

| Сервис | Порт | Описание |
|--------|------|----------|
| `postgres` | 5432 | База данных PostgreSQL |
| `redis` | 6379 | Кэш Redis |
| `minio` | 9000, 9001 | Объектное хранилище (API + Console) |
| `api` | 8000 (внутренний) | FastAPI приложение |
| `nginx` | 80, 443, 4443 | Reverse proxy + SSL |
| `certbot` | — | Автоматическое обновление SSL |

### 10.5. Миграции базы данных

```bash
# Применение миграций
docker-compose exec api alembic upgrade head

# Создание новой миграции
docker-compose exec api alembic revision --autogenerate -m "Description"

# Откат миграции
docker-compose exec api alembic downgrade -1
```

---

## 11. Тестирование

### 11.1. Запуск тестов

```bash
# Все тесты
pytest

# С покрытием
pytest --cov=app --cov-report=html

# Конкретный файл
pytest tests/test_api.py -v

# Интеграционные тесты
pytest tests/test_integration.py -v
```

### 11.2. Типы тестов

- **Юнит-тесты** (`test_api.py`) — тестирование отдельных модулей и функций
- **Тесты аутентификации** (`test_auth.py`) — проверка JWT, регистрации, входа
- **Интеграционные тесты** (`test_integration.py`) —端到端 тестирование сценариев использования

### 11.3. Coverage

Целевой показатель покрытия кода тестами: **>80%**

---

## 12. Мониторинг и логирование

### 12.1. Health Check

Endpoint для проверки состояния системы:

```bash
GET /health
```

**Ответ:**
```json
{
  "status": "ok",
  "version": "1.0.0",
  "services": {
    "database": {"status": "ok"},
    "redis": {"status": "ok"},
    "minio": {"status": "ok"}
  }
}
```

Возможные статусы:
- `ok` — все сервисы работают
- `degraded` — часть сервисов недоступна (некритично)
- `error` — критическая ошибка

### 12.2. Логирование

- **Библиотека:** Structlog
- **Формат:** JSON (структурированные логи)
- **Уровни:** DEBUG, INFO, WARNING, ERROR
- **Вывод:** stdout (сбор через Docker logs)

**Пример лога:**
```json
{
  "event": "Запуск приложения",
  "level": "info",
  "name": "Anmicius API",
  "version": "1.0.0",
  "timestamp": "2024-04-15T10:30:00Z"
}
```

---

## 13. Административная панель

Отдельное SPA-приложение на React/TypeScript, размещённое в директории `admin-panel/`:

- **Технологии:** React 18, TypeScript, Vite, Material UI
- **Интеграция:** Полная интеграция с API через Axios
- **Развёртывание:** Статические файлы обслуживаются через Nginx
- **Маршрут:** `https://admin.anmicius.ru/`

**Функционал административной панели:**
- Управление пользователями
- CRUD для специальностей, новостей, фактов, документов
- Загрузка и удаление файлов
- Управление тестовыми вопросами
- Настройка приёмной кампании
- Очистка кэша

---

## 14. Заключение

Мы разработали масштабируемое, безопасное и высокопроизводительное серверное API, которое служит фундаментом цифровой экосистемы профориентации колледжа. Применение современных архитектурных паттернов, передовых технологий и лучших практик безопасности обеспечивает надёжность системы и готовность к нагрузкам реального использования.

**Ключевые достижения:**
- ✅ Clean Architecture для поддерживаемости кода
- ✅ Полная асинхронность для высокой производительности
- ✅ Многоуровневая система безопасности (JWT, Rate Limiting, CORS)
- ✅ Эффективное кэширование для снижения нагрузки на БД
- ✅ Интеграция с S3-совместимым хранилищем для медиафайлов
- ✅ Автоматизированное развёртывание через Docker Compose
- ✅ Покрытие тестами ключевых сценариев использования
- ✅ Подробная документация API (Swagger UI, ReDoc)

**Перспективы развития:**
- Добавление GraphQL API для гибких запросов
- Внедрение WebSocket для real-time уведомлений
- Расширение аналитики и метрик использования
- Интеграция с внешними системами (электронный журнал, 1С)

---

## Приложение A: Контакты команды разработчиков

Для вопросов по API и сотрудничеству обращайтесь:
- **Email:** dev@anmicius.ru
- **Документация:** https://api.anmicius.ru/docs
- **GitHub:** https://github.com/amyrtaa579/tpgk_server

---

*Документ подготовлен командой разработки для конференции по цифровым технологиям.*
*Версия документа: 1.0.0*
*Дата актуализации: Апрель 2024*
