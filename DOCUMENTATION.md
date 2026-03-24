# Anmicius API — Техническая документация

## Содержание

1. [Обзор](#обзор)
2. [Архитектура](#архитектура)
3. [Быстрый старт](#быстрый-старт)
4. [API Reference](#api-reference)
   - [Health Check](#health-check)
   - [Публичные endpoints](#публичные-endpoints)
   - [Аутентификация](#аутентификация)
   - [Админ-панель](#админ-панель)
5. [Модели данных](#модели-данных)
6. [База данных](#база-данных)
7. [Загрузка файлов](#загрузка-файлов)
8. [Безопасность](#безопасность)
9. [Тестирование](#тестирование)
10. [Развёртывание](#развёртывание)

---

## Обзор

**Anmicius API** — REST API для колледжа Anmicius, реализованное на **FastAPI** с использованием **PostgreSQL** и **MinIO**.

### Основная информация

- **Базовый URL**: `https://api.anmicius.ru`
- **Версия API**: v1
- **Документация Swagger**: `/docs`
- **Документация ReDoc**: `/redoc`

### Технологии

| Компонент | Технология |
|-----------|------------|
| Фреймворк | FastAPI 0.109.2 |
| База данных | PostgreSQL 15+ |
| ORM | SQLAlchemy 2.0.25 |
| Валидация | Pydantic 2.5.3 |
| Хранилище файлов | MinIO 7.2.0 |
| Аутентификация | JWT (PyJWT 2.8.0) |
| Миграции | Alembic 1.13.1 |

---

## Архитектура

Проект использует **чистую архитектуру (Clean Architecture)** с разделением на слои:

```
app/
├── core/           # Конфигурация, JWT, исключения, утилиты
├── domain/         # Бизнес-модели и интерфейсы репозиториев
├── application/    # Use Cases (бизнес-логика)
├── infrastructure/ # Реализации репозиториев, ORM модели, БД, MinIO
└── presentation/   # API роутеры и Pydantic схемы
```

### Слои

| Слой | Описание | Зависимости |
|------|----------|-------------|
| **Domain** | Бизнес-модели и интерфейсы | Нет |
| **Application** | Use Cases, бизнес-правила | Domain |
| **Infrastructure** | Репозитории, ORM, внешние сервисы | Domain, Application |
| **Presentation** | HTTP API (FastAPI роуты) | Application, Infrastructure |

### Поток запроса

```
HTTP Request → Router → Use Case → Repository → Database
                ↓
            Response ← Serializer ← Domain Model ← Repository
```

---

## Быстрый старт

### Требования

- Docker и Docker Compose **ИЛИ** Python 3.11+
- PostgreSQL 15+
- MinIO (опционально)

### Запуск через Docker

```bash
# Клонирование репозитория
cd anmicius-api

# Создание .env файла
cp .env.example .env

# Запуск контейнеров
docker-compose up -d

# Применение миграций
docker-compose exec api alembic upgrade head
```

API доступен по адресу: `http://localhost:8000`

### Локальная разработка

```bash
# Установка зависимостей
pip install -r requirements.txt

# Создание .env файла
cp .env.example .env

# Запуск БД и MinIO (через Docker)
docker-compose up -d postgres minio minio-init

# Применение миграций
alembic upgrade head

# Запуск сервера разработки
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## API Reference

### Health Check

#### GET `/`

Информация о сервисе.

**Ответ (200 OK):**
```json
{
  "name": "Anmicius API",
  "version": "1.0.0",
  "docs": "/docs"
}
```

#### GET `/health`

Проверка статуса API.

**Ответ (200 OK):**
```json
{
  "status": "ok",
  "version": "1.0.0"
}
```

---

### Публичные endpoints

Все публичные endpoints находятся под префиксом `/api/v1` и **не требуют аутентификации**.

#### Информация о колледже

##### GET `/api/v1/about`

Получение общей информации о колледже.

**Параметры:** Нет

**Ответ (200 OK):**
```json
{
  "title": "Колледж Anmicius",
  "description": [
    "Описание 1",
    "Описание 2"
  ],
  "images": [
    {
      "url": "https://minio.anmicius.ru/images/about/img.jpg",
      "alt": "Колледж",
      "caption": "Главное здание"
    }
  ]
}
```

##### GET `/api/v1/admission`

Получение информации о приёмной кампании.

**Параметры:**
| Параметр | Тип | Обязательный | Описание |
|----------|-----|--------------|----------|
| `year` | int | Нет | Год поступления (по умолчанию текущий) |

**Ответ (200 OK):**
```json
{
  "year": 2025,
  "specialties_admission": [
    {
      "code": "15.02.19",
      "name": "Сварочное производство",
      "budget_places": 25,
      "paid_places": 15,
      "exams": ["Математика", "Русский язык", "Физика"],
      "duration": "3 г. 10 мес."
    }
  ],
  "submission_methods": [
    {
      "title": "Онлайн",
      "description": "Подача через сайт",
      "link": "https://anmicius.ru/admission"
    }
  ],
  "important_dates": [
    {
      "title": "Начало приёма документов",
      "date": "2025-06-01T00:00:00",
      "description": "Старт приёмной кампании"
    }
  ],
  "faq_highlights": [
    {
      "question": "Какие документы нужны?",
      "answer": "Паспорт, аттестат, фото 3x4"
    }
  ]
}
```

---

#### Специальности

##### GET `/api/v1/specialties`

Получение списка специальностей с пагинацией и фильтрацией.

**Параметры:**
| Параметр | Тип | Обязательный | Описание |
|----------|-----|--------------|----------|
| `page` | int | Нет | Номер страницы (по умолчанию 1, min 1) |
| `limit` | int | Нет | Элементов на странице (по умолчанию 10, 1-50) |
| `search` | string | Нет | Поиск по названию специальности |
| `form` | string | Нет | Форма обучения: `budget` или `paid` |
| `popular` | boolean | Нет | Только популярные специальности |

**Ответ (200 OK):**
```json
{
  "total": 15,
  "page": 1,
  "limit": 10,
  "items": [
    {
      "code": "15.02.19",
      "name": "Сварочное производство",
      "short_description": "Подготовка сварщиков",
      "images": [
        {
          "url": "https://minio.anmicius.ru/images/specialties/welding.jpg",
          "alt": "Сварка"
        }
      ]
    }
  ]
}
```

##### GET `/api/v1/specialties/{code}`

Получение детальной информации о специальности.

**Параметры:**
| Параметр | Тип | Обязательный | Описание |
|----------|-----|--------------|----------|
| `code` | string | Да | Код специальности (например, `15.02.19`) |

**Ответ (200 OK):**
```json
{
  "code": "15.02.19",
  "name": "Сварочное производство",
  "description": [
    "Полное описание специальности",
    "Чему научатся студенты"
  ],
  "duration": "3 г. 10 мес.",
  "budget_places": 25,
  "paid_places": 15,
  "qualification": "Сварщик",
  "exams": ["Математика", "Русский язык", "Физика"],
  "interesting_facts_preview": [
    {
      "id": 1,
      "title": "История специальности"
    }
  ],
  "images": [
    {
      "url": "https://minio.anmicius.ru/images/specialties/welding.jpg",
      "alt": "Сварка",
      "caption": "Учебный класс"
    }
  ]
}
```

**Ответ (404 Not Found):**
```json
{
  "detail": "Специальность с кодом 15.02.19 не найдена"
}
```

##### GET `/api/v1/specialties/{code}/facts`

Получение заголовков интересных фактов для специальности.

**Параметры:**
| Параметр | Тип | Обязательный | Описание |
|----------|-----|--------------|----------|
| `code` | string | Да | Код специальности |

**Ответ (200 OK):**
```json
[
  {
    "id": 1,
    "title": "История специальности"
  },
  {
    "id": 2,
    "title": "Карьерные перспективы"
  }
]
```

##### GET `/api/v1/facts/{fact_id}`

Получение полного содержимого интересного факта.

**Параметры:**
| Параметр | Тип | Обязательный | Описание |
|----------|-----|--------------|----------|
| `fact_id` | int | Да | ID факта |

**Ответ (200 OK):**
```json
{
  "id": 1,
  "title": "История специальности",
  "description": [
    "Полное описание факта",
    "Дополнительная информация"
  ],
  "images": [
    {
      "url": "https://minio.anmicius.ru/images/facts/fact1.jpg",
      "alt": "Факт",
      "caption": "Иллюстрация"
    }
  ]
}
```

---

#### Новости

##### GET `/api/v1/news`

Получение списка новостей с пагинацией.

**Параметры:**
| Параметр | Тип | Обязательный | Описание |
|----------|-----|--------------|----------|
| `page` | int | Нет | Номер страницы (по умолчанию 1, min 1) |
| `limit` | int | Нет | Новостей на странице (по умолчанию 9, 1-20) |
| `search` | string | Нет | Поиск по заголовку новости |

**Ответ (200 OK):**
```json
{
  "total": 50,
  "page": 1,
  "limit": 9,
  "items": [
    {
      "id": 1,
      "title": "День открытых дверей",
      "slug": "den-otkrytykh-dverej",
      "preview_text": "Приглашаем на день открытых дверей",
      "preview_image": "https://minio.anmicius.ru/images/news/preview.jpg",
      "published_at": "2025-03-20T10:00:00"
    }
  ]
}
```

##### GET `/api/v1/news/{slug}`

Получение полной новости с содержимым и галереей.

**Параметры:**
| Параметр | Тип | Обязательный | Описание |
|----------|-----|--------------|----------|
| `slug` | string | Да | URL-идентификатор новости |

**Ответ (200 OK):**
```json
{
  "id": 1,
  "title": "День открытых дверей",
  "slug": "den-otkrytykh-dverej",
  "content": [
    "Первый параграф новости",
    "Второй параграф новости"
  ],
  "gallery": [
    {
      "url": "https://minio.anmicius.ru/images/news/gallery1.jpg",
      "thumbnail": "https://minio.anmicius.ru/images/news/gallery1_thumb.jpg",
      "alt": "Фото 1",
      "caption": "Описание фото"
    }
  ],
  "published_at": "2025-03-20T10:00:00",
  "views": 125
}
```

---

#### FAQ

##### GET `/api/v1/faq`

Получение списка часто задаваемых вопросов.

**Параметры:**
| Параметр | Тип | Обязательный | Описание |
|----------|-----|--------------|----------|
| `category` | string | Нет | Фильтр по категории (например, `Общее`, `Приём`) |

**Ответ (200 OK):**
```json
[
  {
    "id": 1,
    "question": "Какие документы нужны для поступления?",
    "answer": "Паспорт, аттестат, 4 фотографии 3x4",
    "category": "Приём",
    "show_in_admission": true,
    "images": [],
    "documents": []
  }
]
```

---

#### Документы

##### GET `/api/v1/documents`

Получение списка документов для скачивания.

**Параметры:**
| Параметр | Тип | Обязательный | Описание |
|----------|-----|--------------|----------|
| `category` | string | Нет | Фильтр по категории (например, `Лицензии`, `Аккредитации`) |

**Ответ (200 OK):**
```json
[
  {
    "id": 1,
    "title": "Лицензия на образовательную деятельность",
    "category": "Лицензии",
    "file_url": "https://minio.anmicius.ru/documents/licenses/license.pdf",
    "file_size": 1024000,
    "images": []
  }
]
```

---

#### Галерея

##### GET `/api/v1/images`

Получение общей фотогалереи колледжа.

**Параметры:**
| Параметр | Тип | Обязательный | Описание |
|----------|-----|--------------|----------|
| `category` | string | Нет | Фильтр по категории (например, `Колледж`, `Мероприятия`) |

**Ответ (200 OK):**
```json
[
  {
    "id": 1,
    "url": "https://minio.anmicius.ru/images/gallery/img1.jpg",
    "thumbnail": "https://minio.anmicius.ru/images/gallery/img1_thumb.jpg",
    "alt": "Главное здание",
    "category": "Колледж",
    "caption": "Учебный корпус",
    "date_taken": "2025-01-15T12:00:00"
  }
]
```

---

#### Профориентационный тест

##### GET `/api/v1/test/questions`

Получение всех вопросов профориентационного теста.

**Параметры:** Нет

**Ответ (200 OK):**
```json
[
  {
    "id": 1,
    "text": "Что вам нравится делать в свободное время?",
    "options": [
      "Разбирать и собирать технику",
      "Читать книги",
      "Заниматься спортом"
    ],
    "image_url": null,
    "documents": []
  }
]
```

##### POST `/api/v1/test/results`

Отправка ответов на тест и получение персональной рекомендации.

**Тело запроса:**
```json
{
  "answers": [
    {
      "question_id": 1,
      "selected": "Разбирать и собирать технику"
    },
    {
      "question_id": 2,
      "selected": "Связанную с физическим трудом"
    }
  ]
}
```

**Ответ (200 OK):**
```json
{
  "recommendation": "Технические специальности",
  "motivation": "Ваши ответы показывают интерес к технической деятельности...",
  "recommended_specialties": [
    "15.02.19 - Сварочное производство",
    "09.02.07 - Информационные системы"
  ]
}
```

**Ответ (422 Validation Error):**
```json
{
  "detail": "Должно быть ровно 10 ответов"
}
```

---

### Аутентификация

Все endpoints аутентификации находятся под префиксом `/auth`.

#### POST `/auth/register`

Регистрация нового пользователя.

**Тело запроса:**
```json
{
  "email": "admin@example.com",
  "username": "admin",
  "password": "securepassword123"
}
```

**Ответ (200 OK):**
```json
{
  "id": 1,
  "email": "admin@example.com",
  "username": "admin",
  "is_active": true,
  "is_superuser": false,
  "created_at": "2025-03-24T10:00:00"
}
```

**Ответ (400 Bad Request):**
```json
{
  "detail": "Пользователь с таким email уже существует"
}
```

#### POST `/auth/login`

Вход в систему.

**Тело запроса:**
```json
{
  "username": "admin",
  "password": "securepassword123"
}
```

**Ответ (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Ответ (400 Bad Request):**
```json
{
  "detail": "Неверное имя пользователя или пароль"
}
```

#### POST `/auth/login/oauth`

Вход через OAuth2 (используется Swagger UI).

**Тело запроса (form-data):**
```
username: admin
password: securepassword123
```

**Ответ (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### POST `/auth/refresh`

Обновление access токена.

**Тело запроса:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Ответ (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### POST `/auth/logout`

Выход из системы.

**Тело запроса:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Ответ (200 OK):**
```json
{
  "message": "Выход выполнен успешно"
}
```

#### GET `/auth/me`

Получение информации о текущем пользователе.

**Заголовки:**
```
Authorization: Bearer <access_token>
```

**Ответ (200 OK):**
```json
{
  "id": 1,
  "email": "admin@example.com",
  "username": "admin",
  "is_active": true,
  "is_superuser": true,
  "created_at": "2025-03-24T10:00:00"
}
```

---

### Админ-панель

Все endpoints админ-панели требуют **JWT-аутентификации**.

#### Управление пользователями

##### GET `/admin/users`

Получение списка пользователей (только для суперпользователей).

**Заголовки:**
```
Authorization: Bearer <access_token>
```

**Параметры:**
| Параметр | Тип | Обязательный | Описание |
|----------|-----|--------------|----------|
| `page` | int | Нет | Номер страницы (по умолчанию 1) |
| `limit` | int | Нет | Элементов на странице (по умолчанию 10, 1-100) |

**Ответ (200 OK):**
```json
{
  "total": 5,
  "page": 1,
  "limit": 10,
  "items": [
    {
      "id": 1,
      "email": "admin@example.com",
      "username": "admin",
      "is_active": true,
      "is_superuser": true,
      "created_at": "2025-03-24T10:00:00"
    }
  ]
}
```

**Ответ (403 Forbidden):**
```json
{
  "detail": "Недостаточно прав"
}
```

##### GET `/admin/users/{user_id}`

Получение пользователя по ID.

**Заголовки:**
```
Authorization: Bearer <access_token>
```

**Ответ (200 OK):**
```json
{
  "id": 1,
  "email": "admin@example.com",
  "username": "admin",
  "is_active": true,
  "is_superuser": true,
  "created_at": "2025-03-24T10:00:00"
}
```

##### PATCH `/admin/users/{user_id}`

Обновление пользователя.

**Заголовки:**
```
Authorization: Bearer <access_token>
```

**Тело запроса:**
```json
{
  "email": "newemail@example.com",
  "is_active": true,
  "is_superuser": false
}
```

**Ответ (200 OK):**
```json
{
  "id": 1,
  "email": "newemail@example.com",
  "username": "admin",
  "is_active": true,
  "is_superuser": false,
  "created_at": "2025-03-24T10:00:00"
}
```

##### DELETE `/admin/users/{user_id}`

Удаление пользователя.

**Заголовки:**
```
Authorization: Bearer <access_token>
```

**Ответ (200 OK):**
```json
{
  "message": "Пользователь удалён"
}
```

---

#### Управление специальностями

##### GET `/admin/specialties`

Получение списка специальностей.

**Заголовки:**
```
Authorization: Bearer <access_token>
```

**Параметры:**
| Параметр | Тип | Обязательный | Описание |
|----------|-----|--------------|----------|
| `page` | int | Нет | Номер страницы (по умолчанию 1) |
| `limit` | int | Нет | Элементов на странице (по умолчанию 10, 1-100) |

**Ответ (200 OK):**
```json
{
  "total": 15,
  "page": 1,
  "limit": 10,
  "items": [
    {
      "id": 1,
      "code": "15.02.19",
      "name": "Сварочное производство",
      "is_popular": true
    }
  ]
}
```

##### POST `/admin/specialties`

Создание специальности.

**Заголовки:**
```
Authorization: Bearer <access_token>
Content-Type: application/x-www-form-urlencoded
```

**Параметры (form-data):**
| Параметр | Тип | Обязательный | Описание |
|----------|-----|--------------|----------|
| `code` | string | Да | Код специальности |
| `name` | string | Да | Название |
| `short_description` | string | Нет | Краткое описание |
| `description` | string | Нет | JSON массив строк |
| `duration` | string | Нет | Срок обучения |
| `budget_places` | int | Нет | Количество бюджетных мест |
| `paid_places` | int | Нет | Количество платных мест |
| `qualification` | string | Нет | Квалификация |
| `exams` | string | Нет | JSON массив экзаменов |
| `images` | string | Нет | JSON массив изображений |
| `is_popular` | boolean | Нет | Популярная специальность |

**Пример запроса:**
```bash
curl -X POST http://localhost:8000/admin/specialties \
  -H "Authorization: Bearer <token>" \
  -d "code=15.02.19" \
  -d "name=Сварочное производство" \
  -d "short_description=Подготовка сварщиков" \
  -d 'description=["Описание 1", "Описание 2"]' \
  -d "duration=3 г. 10 мес." \
  -d "budget_places=25" \
  -d "paid_places=15" \
  -d "qualification=Сварщик" \
  -d 'exams=["Математика", "Русский язык", "Физика"]' \
  -d 'images=[]' \
  -d "is_popular=true"
```

**Ответ (200 OK):**
```json
{
  "id": 1,
  "code": "15.02.19",
  "name": "Сварочное производство"
}
```

##### GET `/admin/specialties/{specialty_id}`

Получение специальности по ID.

**Заголовки:**
```
Authorization: Bearer <access_token>
```

**Ответ (200 OK):**
```json
{
  "id": 1,
  "code": "15.02.19",
  "name": "Сварочное производство",
  "short_description": "Подготовка сварщиков",
  "description": ["Описание 1"],
  "duration": "3 г. 10 мес.",
  "budget_places": 25,
  "paid_places": 15,
  "qualification": "Сварщик",
  "exams": ["Математика", "Русский язык", "Физика"],
  "images": [],
  "is_popular": true,
  "created_at": "2025-03-24T10:00:00",
  "updated_at": "2025-03-24T10:00:00"
}
```

##### PUT `/admin/specialties/{specialty_id}`

Обновление специальности.

**Заголовки:**
```
Authorization: Bearer <access_token>
Content-Type: application/x-www-form-urlencoded
```

**Параметры:** Те же, что и для создания.

**Ответ (200 OK):**
```json
{
  "id": 1,
  "code": "15.02.19",
  "name": "Сварочное производство"
}
```

##### DELETE `/admin/specialties/{specialty_id}`

Удаление специальности.

**Заголовки:**
```
Authorization: Bearer <access_token>
```

**Ответ (200 OK):**
```json
{
  "message": "Специальность удалена"
}
```

---

#### Управление новостями

##### GET `/admin/news`

Получение списка новостей.

**Заголовки:**
```
Authorization: Bearer <access_token>
```

**Параметры:**
| Параметр | Тип | Обязательный | Описание |
|----------|-----|--------------|----------|
| `page` | int | Нет | Номер страницы (по умолчанию 1) |
| `limit` | int | Нет | Элементов на странице (по умолчанию 10, 1-100) |

**Ответ (200 OK):**
```json
{
  "total": 50,
  "page": 1,
  "limit": 10,
  "items": [
    {
      "id": 1,
      "title": "День открытых дверей",
      "slug": "den-otkrytykh-dverej",
      "published_at": "2025-03-20T10:00:00"
    }
  ]
}
```

##### POST `/admin/news`

Создание новости.

**Заголовки:**
```
Authorization: Bearer <access_token>
Content-Type: application/x-www-form-urlencoded
```

**Параметры (form-data):**
| Параметр | Тип | Обязательный | Описание |
|----------|-----|--------------|----------|
| `title` | string | Да | Заголовок |
| `slug` | string | Да | URL-идентификатор |
| `preview_text` | string | Нет | Краткое описание |
| `content` | string | Нет | JSON массив параграфов |
| `preview_image` | string | Нет | URL превью изображения |
| `gallery` | string | Нет | JSON массив галереи |

**Ответ (200 OK):**
```json
{
  "id": 1,
  "title": "День открытых дверей",
  "slug": "den-otkrythykh-dverej"
}
```

##### GET `/admin/news/{news_id}`

Получение новости по ID.

**Заголовки:**
```
Authorization: Bearer <access_token>
```

##### PUT `/admin/news/{news_id}`

Обновление новости.

**Заголовки:**
```
Authorization: Bearer <access_token>
Content-Type: application/x-www-form-urlencoded
```

##### DELETE `/admin/news/{news_id}`

Удаление новости.

**Заголовки:**
```
Authorization: Bearer <access_token>
```

**Ответ (200 OK):**
```json
{
  "message": "Новость удалена"
}
```

---

#### Управление фактами

##### GET `/admin/facts`

Получение списка фактов.

**Заголовки:**
```
Authorization: Bearer <access_token>
```

**Параметры:**
| Параметр | Тип | Обязательный | Описание |
|----------|-----|--------------|----------|
| `page` | int | Нет | Номер страницы (по умолчанию 1) |
| `limit` | int | Нет | Элементов на странице (по умолчанию 10, 1-100) |

##### POST `/admin/facts`

Создание факта.

**Заголовки:**
```
Authorization: Bearer <access_token>
Content-Type: application/x-www-form-urlencoded
```

**Параметры (form-data):**
| Параметр | Тип | Обязательный | Описание |
|----------|-----|--------------|----------|
| `specialty_code` | string | Да | Код специальности |
| `title` | string | Да | Заголовок факта |
| `description` | string | Нет | JSON массив описаний |
| `images` | string | Нет | JSON массив изображений |

##### GET `/admin/facts/{fact_id}`

Получение факта по ID.

##### PUT `/admin/facts/{fact_id}`

Обновление факта.

##### DELETE `/admin/facts/{fact_id}`

Удаление факта.

---

#### Управление FAQ

##### GET `/admin/faq`

Получение списка FAQ.

**Заголовки:**
```
Authorization: Bearer <access_token>
```

##### POST `/admin/faq`

Создание вопроса FAQ.

**Заголовки:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Тело запроса:**
```json
{
  "question": "Какие документы нужны?",
  "answer": "Паспорт, аттестат, 4 фотографии 3x4",
  "category": "Приём",
  "show_in_admission": true,
  "images": [],
  "documents": []
}
```

##### GET `/admin/faq/{faq_id}`

Получение вопроса по ID.

##### PUT `/admin/faq/{faq_id}`

Обновление вопроса.

##### DELETE `/admin/faq/{faq_id}`

Удаление вопроса.

---

#### Управление документами

##### GET `/admin/documents`

Получение списка документов.

**Заголовки:**
```
Authorization: Bearer <access_token>
```

##### POST `/admin/documents`

Создание документа.

**Заголовки:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Тело запроса:**
```json
{
  "title": "Лицензия",
  "category": "Лицензии",
  "file_url": "https://minio.anmicius.ru/documents/license.pdf",
  "file_size": 1024000,
  "images": []
}
```

##### DELETE `/admin/documents/{document_id}`

Удаление документа.

---

#### Управление галереей

##### GET `/admin/images`

Получение списка изображений.

**Заголовки:**
```
Authorization: Bearer <access_token>
```

##### POST `/admin/images`

Создание элемента галереи.

**Заголовки:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Тело запроса:**
```json
{
  "url": "https://minio.anmicius.ru/images/gallery/img1.jpg",
  "thumbnail": "https://minio.anmicius.ru/images/gallery/img1_thumb.jpg",
  "alt": "Главное здание",
  "category": "Колледж",
  "caption": "Учебный корпус",
  "date_taken": "2025-01-15T12:00:00"
}
```

##### DELETE `/admin/images/{image_id}`

Удаление изображения.

---

#### Управление вопросами теста

##### GET `/admin/test/questions`

Получение списка вопросов теста.

**Заголовки:**
```
Authorization: Bearer <access_token>
```

##### POST `/admin/test/questions`

Создание вопроса теста.

**Заголовки:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Тело запроса:**
```json
{
  "text": "Что вам нравится делать?",
  "options": ["Вариант 1", "Вариант 2", "Вариант 3"],
  "image_url": null,
  "documents": []
}
```

##### DELETE `/admin/test/questions/{question_id}`

Удаление вопроса.

---

#### Управление информацией о колледже

##### GET `/admin/about`

Получение текущей информации.

**Заголовки:**
```
Authorization: Bearer <access_token>
```

##### PUT `/admin/about`

Обновление информации.

**Заголовки:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Тело запроса:**
```json
{
  "title": "Колледж Anmicius",
  "description": ["Описание 1", "Описание 2"],
  "images": [
    {
      "url": "https://minio.anmicius.ru/images/about/img.jpg",
      "alt": "Колледж",
      "caption": "Главное здание"
    }
  ]
}
```

---

#### Загрузка файлов

##### POST `/admin/upload/image`

Загрузка изображения в MinIO.

**Заголовки:**
```
Authorization: Bearer <access_token>
Content-Type: multipart/form-data
```

**Параметры:**
| Параметр | Тип | Обязательный | Описание |
|----------|-----|--------------|----------|
| `file` | file | Да | Файл изображения |
| `category` | string | Нет | Категория (common, specialties, news, facts, gallery) |

**Разрешённые типы файлов:**
- `image/jpeg`
- `image/png`
- `image/gif`
- `image/webp`

**Ответ (200 OK):**
```json
{
  "url": "https://minio.anmicius.ru/images/specialties/abc123.jpg",
  "filename": "image.jpg",
  "size": 102400,
  "content_type": "image/jpeg"
}
```

##### POST `/admin/upload/document`

Загрузка документа в MinIO.

**Заголовки:**
```
Authorization: Bearer <access_token>
Content-Type: multipart/form-data
```

**Параметры:**
| Параметр | Тип | Обязательный | Описание |
|----------|-----|--------------|----------|
| `file` | file | Да | Файл документа |
| `category` | string | Нет | Категория (licenses, accreditations, other) |

**Разрешённые типы файлов:**
- `application/pdf`
- `application/msword`
- `application/vnd.openxmlformats-officedocument.wordprocessingml.document`
- `application/vnd.ms-excel`
- `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`
- `text/plain`

**Ответ (200 OK):**
```json
{
  "url": "https://minio.anmicius.ru/documents/licenses/abc123.pdf",
  "filename": "document.pdf",
  "size": 2048000,
  "content_type": "application/pdf"
}
```

---

## Модели данных

### Specialty (Специальность)

```json
{
  "id": "integer",
  "code": "string (уникальный)",
  "name": "string",
  "short_description": "string",
  "description": "array[string]",
  "duration": "string",
  "budget_places": "integer",
  "paid_places": "integer",
  "qualification": "string",
  "exams": "array[string]",
  "images": "array[Image]",
  "is_popular": "boolean",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### InterestingFact (Интересный факт)

```json
{
  "id": "integer",
  "specialty_code": "string (FK)",
  "title": "string",
  "description": "array[string]",
  "images": "array[Image]",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### News (Новость)

```json
{
  "id": "integer",
  "title": "string",
  "slug": "string (уникальный)",
  "preview_text": "string",
  "content": "array[string]",
  "preview_image": "string|null",
  "gallery": "array[Image]",
  "published_at": "datetime",
  "views": "integer",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### FAQ (Частый вопрос)

```json
{
  "id": "integer",
  "question": "string",
  "answer": "string|array[string]",
  "category": "string",
  "show_in_admission": "boolean",
  "images": "array[Image]",
  "documents": "array[Image]",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### Document (Документ)

```json
{
  "id": "integer",
  "title": "string",
  "category": "string",
  "file_url": "string",
  "file_size": "integer|null",
  "images": "array[Image]",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### GalleryImage (Изображение галереи)

```json
{
  "id": "integer",
  "url": "string",
  "thumbnail": "string",
  "alt": "string",
  "category": "string",
  "caption": "string|null",
  "date_taken": "datetime|null",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### TestQuestion (Вопрос теста)

```json
{
  "id": "integer",
  "text": "string",
  "options": "array[string]",
  "image_url": "string|null",
  "documents": "array[Image]",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### AboutInfo (Информация о колледже)

```json
{
  "id": "integer",
  "title": "string",
  "description": "array[string]",
  "images": "array[Image]",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### AdmissionInfo (Информация о приёме)

```json
{
  "id": "integer",
  "year": "integer (уникальный)",
  "specialties_admission": "array[object]",
  "submission_methods": "array[object]",
  "important_dates": "array[object]",
  "faq_highlights": "array[object]",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### User (Пользователь)

```json
{
  "id": "integer",
  "email": "string (уникальный)",
  "username": "string (уникальный)",
  "hashed_password": "string",
  "is_active": "boolean",
  "is_superuser": "boolean",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### Image (Изображение)

```json
{
  "url": "string",
  "alt": "string",
  "caption": "string|null",
  "thumbnail": "string|null"
}
```

---

## База данных

### Таблицы

| Таблица | Описание |
|---------|----------|
| `specialties` | Специальности колледжа |
| `interesting_facts` | Интересные факты о специальностях |
| `news` | Новости колледжа |
| `faq` | Часто задаваемые вопросы |
| `documents` | Документы для скачивания |
| `gallery_images` | Изображения галереи |
| `test_questions` | Вопросы профориентационного теста |
| `about_info` | Информация о колледже |
| `admission_info` | Информация о приёмной кампании |
| `users` | Пользователи (администраторы) |
| `refresh_tokens` | Refresh токены для аутентификации |

### Миграции

**Создание новой миграции:**
```bash
alembic revision --autogenerate -m "Описание миграции"
```

**Применение миграций:**
```bash
alembic upgrade head
```

**Откат миграций:**
```bash
alembic downgrade -1
```

**Проверка статуса миграций:**
```bash
alembic current
```

---

## Загрузка файлов

### MinIO конфигурация

| Переменная | Описание | По умолчанию |
|------------|----------|--------------|
| `MINIO_ENDPOINT` | MinIO endpoint | `minio:9000` |
| `MINIO_ACCESS_KEY` | Access key | `minioadmin` |
| `MINIO_SECRET_KEY` | Secret key | `minioadmin` |
| `MINIO_BUCKET` | Имя бакета | `anmicius-media` |

### Структура бакета

```
anmicius-media/
├── images/
│   ├── common/
│   ├── specialties/
│   ├── news/
│   ├── facts/
│   └── gallery/
└── documents/
    ├── licenses/
    ├── accreditations/
    └── other/
```

### Генерация уникальных имён файлов

Файлам присваиваются уникальные имена в формате:
```
{uuid4}.{extension}
```

Пример: `abc123-def456-ghi789.jpg`

---

## Безопасность

### JWT токены

| Токен | Время жизни | Назначение |
|-------|-------------|------------|
| Access Token | 24 часа | Доступ к защищённым endpoints |
| Refresh Token | 30 дней | Обновление access токена |

### Роли пользователей

| Роль | Права |
|------|-------|
| Пользователь | Базовый доступ к админ-панели |
| Суперпользователь | Полный доступ, включая управление пользователями |

### Переменные окружения

**Критичные для безопасности:**
```bash
JWT_SECRET_KEY=your-secret-key-change-in-production
DEBUG=false
CORS_ORIGINS=https://anmicius.ru,https://admin.anmicius.ru
```

### Рекомендации для Production

1. Измените `JWT_SECRET_KEY` на криптографически стойкую случайную строку
2. Используйте HTTPS для всех соединений
3. Ограничьте CORS origins только доверенными доменами
4. Регулярно обновляйте зависимости
5. Используйте environment-specific конфигурации
6. Включите rate limiting для API endpoints

---

## Тестирование

### Запуск тестов

**Unit-тесты:**
```bash
pytest tests/test_api.py tests/test_auth.py -v
```

**Интеграционные тесты:**
```bash
# Требуется запущенный сервер на localhost:8000
pytest tests/test_integration.py -v
```

**Все тесты:**
```bash
pytest -v
```

**С отчётом о покрытии:**
```bash
pytest --cov=app --cov-report=html
```

**Отчёт в терминале:**
```bash
pytest --cov=app --cov-report=term-missing
```

### Структура тестов

```
tests/
├── conftest.py          # Фикстуры и конфигурация
├── test_api.py          # Unit-тесты публичных endpoints
├── test_auth.py         # Unit-тесты аутентификации и админки
└── test_integration.py  # Интеграционные тесты
```

### Покрытие кода

Текущее покрытие: **64%**

| Модуль | Покрытие |
|--------|----------|
| Domain models | 100% |
| Infrastructure models | 100% |
| Core exceptions | 100% |
| Presentation schemas | 99% |
| Main app | 87% |
| Presentation routes | 86% |
| Core JWT | 86% |
| Application use cases | 75% |
| Infrastructure repositories | 40% |
| Admin routes | 40% |

---

## Развёртывание

### Docker контейнеры

| Контейнер | Порт | Описание |
|-----------|------|----------|
| `anmicius-api` | 8000 | FastAPI приложение |
| `anmicius-postgres` | 5432 | PostgreSQL база данных |
| `anmicius-minio` | 9000, 9001 | MinIO (S3-совместимое хранилище) |
| `anmicius-nginx` | 80, 443 | Nginx reverse proxy + SSL |
| `anmicius-certbot` | — | Автоматическое обновление SSL |

### Переменные окружения

```bash
# PostgreSQL
POSTGRES_USER=anmicius
POSTGRES_PASSWORD=anmicius_secret_password
POSTGRES_DB=anmicius_db
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

# MinIO
MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET=anmicius-media

# Приложение
DEBUG=false
CORS_ORIGINS=https://anmicius.ru,https://admin.anmicius.ru,https://api.anmicius.ru
JWT_SECRET_KEY=your-secret-key-change-in-production
```

### SSL/HTTPS

**Получение сертификатов Let's Encrypt:**
```bash
./scripts/ssl-cert.sh your-email@example.com
```

**Автоматическое обновление:**
Certbot контейнер автоматически обновляет сертификаты каждые 3 месяца.

### Мониторинг и логи

**Логи приложения:**
```bash
docker-compose logs -f api
```

**Логи базы данных:**
```bash
docker-compose logs -f postgres
```

**Логи Nginx:**
```bash
docker-compose logs -f nginx
```

---

## Приложение A: Примеры использования

### Python (httpx)

```python
import httpx
import asyncio

async def main():
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        # Получение списка специальностей
        response = await client.get("/api/v1/specialties")
        specialties = response.json()
        
        # Получение детали специальности
        response = await client.get("/api/v1/specialties/15.02.19")
        specialty = response.json()
        
        # Аутентификация
        login_response = await client.post("/auth/login", json={
            "username": "admin",
            "password": "adminpass"
        })
        tokens = login_response.json()
        
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        
        # Создание новости (админ)
        news_response = await client.post(
            "/admin/news",
            headers=headers,
            data={
                "title": "Новая новость",
                "slug": "novaya-novost",
                "preview_text": "Краткое описание",
                "content": '["Параграф 1", "Параграф 2"]',
                "gallery": "[]"
            }
        )

asyncio.run(main())
```

### cURL

```bash
# Получение специальностей
curl http://localhost:8000/api/v1/specialties

# Аутентификация
TOKEN=$(curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"adminpass"}' | jq -r '.access_token')

# Создание специальности
curl -X POST http://localhost:8000/admin/specialties \
  -H "Authorization: Bearer $TOKEN" \
  -d "code=15.02.19" \
  -d "name=Сварочное производство" \
  -d "short_description=Подготовка сварщиков"

# Загрузка изображения
curl -X POST "http://localhost:8000/admin/upload/image?category=specialties" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@image.jpg"
```

---

## Приложение B: Коды ошибок

| Код | Описание |
|-----|----------|
| 200 | Успешный запрос |
| 400 | Некорректный запрос (валидация, бизнес-логика) |
| 401 | Неавторизованный доступ |
| 403 | Доступ запрещён (недостаточно прав) |
| 404 | Ресурс не найден |
| 422 | Ошибка валидации (Pydantic) |
| 500 | Внутренняя ошибка сервера |

---

## Приложение C: Changelog

### Версия 1.0.0

- ✅ Публичные endpoints для получения информации о колледже
- ✅ Управление специальностями, новостями, FAQ, документами
- ✅ Профориентационный тест
- ✅ JWT аутентификация
- ✅ Загрузка файлов в MinIO
- ✅ Чистая архитектура (Clean Architecture)
- ✅ Покрытие тестами 64%

---

**Документация создана:** 2025-03-24  
**Версия API:** 1.0.0  
**Контакты:** support@anmicius.ru
