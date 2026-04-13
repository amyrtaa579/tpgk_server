# Админ-эндпоинты API

Все эндпоинты префикса `/admin` требуют **JWT-аутентификации**. Большинство операций — CRUD для соответствующих сущностей.

## Базовый URL

```
https://api.anmicius.ru/admin
```

## Заголовки

```
Authorization: Bearer <access_token>
Content-Type: application/json          # для JSON-запросов
Content-Type: multipart/form-data       # для загрузки файлов
```

---

## Управление пользователями (`/admin/users`)

**Требование:** Суперпользователь

### GET /admin/users

Список всех пользователей с пагинацией.

**Параметры:**
| Параметр | Тип | По умолчанию | Описание |
|----------|-----|-------------|----------|
| `page` | int | 1 | Номер страницы |
| `limit` | int | 10 | Элементов (1-100) |

**Ответ:**
```json
{
  "items": [
    {
      "id": 1,
      "email": "admin@anmicius.ru",
      "username": "admin",
      "is_active": true,
      "is_superuser": true
    }
  ],
  "total": 5,
  "page": 1,
  "limit": 10,
  "pages": 1
}
```

### GET /admin/users/{user_id}

Информация о конкретном пользователе.

### PATCH /admin/users/{user_id}

Обновить данные пользователя.

**Тело запроса:**
```json
{
  "email": "new@example.com",
  "is_active": true,
  "is_superuser": false,
  "password": "NewStr0ng!Pass"
}
```

Все поля необязательны. Указываются только те, что нужно изменить.

> **Важно:** При изменении пароля все refresh-токены пользователя аннулируются.

### DELETE /admin/users/{user_id}

Удалить пользователя. Каскадно удаляются все refresh-токены.

---

## Управление специальностями (`/admin/specialties`)

### GET /admin/specialties

Список специальностей (пагинация).

**Параметры:**
| Параметр | Тип | По умолчанию |
|----------|-----|-------------|
| `page` | int | 1 |
| `limit` | int | 10 (1-100) |

### POST /admin/specialties

Создать специальность.

**Content-Type:** `application/x-www-form-urlencoded`

**Поля формы:**
| Поле | Тип | Обязательный | Описание |
|------|-----|-------------|----------|
| `code` | string | Да | Код специальности (уникальный) |
| `name` | string | Да | Название |
| `short_description` | string | Да | Краткое описание |
| `description` | JSON string | Нет | Массив строк (полное описание) |
| `exams` | JSON string | Нет | Массив строк (экзамены) |
| `images` | JSON string | Нет | Массив объектов Image |
| `documents` | JSON string | Нет | Массив объектов Image |
| `education_options` | JSON string | Нет | Массив education options |

**Пример cURL:**
```bash
curl -X POST https://api.anmicius.ru/admin/specialties \
  -H "Authorization: Bearer TOKEN" \
  -F "code=09.02.07" \
  -F "name=Информационные системы и программирование" \
  -F "short_description=Подготовка программистов" \
  -F 'description=["Полное описание..."]' \
  -F 'exams=["Математика", "Русский язык"]' \
  -F 'education_options=[{"education_level":"9 классов","duration":"3г 10м","budget_places":25,"paid_places":10}]'
```

> **После создания кэш `public` автоматически очищается.**

### GET /admin/specialties/{specialty_id}

Получить специальность по ID.

### PUT /admin/specialties/{specialty_id}

Полностью обновить специальность. Формат данных аналогичен POST.

### DELETE /admin/specialties/{specialty_id}

Удалить специальость. Каскадно удаляются education options.

> **После удаления кэш `public` автоматически очищается.**

---

## Управление новостями (`/admin/news`)

### GET /admin/news

Список новостей.

**Параметры:**
| Параметр | Тип | По умолчанию |
|----------|-----|-------------|
| `page` | int | 1 |
| `limit` | int | 10 (1-100) |

### POST /admin/news

Создать новость.

**Content-Type:** `multipart/form-data`

**Поля формы:**
| Поле | Тип | Обязательный |
|------|-----|-------------|
| `title` | string | Да |
| `slug` | string | Да (уникальный) |
| `preview_text` | string | Да |
| `content` | JSON string | Да (массив строк) |
| `preview_image` | JSON string | Нет |
| `gallery` | JSON string | Нет (массив Image) |

