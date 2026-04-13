# Rate Limiting (Ограничение запросов)

API использует **SlowAPI** для ограничения частоты запросов, что защищает сервис от злоупотреблений, brute-force атак и чрезмерной нагрузки.

## Обзор

| Параметр | Значение |
|----------|----------|
| **Библиотека** | SlowAPI 0.1.8 |
| **Стратегия** | Fixed Window |
| **Идентификатор** | IP-адрес клиента |
| **Хранилище** | In-memory |

---

## Лимиты запросов

Разные эндпоинты имеют разные лимиты в зависимости от их критичности.

### Аутентификация (`/auth/*`)

Строгие лимиты для защиты от brute-force атак.

| Лимит | Значение | Описание |
|-------|----------|----------|
| В минуту | 10 запросов | Краткосрочная защита |
| В час | 30 запросов | Долгосрочная защита |

**Эндпоинты:**
- `POST /auth/login`
- `POST /auth/register`
- `POST /auth/login/oauth`
- `POST /auth/refresh`

### Остальные эндпоинты

Стандартные лимиты для обычных запросов.

| Лимит | Значение | Описание |
|-------|----------|----------|
| В минуту | 60 запросов | Краткосрочная защита |
| В час | 1000 запросов | Долгосрочная защита |

**Эндпоинты:**
- Все публичные эндпоинты (`/api/v1/*`)
- Все админ-эндпоинты (`/admin/*`)
- Health check (`/health`)

---

## Превышение лимита

### Код ответа

При превышении лимита возвращается **HTTP 429 Too Many Requests**.

### Формат ответа

```json
{
  "detail": "Слишком много запросов",
  "message": "Превышен лимит запросов. Попробуйте позже."
}
```

### Заголовки ответа

Сервер не возвращает заголовки `Retry-After` или `X-RateLimit-*` (настраивается).

---

## Примеры

### Нормальный запрос

```bash
curl -X POST https://api.anmicius.ru/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"secret"}'
```

**Ответ (200 OK):**
```json
{
  "access_token": "eyJhbGci...",
  "refresh_token": "eyJhbGci...",
  "token_type": "bearer"
}
```

### Превышение лимита

После 10 запросов в минуту к `/auth/login`:

**Ответ (429 Too Many Requests):**
```json
{
  "detail": "Слишком много запросов",
  "message": "Превышен лимит запросов. Попробуйте позже."
}
```

---

## Реализация

### Конфигурация SlowAPI

Расположена в `app/core/rate_limiter.py`.

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

# Инициализация лимитера
limiter = Limiter(key_func=get_remote_address)
```

**`key_func`** — функция для определения идентификатора клиента. По умолчанию используется IP-адрес (`get_remote_address`).

### Настройка лимитов

```python
def get_rate_limit_limits() -> dict:
    """Получить настройки rate limiting."""
    return {
        # Auth endpoints - строгие лимиты для защиты от brute-force
        "auth_per_minute": "10/minute",
        "auth_per_hour": "30/hour",
        # Общие лимиты
        "default_per_minute": "60/minute",
        "default_per_hour": "1000/hour",
    }
```

### Обработчик исключений

```python
async def rate_limit_exception_handler(
    request: Request, 
    exc: RateLimitExceeded
) -> JSONResponse:
    """Обработчик превышения rate limit."""
    return JSONResponse(
        status_code=429,
        content={
            "detail": "Слишком много запросов",
            "message": "Превышен лимит запросов. Попробуйте позже.",
        },
    )
```

Регистрация обработчика в `main.py`:

```python
app.add_exception_handler(
    RateLimitExceeded, 
    get_rate_limit_exception_handler()
)
```

### Использование декоратора

```python
@router.post("/login")
@limiter.limit("10/minute;30/hour")  # Декоратор лимита
async def login(
    request: Request,  # Обязателен для SlowAPI
    credentials: LoginSchema,
    session: AsyncSession = Depends(get_db_session),
):
    # Логика аутентификации
```

---

## Переменные окружения

Настройки Rate Limiting **не** загружаются из `.env`. Они захардкожены в `app/core/rate_limiter.py`.

Для изменения лимитов необходимо изменить код напрямую.

---

## Обходные пути

### Для тестирования

При тестировании можно временно отключить Rate Limiting:

```python
# В .slowapi.env
ENV_FILE=""  # Отключает поиск .env файла
```

### Для доверенных IP

В текущей реализации **нет** белых списков IP. Все клиенты подчиняются одним и тем же лимитам.

**Рекомендация:** Для production добавить middleware для whitelist IP.

---

## Рекомендации для Production

1. **Используйте Redis** для хранения счётчиков (вместо in-memory)
   - Позволяет шардировать лимиты across multiple instances
   - Сохраняет счётчики при перезапуске приложения

2. **Настройте заголовки** `X-RateLimit-*`:
   ```python
   limiter = Limiter(
       key_func=get_remote_address,
       headers_enabled=True
   )
   ```

3. **Добавьте whitelist** для внутренних сервисов (мониторинг, CI/CD)

4. **Мониторинг** частоты 429 ответов для выявления атак

5. **Уведомления** при частом превышении лимитов

---

## Диагностика

### Проверка текущих лимитов

Посмотрите логи SlowAPI (при `DEBUG=true`):

```bash
docker-compose logs api | grep rate
```

### Тестирование лимитов

```bash
# Отправить 15 запросов подряд
for i in {1..15}; do
  curl -s -o /dev/null -w "%{http_code}\n" \
    -X POST https://api.anmicius.ru/auth/login \
    -H "Content-Type: application/json" \
    -d '{"username":"test","password":"wrong"}'
done
```

Ожидаемый результат:
```
401
401
...
429  <- Начиная с 11-го запроса
429
```

---

## Troubleshooting

### Все запросы блокируются (429)

**Причина:** Превышен лимит из-за общего IP (NAT, прокси).

**Решение:** 
- Подождите сброса окна (1 минута или 1 час)
- Обратитесь к администратору для увеличения лимитов

### Лимиты не работают

**Причина:** SlowAPI не инициализирован или middleware не добавлен.

**Решение:**
```bash
# Проверьте main.py
grep "slowapi" app/main.py
```

### Разные клиенты имеют один IP

**Причина:** Клиенты находятся за NAT или reverse proxy.

**Решение:** Настройте определение реального IP через заголовок `X-Forwarded-For`:

```python
from slowapi.util import get_remote_address

def get_real_ip(request: Request) -> str:
    """Получить реальный IP из X-Forwarded-For."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return get_remote_address(request)

limiter = Limiter(key_func=get_real_ip)
```

---

## Связанные документы

- [Аутентификация](./authentication.md) — эндпоинты с строгими лимитами
- [Обработка ошибок](./errors.md) — коды ответов, включая 429
- [Безопасность](./deployment.md#безопасность) — рекомендации для production
