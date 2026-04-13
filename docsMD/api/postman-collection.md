# Примеры запросов (Postman/cURL)

Полная коллекция примеров HTTP-запросов для всех эндпоинтов API в форматах **cURL** и **HTTP**.

## Базовая информация

| Параметр | Значение |
|----------|----------|
| **Базовый URL (dev)** | `http://localhost:8000` |
| **Базовый URL (prod)** | `https://api.anmicius.ru` |
| **Аутентификация** | JWT Bearer Token |
| **Content-Type** | `application/json` или `multipart/form-data` |

---

## Health Check и Root

### GET /health

Проверка состояния всех сервис.

**cURL:**
```bash
curl -X GET http://localhost:8000/health
```

**Ответ (200 OK):**
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

---

### GET /

Информация о сервисе.

**cURL:**
```bash
curl -X GET http://localhost:8000
```

**Ответ (200 OK):**
```json
{
  "name": "Anmicius API",
  "version": "1.0.0",
  "docs": "/docs"
}
```

---

## Аутентификация

### POST /auth/register

Регистрация нового пользователя.

**cURL:**
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@anmicius.ru",
    "username": "admin",
    "password": "Str0ng!Pass123"
  }'
```

**Ответ (200 OK):**
```json
{
  "id": 1,
  "email": "admin@anmicius.ru",
  "username": "admin",
  "is_active": true,
  "is_superuser": false
}
```

---

### POST /auth/login

Вход в систему.

**cURL:**
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "Str0ng!Pass123"
  }'
```

