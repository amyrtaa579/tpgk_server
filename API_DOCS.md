# Anmicius API - Документация

> ⚠️ **Обратите внимание:** Эта документация устарела.  
> 📄 **Актуальная техническая документация:** см. [DOCUMENTATION.md](DOCUMENTATION.md)

## Обзор

API для колледжа Anmicius, реализованное на FastAPI. Предоставляет публичные endpoints для получения информации о колледже и защищённые endpoints для администраторов.

## Содержание

- [Быстрый старт](#быстрый-старт)
- [Публичные API](#публичные-api)
- [Админ-панель](#админ-панель)
- [Аутентификация](#аутентификация)
- [Загрузка файлов](#загрузка-файлов)

---

## Быстрый старт

### Запуск через Docker

```bash
docker-compose up -d
```

API доступен по адресу: `http://localhost:8000`

### Документация Swagger

Откройте `http://localhost:8000/docs` для интерактивной документации.

---

## Публичные API

Все публичные endpoints находятся под префиксом `/api/v1` и не требуют аутентификации.

### Информация о колледже

| Метод | Endpoint | Описание |
|-------|----------|----------|
| GET | `/api/v1/about` | Информация о колледже |
| GET | `/api/v1/admission` | Приёмная кампания |

### Специальности

| Метод | Endpoint | Описание |
|-------|----------|----------|
| GET | `/api/v1/specialties` | Список специальностей (с пагинацией) |
| GET | `/api/v1/specialties/{code}` | Детали специальности |
| GET | `/api/v1/specialties/{code}/facts` | Факты специальности |

### Новости

| Метод | Endpoint | Описание |
|-------|----------|----------|
| GET | `/api/v1/news` | Список новостей |
| GET | `/api/v1/news/{slug}` | Детали новости |

### Другое

| Метод | Endpoint | Описание |
|-------|----------|----------|
| GET | `/api/v1/faq` | Часто задаваемые вопросы |
| GET | `/api/v1/documents` | Документы |
| GET | `/api/v1/images` | Галерея изображений |
| GET | `/api/v1/test/questions` | Вопросы профориентационного теста |
| POST | `/api/v1/test/results` | Отправка результатов теста |

---

## Админ-панель

Все endpoints админ-панели требуют JWT-аутентификации.

### Аутентификация

#### Регистрация нового пользователя

```bash
POST /auth/register
Content-Type: application/json

{
  "email": "admin@example.com",
  "username": "admin",
  "password": "securepassword123"
}
```

#### Вход в систему

```bash
POST /auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "securepassword123"
}
```

**Ответ:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

#### Обновление токена

```bash
POST /auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
}
```

#### Выход из системы

```bash
POST /auth/logout
Content-Type: application/json

{
  "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
}
```

#### Получение информации о текущем пользователе

```bash
GET /auth/me
Authorization: Bearer <access_token>
```

---

### Управление пользователями (только для суперпользователей)

#### Получить всех пользователей

```bash
GET /admin/users?page=1&limit=10
Authorization: Bearer <access_token>
```

#### Получить пользователя по ID

```bash
GET /admin/users/{user_id}
Authorization: Bearer <access_token>
```

#### Обновить пользователя

```bash
PATCH /admin/users/{user_id}
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "email": "newemail@example.com",
  "is_active": true,
  "is_superuser": false
}
```

#### Удалить пользователя

```bash
DELETE /admin/users/{user_id}
Authorization: Bearer <access_token>
```

---

### Управление специальностями

#### Получить все специальности

```bash
GET /admin/specialties?page=1&limit=10
Authorization: Bearer <access_token>
```

#### Создать специальность

```bash
POST /admin/specialties
Authorization: Bearer <access_token>
Content-Type: application/x-www-form-urlencoded

code=15.02.19&
name=Сварочное производство&
short_description=Подготовка сварщиков&
description=[]&
duration=3 г. 10 мес.&
budget_places=25&
paid_places=15&
qualification=Сварщик&
exams=[]&
images=[]&
is_popular=false
```

#### Получить специальность по ID

```bash
GET /admin/specialties/{specialty_id}
Authorization: Bearer <access_token>
```

#### Обновить специальность

```bash
PUT /admin/specialties/{specialty_id}
Authorization: Bearer <access_token>
Content-Type: application/x-www-form-urlencoded

code=15.02.19&
name=Обновлённое название&
...
```

#### Удалить специальность

```bash
DELETE /admin/specialties/{specialty_id}
Authorization: Bearer <access_token>
```

---

### Управление новостями

#### Получить все новости

```bash
GET /admin/news?page=1&limit=10
Authorization: Bearer <access_token>
```

#### Создать новость

```bash
POST /admin/news
Authorization: Bearer <access_token>
Content-Type: application/x-www-form-urlencoded

title=Заголовок новости&
slug=zagolovok-novosti&
preview_text=Краткое описание&
content=["Параграф 1", "Параграф 2"]&
preview_image=https://example.com/image.jpg&
gallery=[]
```

#### Получить новость по ID

```bash
GET /admin/news/{news_id}
Authorization: Bearer <access_token>
```

#### Обновить новость

```bash
PUT /admin/news/{news_id}
Authorization: Bearer <access_token>
Content-Type: application/x-www-form-urlencoded

title=Обновлённый заголовок&
...
```

#### Удалить новость

```bash
DELETE /admin/news/{news_id}
Authorization: Bearer <access_token>
```

---

### Управление фактами

#### Получить все факты

```bash
GET /admin/facts?page=1&limit=10
Authorization: Bearer <access_token>
```

#### Создать факт

```bash
POST /admin/facts
Authorization: Bearer <access_token>
Content-Type: application/x-www-form-urlencoded

specialty_code=15.02.19&
title=Интересный факт&
description=["Описание факта"]&
images=[]
```

#### Удалить факт

```bash
DELETE /admin/facts/{fact_id}
Authorization: Bearer <access_token>
```

---

## Загрузка файлов

### Загрузка изображения

```bash
POST /admin/upload/image?category=common
Authorization: Bearer <access_token>
Content-Type: multipart/form-data

file: <binary>
```

**Разрешённые типы файлов:**
- `image/jpeg`
- `image/png`
- `image/gif`
- `image/webp`

**Ответ:**
```json
{
  "url": "http://minio:9000/anmicius-media/images/common/abc123.jpg",
  "filename": "image.jpg",
  "size": 102400,
  "content_type": "image/jpeg"
}
```

### Загрузка документа

```bash
POST /admin/upload/document?category=licenses
Authorization: Bearer <access_token>
Content-Type: multipart/form-data

file: <binary>
```

**Разрешённые типы файлов:**
- `application/pdf`
- `application/msword`
- `application/vnd.openxmlformats-officedocument.wordprocessingml.document`
- `application/vnd.ms-excel`
- `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`
- `text/plain`

---

## Примеры использования

### Python (с использованием httpx)

```python
import httpx
import asyncio

async def main():
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        # Вход
        login_response = await client.post("/auth/login", json={
            "username": "admin",
            "password": "adminpass"
        })
        tokens = login_response.json()
        
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        
        # Создание специальности
        specialty_response = await client.post(
            "/admin/specialties",
            headers=headers,
            data={
                "code": "15.02.19",
                "name": "Сварочное производство",
                "short_description": "Подготовка сварщиков",
                "description": "[]",
                "duration": "3 г. 10 мес.",
                "budget_places": 25,
                "paid_places": 15,
                "qualification": "Сварщик",
                "exams": "[]",
                "images": "[]",
                "is_popular": True,
            }
        )
        
        # Загрузка изображения
        with open("image.jpg", "rb") as f:
            files = {"file": ("image.jpg", f, "image/jpeg")}
            upload_response = await client.post(
                "/admin/upload/image?category=specialties",
                headers=headers,
                files=files
            )
            image_url = upload_response.json()["url"]
        
        print(f"Изображение загружено: {image_url}")

asyncio.run(main())
```

### cURL

```bash
# Вход
TOKEN=$(curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"adminpass"}' | jq -r '.access_token')

# Получение списка пользователей
curl -s http://localhost:8000/admin/users \
  -H "Authorization: Bearer $TOKEN"

# Загрузка изображения
curl -s -X POST http://localhost:8000/admin/upload/image?category=test \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@image.jpg"
```

---

## Структура проекта

```
app/
├── core/           # Конфигурация, JWT, исключения
├── domain/         # Доменные модели и интерфейсы репозиториев
├── application/    # Use cases и зависимости
├── infrastructure/ # Реализация репозиториев, модели БД, MinIO
├── presentation/   # API роутеры и Pydantic схемы
└── main.py         # Точка входа приложения
```

---

## Тесты

### Запуск тестов

```bash
# Unit-тесты
bash scripts/run_tests.sh unit

# Интеграционные тесты
bash scripts/run_tests.sh integration

# Все тесты
bash scripts/run_tests.sh all

# С отчётом о покрытии
bash scripts/run_tests.sh coverage
```

---

## Переменные окружения

| Переменная | Описание | По умолчанию |
|------------|----------|--------------|
| `POSTGRES_USER` | Пользователь PostgreSQL | `anmicius` |
| `POSTGRES_PASSWORD` | Пароль PostgreSQL | `anmicius_secret_password` |
| `POSTGRES_DB` | Имя базы данных | `anmicius_db` |
| `POSTGRES_HOST` | Хост PostgreSQL | `postgres` |
| `MINIO_ENDPOINT` | MinIO endpoint | `minio:9000` |
| `MINIO_ACCESS_KEY` | MinIO access key | `minioadmin` |
| `MINIO_SECRET_KEY` | MinIO secret key | `minioadmin` |
| `MINIO_BUCKET` | Имя бакета | `anmicius-media` |
| `DEBUG` | Режим отладки | `false` |
| `JWT_SECRET_KEY` | Секретный ключ JWT | (измените в production!) |

---

## Безопасность

### JWT Токены

- **Access Token**: действует 24 часа, используется для доступа к защищённым endpoints
- **Refresh Token**: действует 30 дней, используется для обновления access token

### Роли пользователей

- **Пользователь**: базовый доступ к админ-панели
- **Суперпользователь**: полный доступ, включая управление пользователями

### Рекомендации для Production

1. Измените `JWT_SECRET_KEY` на случайную строку
2. Используйте HTTPS
3. Ограничьте CORS origins
4. Регулярно обновляйте зависимости
