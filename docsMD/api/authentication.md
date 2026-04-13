# Аутентификация и авторизация

API использует **JWT (JSON Web Tokens)** для аутентификации и **OAuth2 Password Bearer** для интеграции со Swagger UI.

## Механизм аутентификации

### Обзор

```
┌──────────┐    POST /auth/login     ┌──────────────────────┐
│  Клиент   │ ──────────────────────► │        API           │
│          │ ◄────────────────────── │                      │
└──────────┘   access_token +         │ 1. Проверка логина    │
              refresh_token            │ 2. Проверка пароля    │
                                       │ 3. Создание токенов   │
                                       │ 4. Сохранение refresh │
                                       └──────────────────────┘
```

### Параметры JWT

| Параметр | Значение |
|----------|----------|
| **Алгоритм** | HS256 |
| **Access Token TTL** | 24 часа |
| **Refresh Token TTL** | 30 дней |
| **Хэширование паролей** | bcrypt, 12 rounds |

## Эндпоинты аутентификации

### POST /auth/register

Регистрация нового пользователя.

**Тело запроса:**
```json
{
  "email": "user@example.com",
  "username": "username",
  "password": "Str0ng!Pass123"
}
```

**Требования к паролю:**
- Минимум 12 символов
- Минимум 1 заглавная буква
- Минимум 1 строчная буква
- Минимум 1 цифра
- Минимум 1 специальный символ

**Требования к email:**
- Валидный формат (regex: `^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`)

**Ответ (200 OK):**
```json
{
  "id": 5,
  "email": "user@example.com",
  "username": "username",
  "is_active": true,
  "is_superuser": false
}
```

**Валидации:**
- Email должен быть уникальным
- Username должен быть уникальным (3-50 символов)
- Пароль должен соответствовать требованиям сложности

---

### POST /auth/login

Вход в систему.

**Тело запроса:**
```json
{
  "username": "admin",
  "password": "Str0ng!Pass123"
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

**Rate Limiting:** 10 запросов/минуту, 30/час (защита от брутфорса)

**Логика:**
1. Проверка username/password
2. Создание access токена (24ч) с scopes
3. Создание refresh токена (30д)
4. Сохранение refresh токена в БД (таблица `refresh_tokens`)

**Scopes при входе:**

| Роль | Scopes |
|------|--------|
| **Суперпользователь** | Все: `users:read`, `users:write`, `specialties:read`, `specialties:write`, `news:read`, `news:write`, `facts:read`, `facts:write`, `upload:write` |
| **Обычный пользователь** | Только чтение: `users:read`, `specialties:read`, `news:read`, `facts:read` |

---

### POST /auth/login/oauth

OAuth2-совместимый эндпоинт для Swagger UI.

**Content-Type:** `application/x-www-form-urlencoded`

**Тело:**
```
username=admin&password=Str0ng!Pass123
```

**Ответ:**
```json
{
  "access_token": "eyJhbGci...",
  "token_type": "bearer"
}
```

Используется автоматически при нажатии кнопки **Authorize** в Swagger UI (`/docs`).

---

### POST /auth/refresh

Обновление access токена.

**Тело запроса:**
```json
{
  "refresh_token": "eyJhbGci..."
}
```

**Ответ (200 OK):**
```json
{
  "access_token": "eyJhbGci...новый...",
  "refresh_token": "eyJhbGci...новый...",
  "token_type": "bearer"
}
```

**Логика:**
1. Проверка refresh токена в БД
2. Проверка срока действия (`expires_at`)
3. Создание новой пары токенов
4. Удаление старого refresh токена

**Rate Limiting:** 30/мин, 100/час

---

### POST /auth/logout

Выход из системы.

**Тело запроса:**
```json
{
  "refresh_token": "eyJhbGci..."
}
```

**Ответ (200 OK):**
```json
{
  "message": "Выход выполнен успешно"
}
```

**Логика:** Удаление refresh токена из БД.

---

### GET /auth/me

Получение информации о текущем пользователе.

**Заголовки:**
```
Authorization: Bearer <access_token>
```

**Ответ (200 OK):**
```json
{
  "id": 1,
  "email": "admin@anmicius.ru",
  "username": "admin",
  "is_active": true,
  "is_superuser": true
}
```

---

## Использование токенов

### В заголовке запроса

```bash
curl -X GET https://api.anmicius.ru/admin/users \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### В Swagger UI

1. Открыть `https://api.anmicius.ru/docs`
2. Нажать **Authorize** 🔓
3. Ввести username и password
4. Нажать **Authorize** → **Close**
5. Все запросы из Swagger будут автоматически включать токен

---

## Структура JWT Payload

```json
{
  "sub": "1",                    // user_id (string)
  "scopes": [                    // области доступа
    "users:read",
    "users:write",
    "specialties:read",
    "specialties:write",
    "news:read",
    "news:write",
    "facts:read",
    "facts:write",
    "upload:write"
  ],
  "exp": 1713024000,             // expiration timestamp
  "iat": 1712937600              // issued at timestamp
}
```