### GET /admin/news/{news_id}

Получить новость по ID.

### PUT /admin/news/{news_id}

Обновить новость.

### DELETE /admin/news/{news_id}

Удалить новость.

> **После любого CRUD кэш `public` автоматически очищается.**

---

## Управление фактами (`/admin/facts`)

### GET /admin/facts

Список фактов.

**Параметры:**
| Параметр | Тип | По умолчанию |
|----------|-----|-------------|
| `page` | int | 1 |
| `limit` | int | 10 (1-100) |

### POST /admin/facts

Создать факт.

**Content-Type:** `multipart/form-data`

**Поля:**
| Поле | Тип | Обязательный |
|------|-----|-------------|
| `specialty_code` | string | Да |
| `title` | string | Да |
| `description` | JSON string | Да (массив строк) |
| `images` | JSON string | Нет |

### GET /admin/facts/{fact_id}

Получить факт по ID.

### PUT /admin/facts/{fact_id}

Обновить факт.

### DELETE /admin/facts/{fact_id}

Удалить факт.

> **Кэш `public` инвалидируется автоматически.**

---

## Загрузка файлов (`/admin/upload`)

### POST /admin/upload/image

Загрузить изображение.

**Content-Type:** `multipart/form-data`

**Поля:**
| Поле | Тип | Описание |
|------|-----|----------|
| `file` | File | Файл изображения |
| `category` | string | Категория (subfolder) |

**Поддерживаемые форматы:** JPEG, PNG, GIF, WebP
**Максимальный размер:** 10 МБ

**Ответ:**
```json
{
  "url": "https://minio.anmicius.ru/anmicius-media/images/news/abc123def.jpg"
}
```

### POST /admin/upload/document

Загрузить документ.

**Content-Type:** `multipart/form-data`

**Поля:**
| Поле | Тип | Описание |
|------|-----|----------|
| `file` | File | Файл документа |
| `category` | string | Категория |

**Поддерживаемые форматы:** PDF, DOC, DOCX, XLS, XLSX, TXT
**Максимальный размер:** 50 МБ

**Ответ:**
```json
{
  "url": "https://minio.anmicius.ru/anmicius-media/documents/other/xyz456.pdf"
}
```

### GET /admin/upload/minio/list

Список файлов в MinIO.

**Параметры запроса:**
| Параметр | Тип | Описание |
|----------|-----|----------|
| `prefix` | string | Префикс пути (например `images/news/`) |

**Ответ:**
```json
[
  {
    "name": "images/news/abc123.jpg",
    "size": 1024000,
    "last_modified": "2025-01-15T10:00:00Z"
  }
]
```

---

## Фотогалерея (`/admin/gallery`)

### GET /admin/gallery

Список изображений галереи.

**Параметры:**
| Параметр | Тип | Описание |
|----------|-----|----------|
| `category` | string | Фильтр по категории |

### POST /admin/gallery

Добавить изображение в галерею.

**Тело (JSON):**
```json
{
  "url": "https://minio.anmicius.ru/anmicius-media/images/gallery/abc.jpg",
  "thumbnail": "https://minio.anmicius.ru/anmicius-media/images/gallery/thumb.jpg",
  "alt": "Описание",
  "category": "college",
  "caption": "Подпись",
  "date_taken": "2025-01-15"
}
```

### GET /admin/gallery/{image_id}

Получить изображение по ID.

### PUT /admin/gallery/{image_id}

Обновить изображение.

### DELETE /admin/gallery/{image_id}

Удалить изображение.

---

## Файлы документов (`/admin/document-files`)

### GET /admin/document-files

Список файлов документов.

**Параметры:**
| Параметр | Тип | Описание |
|----------|-----|----------|
| `category` | string | Фильтр |

### POST /admin/document-files

Создать запись документа.

```json
{
  "title": "Правила приёма",
  "file_url": "https://minio.anmicius.ru/anmicius-media/documents/rules.pdf",
  "file_size": 1024000,
  "category": "admission"
}
```

### GET /admin/document-files/{file_id}

Получить файл по ID.

### PUT /admin/document-files/{file_id}

Обновить файл.

### DELETE /admin/document-files/{file_id}

Удалить файл.

---

## FAQ (`/admin/faq`)

### GET /admin/faq

Список FAQ-записей.

