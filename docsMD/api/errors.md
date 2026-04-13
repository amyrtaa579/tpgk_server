# Обработка ошибок и исключения

API использует единую систему обработки ошибок через **кастомные исключения** и **глобальные обработчики** FastAPI.

## Обзор

Все ошибки возвращаются в **едином формате JSON** с полями `detail` и `status_code`.

---

## Формат ответа об ошибке

### Стандартная ошибка

```json
{
  "detail": "Описание ошибки",
  "status_code": 404
}
```

### Ошибка валидации (Pydantic)

```json
{
  "detail": "body.title: Field required; body.slug: Field required",
  "status_code": 422
}
```

### Внутренняя ошибка сервера

```json
{
  "detail": "Внутренняя ошибка сервера",
  "status_code": 500
}
```

---

## Кастомные исключения

Определены в `app/core/exceptions.py`.

### Иерархия исключений

```
Exception
  └── AppException (500)
       ├── NotFoundException (404)
       ├── BadRequestException (400)
       └── ValidationException (422)
```

### AppException

Базовый класс для всех кастомных исключений.

```python
class AppException(Exception):
    """Базовое исключение приложения."""
    
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(message)
```

### NotFoundException (404)

Ресурс не найден.

**Примеры использования:**
- Специальность не найдена по коду
- Новость не найдена по ID
- Пользователь не найден

```python
raise NotFoundException("Специальность с кодом 09.02.07 не найдена")
```

**Ответ:**
```json
{
  "detail": "Специальность с кодом 09.02.07 не найдена",
  "status_code": 404
}
```

### BadRequestException (400)

Некорректный запрос.

**Примеры использования:**
- Недопустимый тип файла
- Размер файла превышает лимит
- Дубликат уникального поля

```python
raise BadRequestException("Недопустимый тип файла. Разрешены: JPEG, PNG, GIF, WebP")
```

**Ответ:**
```json
{
  "detail": "Недопустимый тип файла. Разрешены: JPEG, PNG, GIF, WebP",
  "status_code": 400
}
```

### ValidationException (422)

Ошибка валидации данных.

**Примеры использования:**
- Неверный формат email
- Пароль не соответствует требованиям
- Неверный формат даты

```python
raise ValidationException("Неверный формат email")
```

---

## Глобальные обработчики исключений

Зарегистрированы в `main.py`.

### Обработчик AppException

```python
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message, "status_code": exc.status_code},
    )
```

### Обработчик RequestValidationError (Pydantic)

```python
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for error in exc.errors():
        errors.append(f"{error['loc']}: {error['msg']}")
    return JSONResponse(
        status_code=422,
        content={"detail": "; ".join(errors), "status_code": 422},
    )
```

### Обработчик общих исключений

```python
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error("Необработанное исключение", error=str(exc))
    return JSONResponse(
        status_code=500,
        content={"detail": "Внутренняя ошибка сервера", "status_code": 500},
    )
```

### Обработчик RateLimitExceeded (SlowAPI)

```python
app.add_exception_handler(
    RateLimitExceeded, 
    get_rate_limit_exception_handler()
)
```

---

## Коды ответов HTTP

### Успешные ответы

| Код | Описание | Пример |
|-----|----------|--------|
| 200 | OK | Успешный GET/PUT |
| 201 | Created | Успешный POST (создание) |

### Ошибки клиента (4xx)

| Код | Название | Описание | Пример |
|-----|----------|----------|--------|
| 400 | Bad Request | Некорректный запрос | Недопустимый тип файла |
| 401 | Unauthorized | Не авторизован | Отсутствует или неверный токен |
| 403 | Forbidden | Недостаточно прав | Нет scope для операции |
| 404 | Not Found | Ресурс не найден | Специальность не найдена |
| 409 | Conflict | Конфликт | Дубликат уникального поля |
| 422 | Unprocessable Entity | Ошибка валидации | Неверный формат email |
| 429 | Too Many Requests | Превышен лимит | Brute-force защита |

### Ошибки сервера (5xx)

| Код | Название | Описание | Пример |
|-----|----------|----------|--------|
| 500 | Internal Server Error | Внутренняя ошибка | Ошибка БД, необработанное исключение |
| 503 | Service Unavailable | Сервис недоступ | Health check failed |

---

## Примеры ошибок по эндпоинтам

### Аутентификация

#### POST /auth/login

| Код | Описание |
|-----|----------|
| 400 | Неверный формат запроса |
| 401 | Неверный username/password |
| 429 | Превышен лимит запросов |

**Пример (401):**
```json
{
  "detail": "Неверный username или пароль",
  "status_code": 401
}
```

#### POST /auth/register

| Код | Описание |
|-----|----------|
| 400 | Email/username уже существует |
| 400 | Пароль не соответствует требованиям |
| 422 | Ошибка валидации Pydantic |
| 429 | Превышен лимит запросов |

**Пример (400):**
```json
{
  "detail": "Email уже зарегистрирован",
  "status_code": 400
}
```

**Пример (422):**
```json
{
  "detail": "body.password: Пароль не соответствует требованиям: Минимум 12 символа, Минимум 1 заглавная буква, Минимум 1 цифра",
  "status_code": 422
}
```