### Проверка scopes

Каждый админ-эндпоинт требует определённый scope:

```python
@router.post("/specialties")
async def create_specialty(
    current_user: User = Depends(get_current_user),  # проверяет токен
    # ...
):
    # get_current_user автоматически проверяет scopes
```

---

## Flow диаграмма

### Полный цикл аутентификации

```
┌─────────┐                          ┌─────────┐
│ Клиент   │                          │  Сервер  │
└────┬─────┘                          └────┬────┘
     │                                     │
     │  POST /auth/register                │
     │  {email, username, password}        │
     │ ─────────────────────────────────► │
     │                                     │ Валидация, хэширование
     │                                     │ Создание пользователя
     │  200 {id, email, username}          │
     │ ◄───────────────────────────────── │
     │                                     │
     │  POST /auth/login                   │
     │  {username, password}               │
     │ ─────────────────────────────────► │
     │                                     │ Проверка пароля
     │                                     │ Создание JWT + refresh
     │  200 {access_token, refresh_token}  │
     │ ◄───────────────────────────────── │
     │                                     │
     │  GET /admin/users                   │
     │  Authorization: Bearer access_token │
     │ ─────────────────────────────────► │
     │                                     │ Проверка токена, scopes
     │  200 {items: [...]}                 │
     │ ◄───────────────────────────────── │
     │                                     │
     │  (через 24 часа токен истёк)        │
     │                                     │
     │  POST /auth/refresh                 │
     │  {refresh_token}                    │
     │ ─────────────────────────────────► │
     │                                     │ Проверка, новая пара
     │  200 {new_access, new_refresh}      │
     │ ◄───────────────────────────────── │
     │                                     │
     │  POST /auth/logout                  │
     │  {refresh_token}                    │
     │ ─────────────────────────────────► │
     │                                     │ Удаление из БД
     │  200 {message}                      │
     │ ◄───────────────────────────────── │
```

---

## FastAPI зависимости (DI)

### `get_current_user_id`

Извлекает `user_id` из JWT токена.

```python
async def get_current_user_id(
    token: str = Depends(oauth2_scheme)
) -> int:
    payload = decode_token(token)
    verify_scopes(payload, required_scopes)
    return int(payload["sub"])
```

### `get_current_user`

Загружает пользователя из БД.

```python
async def get_current_user(
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_db_session),
) -> User:
    user = await user_repo.get_by_id(user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=401)
    return user
```

### `get_current_superuser`

Проверяет суперпользователя.

```python
async def get_current_superuser(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Superuser required")
    return current_user
```

---

## Безопасность

### Хранение паролей

```python
import bcrypt

def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(
        password.encode('utf-8'),
        bcrypt.gensalt(rounds=12)
    ).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode('utf-8'),
        hashed_password.encode('utf-8')
    )
```

### Валидация паролей

```python
def validate_password(password: str) -> tuple[bool, list[str]]:
    errors = []
    if len(password) < 12:
        errors.append("Минимум 12 символа")
    if not re.search(r'[A-Z]', password):
        errors.append("Минимум 1 заглавная буква")
    if not re.search(r'[a-z]', password):
        errors.append("Минимум 1 строчная буква")
    if not re.search(r'\d', password):
        errors.append("Минимум 1 цифра")
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        errors.append("Минимум 1 специальный символ")
    return len(errors) == 0, errors
```

### Обновление пароля

При изменении пароля пользователя **все refresh токены аннулируются**:

```python
async def update_user(user_id: int, update_data: UserUpdateSchema):
    if update_data.password:
        user.hashed_password = get_password_hash(update_data.password)
        # Аннулировать все refresh токены
        await refresh_token_repo.delete_by_user_id(user_id)
```

---

## Настройка OAuth2 для Swagger

```python
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="auth/login/oauth",
    scopes={
        "users:read": "Просмотр пользователей",
        "users:write": "Редактирование пользователей",
        "specialties:read": "Просмотр специальностей",
        "specialties:write": "Редактирование специальностей",
        "news:read": "Просмотр контента",
        "news:write": "Редактирование контента",
        "facts:read": "Просмотр фактов",
        "facts:write": "Редактирование фактов",
        "upload:write": "Загрузка файлов",
    }
)
```

---

## Возможные ошибки

| Код | Описание | Решение |
|-----|----------|---------|
| 400 | Неверный формат запроса | Проверить тело запроса |
| 400 | Email/username уже существует | Использовать другие значения |
| 400 | Пароль не соответствует требованиям | Усилить пароль |
| 401 | Неверный username/password | Проверить учётные данные |
| 401 | Токен истёк | Использовать `/auth/refresh` |
| 401 | Неверный refresh токен | Повторно войти через `/auth/login` |
| 403 | Недостаточно scopes | Обратиться к администратору |
| 422 | Ошибка валидации JWT | Проверить формат токена |
| 429 | Превышен лимит запросов | Подождать и повторить |