**Параметры:**
| Параметр | Тип | Описание |
|----------|-----|----------|
| `category` | string | Фильтр |

### GET /admin/faq/{faq_id}

Получить FAQ по ID.

### POST /admin/faq

Создать FAQ.

```json
{
  "question": "Как поступить?",
  "answer": "Необходимо подать документы...",
  "category": "admission",
  "show_in_admission": true,
  "images": [],
  "documents": [],
  "document_file_ids": []
}
```

### PUT /admin/faq/{faq_id}

Обновить FAQ.

### DELETE /admin/faq/{faq_id}

Удалить FAQ.

> **Кэш `public` инвалидируется.**

---

## Документы (`/admin/documents`)

### GET /admin/documents

Список документов.

**Параметры:**
| Параметр | Тип | Описание |
|----------|-----|----------|
| `category` | string | Фильтр |

### GET /admin/documents/{doc_id}

Получить документ по ID.

### POST /admin/documents

Создать документ.

```json
{
  "title": "Лицензия",
  "category": "licenses",
  "file_url": "https://minio.anmicius.ru/anmicius-media/documents/licenses/license.pdf",
  "file_size": 2048000,
  "images": []
}
```

### PUT /admin/documents/{doc_id}

Обновить документ.

### DELETE /admin/documents/{doc_id}

Удалить документ.

> **Кэш `public` инвалидируется.**

---

## О колледже (`/admin/about`)

### GET /admin/about

Получить текущую информацию о колледже.

### PUT /admin/about

Обновить информацию.

```json
{
  "title": "Стрельнинский филиал ТИГК",
  "description": [
    "Колледж ведёт подготовку с 1965 года...",
    "Обновлённое описание..."
  ],
  "images": [
    {
      "url": "https://minio.anmicius.ru/anmicius-media/images/common/main.jpg",
      "alt": "Здание колледжа"
    }
  ]
}
```

> **Кэш `public` инвалидируется.**

---

## Вопросы теста (`/admin/test/questions`)

### GET /admin/test/questions

Список всех вопросов профориентационного теста.

### GET /admin/test/questions/{question_id}

Получить вопрос по ID.

### POST /admin/test/questions

Создать вопрос.

```json
{
  "text": "Что вам больше нравится?",
  "options": [
    "Разбираться в технике",
    "Рисовать",
    "Работать с людьми",
    "Считать"
  ],
  "answer_scores": [
    {"15.02.19": 3, "21.02.03": 1},
    {"54.02.01": 3, "09.02.07": 2},
    {"43.02.15": 3, "38.02.01": 2},
    {"09.02.07": 3, "38.02.01": 1}
  ],
  "image_url": null,
  "documents": []
}
```

**Поле `answer_scores`:** Массив словарей. Индекс словаря соответствует индексу варианта ответа в `options`. Ключи — коды специальностей, значения — баллы.

### PUT /admin/test/questions/{question_id}

Обновить вопрос.

### DELETE /admin/test/questions/{question_id}

Удалить вопрос.

---

## Приёмная кампания (`/admin/admission`)

### GET /admin/admission

Список всех приёмных кампаний.

### GET /admin/admission/{year}

Получить кампанию по году.

### POST /admin/admission

Создать приёмную кампанию.

```json
{
  "year": 2025,
  "specialties_admission": [
    {
      "specialty_code": "09.02.07",
      "specialty_name": "Информационные системы",
      "budget_places": 25,
      "paid_places": 10,
      "min_score": 150,
      "description": "Приём на основе ОГЭ"
    }
  ],
  "submission_methods": [
    {
      "title": "Лично",
      "description": "В приёмной комиссии",
      "link": ""
    }
  ],
  "important_dates": [
    {
      "title": "Начало приёма",
      "date": "2025-06-20",
      "description": "Приём документов"
    }
  ]
}
```

### PUT /admin/admission/{year}

Обновить кампанию.

### DELETE /admin/admission/{year}

Удалить кампанию.

---

## Управление кэшем (`/admin/cache`)

**Требование:** Суперпользователь

### GET /admin/cache/stats

Статистика кэширования.

**Ответ:**
```json
{
  "total_keys": 42,
  "total_size_bytes": 1048576,
  "groups": {
    "public": {
      "version": 15,
      "keys": 42
    }
  }
}
```

### POST /admin/cache/clear