### Публичные эндпоинты

#### GET /api/v1/specialties/{code}

| Код | Описание |
|-----|----------|
| 404 | Специальность не найдена |

**Пример (404):**
```json
{
  "detail": "Специальность с кодом 99.99.99 не найдена",
  "status_code": 404
}
```

#### POST /api/v1/test/results

| Код | Описание |
|-----|----------|
| 422 | Неверное количество ответов (должно быть 10) |

**Пример (422):**
```json
{
  "detail": "Необходимо ровно 10 ответов, получено: 9",
  "status_code": 422
}
```

### Админ-эндпоинты

#### POST /admin/specialties

| Код | Описание |
|-----|----------|
| 400 | Код специальности уже существует |
| 401 | Не авторизован |
| 403 | Недостаточно прав |
| 422 | Ошибка валидации |

**Пример (400):**
```json
{
  "detail": "Специальность с кодом '09.02.07' уже существует",
  "status_code": 400
}
```

#### POST /admin/upload/image

| Код | Описание |
|-----|----------|
| 400 | Недопустимый тип файла |
| 400 | Размер файла превышает лимит |
| 401 | Не авторизован |

**Пример (400):**
```json
{
  "detail": "Недопустимый тип файла. Разрешены: JPEG, PNG, GIF, WebP",
  "status_code": 400
}
```

---

## Валидация Pydantic

### Формат ошибки

```
{location}.{field}: {message}; {location}.{field}: {message}
```

**Пример:**
```
body.title: Field required; body.slug: Field required
```

### Расположение ошибок (location)

| Location | Описание |
|----------|----------|
| `body` | Тело запроса (JSON) |
| `query` | Параметры строки запроса |
| `path` | Параметры пути |

### Примеры

**Отсутствующее обязательное поле:**
```json
{
  "detail": "body.title: Field required",
  "status_code": 422
}
```

**Неверный тип данных:**
```json
{
  "detail": "body.page: Input should be a valid integer",
  "status_code": 422
}
```

**Ошибка кастомного валидатора:**
```json
{
  "detail": "body.email: Неверный формат email",
  "status_code": 422
}
```

---

## JWT-ошибки

### 401 Unauthorized

| Ситуация | Описание |
|----------|----------|
| Отсутствует заголовок `Authorization` | "Not authenticated" |
| Неверный формат токена | "Could not validate credentials" |
| Токен истёк | "Token has expired" |
| Неверная подпись | "Invalid token" |

**Пример:**
```json
{
  "detail": "Could not validate credentials",
  "status_code": 401
}
```

### 403 Forbidden

| Ситуация | Описание |
|----------|----------|
| Недостаточно scopes | "Not enough permissions" |
| Требуется суперпользователь | "Superuser required" |
| Пользователь не активен | "User is not active" |

**Пример:**
```json
{
  "detail": "Superuser required",
  "status_code": 403
}
```

---

## Логирование ошибок

### Структурное логирование (Structlog)

Все ошибки логируются с контекстом:

```python
logger.error("Необработанное исключение", error=str(exc))
```

**Пример лога:**
```json
{
  "event": "Необработанное исключение",
  "error": "Connection refused",
  "timestamp": "2025-01-15T10:30:00Z"
}
```

---

## Обработка ошибок в клиенте

### Python (httpx)

```python
import httpx

async def get_specialty(code: str, token: str):
    async with httpx.AsyncClient(base_url="https://api.anmicius.ru") as client:
        try:
            response = await client.get(
                f"/api/v1/specialties/{code}",
                headers={"Authorization": f"Bearer {token}"}
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                print(f"Специальность {code} не найдена")
            elif e.response.status_code == 401:
                print("Необходимо авторизоваться")
            else:
                print(f"Ошибка: {e.response.status_code} - {e.response.text}")
```

### JavaScript (fetch)

```javascript
async function getSpecialty(code) {
  const response = await fetch(`/api/v1/specialties/${code}`);
  
  if (!response.ok) {
    const error = await response.json();
    
    switch (response.status) {
      case 404:
        console.error(`Специальность ${code} не найдена: ${error.detail}`);
        break;
      case 429:
        console.error('Превышен лимит запросов, подождите');
        break;
      default:
        console.error(`Ошибка ${response.status}: ${error.detail}`);
    }
    
    throw new Error(error.detail);
  }
  
  return response.json();
}
```

---

## Рекомендации

### Для клиентов API

1. **Всегда проверяйте коды ответов** и обрабатывайте ошибки
2. **Реализуйте retry-логику** с exponential backoff для 429 и 5xx ошибок
3. **Логируйте `detail`** для отладки
4. **Показывайте пользователю** человеко-читаемые сообщения

### Для разработчиков API

1. **Используйте кастомные исключения** для бизнес-логики
2. **Не возвращайте stack trace** в production
3. **Логируйте контекст** ошибки (user_id, request_id, etc.)
4. **Документируйте все возможные ошибки** в API-документации

---

## Связанные документы

- [Rate Limiting](./rate-limiting.md) — ошибки 429
- [Аутентификация](./authentication.md) — ошибки 401/403
- [Публичные эндпоинты](./public-endpoints.md) — возможные ошибки эндпоинтов