**Ответ (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Сохранение токена в переменную:**
```bash
TOKEN=$(curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"Str0ng!Pass123"}' \
  | jq -r '.access_token')
```

---

### POST /auth/refresh

Обновление access токена.

**cURL:**
```bash
curl -X POST http://localhost:8000/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "eyJhbGci..."
  }'
```

**Ответ (200 OK):**
```json
{
  "access_token": "eyJhbGci...новый...",
  "refresh_token": "eyJhbGci...новый...",
  "token_type": "bearer"
}
```

---

### POST /auth/logout

Выход из системы.

**cURL:**
```bash
curl -X POST http://localhost:8000/auth/logout \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "eyJhbGci..."
  }'
```

**Ответ (200 OK):**
```json
{
  "message": "Выход выполнен успешно"
}
```

---

### GET /auth/me

Текущий пользователь.

**cURL:**
```bash
curl -X GET http://localhost:8000/auth/me \
  -H "Authorization: Bearer eyJhbGci..."
```

**Ответ (200 OK):**
```json
{
  "id": 1,
  "email": "admin@anmicius.ru",
  "username": "admin",
  "is_active": true,
  "is_superuser": false
}
```

---

## Публичные эндпоинты

### GET /api/v1/about

Информация о колледже.

**cURL:**
```bash
curl -X GET http://localhost:8000/api/v1/about
```

**Ответ (200 OK):**
```json
{
  "title": "Стрельнинский филиал ТИГК",
  "description": [
    "Колледж ведёт подготовку специалистов с 1965 года...",
    "Образование ведётся по нескольким направлениям..."
  ],
  "images": [
    {
      "url": "https://minio.anmicius.ru/anmicius-media/images/common/main.jpg",
      "alt": "Главное здание",
      "caption": "Вход в главное здание"
    }
  ]
}
```

---

### GET /api/v1/specialties

Список специальностей.

**Без параметров:**
```bash
curl -X GET http://localhost:8000/api/v1/specialties
```

**С пагинацией:**
```bash
curl -X GET "http://localhost:8000/api/v1/specialties?page=2&limit=5"
```

**С поиском:**
```bash
curl -X GET "http://localhost:8000/api/v1/specialties?search=программ"
```

**С фильтром по форме обучения:**
```bash
# Только с бюджетными местами
curl -X GET "http://localhost:8000/api/v1/specialties?form=budget"

# Только с платными местами
curl -X GET "http://localhost:8000/api/v1/specialties?form=paid"
```

**Только популярные:**
```bash
curl -X GET "http://localhost:8000/api/v1/specialties?popular=true"
```

**Ответ (200 OK):**
```json
{
  "items": [
    {
      "id": 1,
      "code": "09.02.07",
      "name": "Информационные системы и программирование",
      "short_description": "Подготовка специалистов в области разработки ПО..."
    }
  ],
  "total": 12,
  "page": 1,
  "limit": 10,
  "pages": 2
}
```

---

### GET /api/v1/specialties/{code}

Детали специальности.

**cURL:**
```bash
curl -X GET http://localhost:8000/api/v1/specialties/09.02.07
```

**Ответ (200 OK):**
```json
{
  "id": 1,
  "code": "09.02.07",
  "name": "Информационные системы и программирование",
  "description": [
    "Программа подготовки охватывает...",
    "Студенты изучают..."
  ],
  "exams": ["Математика (ОГЭ)", "Русский язык (ОГЭ)"],
  "images": [],
  "education_options": [
    {
      "id": 1,
      "education_level": "На базе 9 классов",
      "duration": "3 года 10 месяцев",
      "budget_places": 25,
      "paid_places": 10
    }
  ],
  "facts_preview": [
    {
      "id": 1,
      "title": "Программирование — это творчество"
    }
  ]
}
```

---

### GET /api/v1/news

Список новостей.

**cURL:**
```bash
curl -X GET "http://localhost:8000/api/v1/news?page=1&limit=5"
```

**С поиском:**
```bash
curl -X GET "http://localhost:8000/api/v1/news?search=день"
```

---

### GET /api/v1/news/{slug}

Детали новости.

**cURL:**
```bash
curl -X GET http://localhost:8000/api/v1/news/open-day-2025
```

---

### GET /api/v1/faq

FAQ с фильтром категории.

**Все FAQ:**
```bash
curl -X GET http://localhost:8000/api/v1/faq
```

**По категории:**
```bash
curl -X GET "http://localhost:8000/api/v1/faq?category=admission"
```

---

### GET /api/v1/documents

Документы.

**Все документы:**
```bash
curl -X GET http://localhost:8000/api/v1/documents
```

**По категории:**
```bash
curl -X GET "http://localhost:8000/api/v1/documents?category=licenses"
```

---

### GET /api/v1/images

Фотогалерея.

**Все изображения:**
```bash
curl -X GET http://localhost:8000/api/v1/images
```

**По категории:**
```bash
curl -X GET "http://localhost:8000/api/v1/images?category=college"
```

---

### GET /api/v1/test/questions

Вопросы профориентационного теста.

**cURL:**
```bash
curl -X GET http://localhost:8000/api/v1/test/questions
```

---

### POST /api/v1/test/results

Отправка ответов теста.

**cURL:**
```bash
curl -X POST http://localhost:8000/api/v1/test/results \
  -H "Content-Type: application/json" \
  -d '{
    "answers": [
      {"question_id": 1, "selected": 0},
      {"question_id": 2, "selected": 1},
      {"question_id": 3, "selected": 2},
      {"question_id": 4, "selected": 3},
      {"question_id": 5, "selected": 0},
      {"question_id": 6, "selected": 1},
      {"question_id": 7, "selected": 2},
      {"question_id": 8, "selected": 0},
      {"question_id": 9, "selected": 3},
      {"question_id": 10, "selected": 1}
    ]
  }'
```

**Ответ (200 OK):**
```json
{
  "recommendation": "На основе ваших ответов, рекомендуем специальность:",
  "motivation": "Вы проявляете интерес к техническим дисциплинам...",
  "recommended_specialties": [
    {
      "code": "15.02.19",
      "name": "Технология аддитивного производства",
      "score": 15
    },
    {
      "code": "21.02.03",
      "name": "Монтаж и техническая эксплуатация",
      "score": 12
    },
    {
      "code": "09.02.07",
      "name": "Информационные системы и программирование",
      "score": 8
    }
  ]
}
```

---

## Админ-эндпоинты

> **Требуют JWT-аутентификации.** Замените `TOKEN` на ваш access_token.

### Управление пользователями

#### GET /admin/users

**cURL:**
```bash
curl -X GET "http://localhost:8000/admin/users?page=1&limit=10" \
  -H "Authorization: Bearer $TOKEN"
```

#### PATCH /admin/users/{id}

**cURL:**
```bash
curl -X PATCH http://localhost:8000/admin/users/1 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newemail@example.com",
    "is_superuser": true
  }'
```

#### DELETE /admin/users/{id}

**cURL:**
```bash
curl -X DELETE http://localhost:8000/admin/users/2 \
  -H "Authorization: Bearer $TOKEN"
```

---

### Управление специальностями

#### POST /admin/specialties

**cURL (form-data):**
```bash
curl -X POST http://localhost:8000/admin/specialties \
  -H "Authorization: Bearer $TOKEN" \
  -F "code=99.99.99" \
  -F "name=Тестовая специальность" \
  -F "short_description=Краткое описание" \
  -F 'description=["Параграф 1", "Параграф 2"]' \
  -F 'exams=["Экзамен 1", "Экзамен 2"]' \
  -F 'education_options=[{"education_level":"9 классов","duration":"3г 10м","budget_places":25,"paid_places":10}]'
```

#### PUT /admin/specialties/{id}

**cURL:**
```bash
curl -X PUT http://localhost:8000/admin/specialties/1 \
  -H "Authorization: Bearer $TOKEN" \
  -F "code=09.02.07" \
  -F "name=Обновлённое название" \
  -F "short_description=Обновлённое описание"
```

#### DELETE /admin/specialties/{id}

**cURL:**
```bash
curl -X DELETE http://localhost:8000/admin/specialties/1 \
  -H "Authorization: Bearer $TOKEN"
```

---

### Загрузка файлов

#### POST /admin/upload/image

**cURL:**
```bash
curl -X POST "http://localhost:8000/admin/upload/image?category=news" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@photo.jpg"
```

#### POST /admin/upload/document

**cURL:**
```bash
curl -X POST "http://localhost:8000/admin/upload/document?category=licenses" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@license.pdf"
```

---

### Управление кэшем

#### GET /admin/cache/stats

**cURL:**
```bash
curl -X GET http://localhost:8000/admin/cache/stats \
  -H "Authorization: Bearer $TOKEN"
```

**Ответ (200 OK):**
```json
{
  "available": true,
  "keys_count": 42,
  "used_memory": "1.23M",
  "used_memory_peak": "2.45M"
}
```

#### POST /admin/cache/clear

**cURL:**
```bash
curl -X POST http://localhost:8000/admin/cache/clear \
  -H "Authorization: Bearer $TOKEN"
```

---

## Python примеры

### Полный сценарий (регистрация → вход → CRUD)

```python
import httpx
import asyncio

async def main():
    base_url = "http://localhost:8000"
    
    async with httpx.AsyncClient(base_url=base_url) as client:
        # 1. Регистрация
        register_response = await client.post(
            "/auth/register",
            json={
                "email": "test@example.com",
                "username": "testuser",
                "password": "Str0ng!Pass123"
            }
        )
        print("Регистрация:", register_response.json())
        
        # 2. Вход
        login_response = await client.post(
            "/auth/login",
            json={
                "username": "testuser",
                "password": "Str0ng!Pass123"
            }
        )
        tokens = login_response.json()
        token = tokens["access_token"]
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # 3. Создание специальности
        specialty_response = await client.post(
            "/admin/specialties",
            headers=headers,
            data={
                "code": "99.99.99",
                "name": "Тестовая специальность",
                "short_description": "Краткое описание",
                "description": '["Параграф 1"]',
                "exams": '["Экзамен 1"]',
                "education_options": '[{"education_level":"9 классов","duration":"3г","budget_places":25,"paid_places":10}]'
            }
        )
        print("Создание специальности:", specialty_response.json())
        
        # 4. Получение списка специальностей
        specialties_response = await client.get(
            "/admin/specialties?page=1&limit=10",
            headers=headers
        )
        print("Список специальностей:", specialties_response.json())
        
        # 5. Загрузка изображения
        with open("test.jpg", "rb") as f:
            files = {"file": ("test.jpg", f, "image/jpeg")}
            upload_response = await client.post(
                "/admin/upload/image?category=test",
                headers=headers,
                files=files
            )
            print("Загрузка изображения:", upload_response.json())
        
        # 6. Выход
        logout_response = await client.post(
            "/auth/logout",
            json={"refresh_token": tokens["refresh_token"]}
        )
        print("Выход:", logout_response.json())

asyncio.run(main())
```

---

## JavaScript (fetch) примеры

### Получение списка специальностей

```javascript
async function getSpecialties(page = 1, limit = 10) {
  const response = await fetch(
    `/api/v1/specialties?page=${page}&limit=${limit}`
  );
  
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
  }
  
  return response.json();
}

// Использование
getSpecialties()
  .then(data => console.log(`Найдено ${data.total} специальностей`))
  .catch(err => console.error(err));
```

### Создание новости с авторизацией

```javascript
async function createNews(newsData) {
  const token = localStorage.getItem('access_token');
  
  const response = await fetch('/admin/news', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: new URLSearchParams({
      title: newsData.title,
      slug: newsData.slug,
      preview_text: newsData.preview_text,
      content: JSON.stringify(newsData.content),
    })
  });
  
  return response.json();
}

// Использование
createNews({
  title: 'День открытых дверей',
  slug: 'open-day-2025',
  preview_text: 'Приглашаем на день открытых дверей...',
  content: ['Первый абзац', 'Второй абзац']
})
  .then(data => console.log('Новость создана:', data))
  .catch(err => console.error(err));
```

---

## Postman коллекция

### Импорт в Postman

1. Открыть Postman
2. **Import** → **Paste raw text**
3. Вставить JSON коллекцию (см. ниже)
4. Нажать **Import**

### Postman Collection (JSON)

```json
{
  "info": {
    "name": "Anmicius API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Health Check",
      "request": {
        "method": "GET",
        "header": [],
        "url": {
          "raw": "{{base_url}}/health",
          "host": ["{{base_url}}"],
          "path": ["health"]
        }
      }
    },
    {
      "name": "Login",
      "request": {
        "method": "POST",
        "header": [
          {"key": "Content-Type", "value": "application/json"}
        ],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"username\": \"admin\",\n  \"password\": \"Str0ng!Pass123\"\n}"
        },
        "url": {
          "raw": "{{base_url}}/auth/login",
          "host": ["{{base_url}}"],
          "path": ["auth", "login"]
        }
      }
    },
    {
      "name": "Get Specialties",
      "request": {
        "method": "GET",
        "header": [],
        "url": {
          "raw": "{{base_url}}/api/v1/specialties?page=1&limit=10",
          "host": ["{{base_url}}"],
          "path": ["api", "v1", "specialties"],
          "query": [
            {"key": "page", "value": "1"},
            {"key": "limit", "value": "10"}
          ]
        }
      }
    }
  ],
  "variable": [
    {
      "key": "base_url",
      "value": "http://localhost:8000"
    }
  ]
}
```

---

## HTTPie примеры

### Установка

```bash
pip install httpie
```

### Примеры

```bash
# Health check
http GET http://localhost:8000/health

# Login
http POST http://localhost:8000/auth/login \
  username=admin password=Str0ng!Pass123

# Get specialties (с токеном)
http GET http://localhost:8000/api/v1/specialties \
  Authorization:"Bearer $TOKEN"

# Create specialty
http --form POST http://localhost:8000/admin/specialties \
  Authorization:"Bearer $TOKEN" \
  code=99.99.99 name="Тест" short_description="Описание"
```

---

## Связанные документы

- [Публичные эндпоинты](./public-endpoints.md) — полное описание
- [Админ-эндпоинты](./admin-endpoints.md) — CRUD операции
- [Аутентификация](./authentication.md) — JWT токены
- [Обработка ошибок](./errors.md) — коды ответов