Очистить весь кэш.

**Ответ:**
```json
{
  "message": "Cache cleared",
  "cleared_keys": 42
}
```

### POST /admin/cache/clear/{group}

Очистить кэш конкретной группы (инкрементирует версию).

**Параметр пути:**
| Параметр | Описание |
|----------|----------|
| `group` | Название группы (например `public`) |

---

## Сводная таблица всех админ-эндпоинтов

### Пользователи

| Метод | Путь | Scope | Описание |
|-------|------|-------|----------|
| GET | `/admin/users` | `users:read` (superuser) | Список |
| GET | `/admin/users/{id}` | `users:read` (superuser) | По ID |
| PATCH | `/admin/users/{id}` | `users:write` (superuser) | Обновить |
| DELETE | `/admin/users/{id}` | superuser | Удалить |

### Специальности

| Метод | Путь | Scope |
|-------|------|-------|
| GET | `/admin/specialties` | `specialties:read` |
| POST | `/admin/specialties` | `specialties:write` |
| GET | `/admin/specialties/{id}` | `specialties:read` |
| PUT | `/admin/specialties/{id}` | `specialties:write` |
| DELETE | `/admin/specialties/{id}` | `specialties:write` |

### Новости

| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/admin/news` | Список |
| POST | `/admin/news` | Создать |
| GET | `/admin/news/{id}` | По ID |
| PUT | `/admin/news/{id}` | Обновить |
| DELETE | `/admin/news/{id}` | Удалить |

### Факты

| Метод | Путь |
|-------|------|
| GET | `/admin/facts` |
| POST | `/admin/facts` |
| GET | `/admin/facts/{id}` |
| PUT | `/admin/facts/{id}` |
| DELETE | `/admin/facts/{id}` |

### Загрузка

| Метод | Путь | Макс. размер |
|-------|------|-------------|
| POST | `/admin/upload/image` | 10 МБ |
| POST | `/admin/upload/document` | 50 МБ |
| GET | `/admin/upload/minio/list` | — |

### Галерея

| Метод | Путь |
|-------|------|
| GET | `/admin/gallery` |
| POST | `/admin/gallery` |
| GET | `/admin/gallery/{id}` |
| PUT | `/admin/gallery/{id}` |
| DELETE | `/admin/gallery/{id}` |

### Файлы документов

| Метод | Путь |
|-------|------|
| GET | `/admin/document-files` |
| POST | `/admin/document-files` |
| GET | `/admin/document-files/{id}` |
| PUT | `/admin/document-files/{id}` |
| DELETE | `/admin/document-files/{id}` |

### FAQ

| Метод | Путь |
|-------|------|
| GET | `/admin/faq` |
| GET | `/admin/faq/{id}` |
| POST | `/admin/faq` |
| PUT | `/admin/faq/{id}` |
| DELETE | `/admin/faq/{id}` |

### Документы

| Метод | Путь |
|-------|------|
| GET | `/admin/documents` |
| GET | `/admin/documents/{id}` |
| POST | `/admin/documents` |
| PUT | `/admin/documents/{id}` |
| DELETE | `/admin/documents/{id}` |

### О колледже

| Метод | Путь |
|-------|------|
| GET | `/admin/about` |
| PUT | `/admin/about` |

### Тест

| Метод | Путь |
|-------|------|
| GET | `/admin/test/questions` |
| GET | `/admin/test/questions/{id}` |
| POST | `/admin/test/questions` |
| PUT | `/admin/test/questions/{id}` |
| DELETE | `/admin/test/questions/{id}` |

### Кэш (superuser only)

| Метод | Путь |
|-------|------|
| GET | `/admin/cache/stats` |
| POST | `/admin/cache/clear` |
| POST | `/admin/cache/clear/{group}` |

### Приёмная кампания

| Метод | Путь |
|-------|------|
| GET | `/admin/admission` |
| GET | `/admin/admission/{year}` |
| POST | `/admin/admission` |
| PUT | `/admin/admission/{year}` |
| DELETE | `/admin/admission/{year}` |

---

## Автоматическая инвалидация кэша

При любом изменении данных (POST/PUT/DELETE) в админ-панели кэш `public` **автоматически очищается** через `cache_service.clear_group("public")`.

Это гарантирует, что публичное API всегда возвращает актуальные данные после изменений через админку.
