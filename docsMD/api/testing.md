# Тестирование API

Проект использует **pytest** и **httpx** для автоматизированного тестирования, включая unit-тесты и интеграционные тесты.

## Обзор

| Параметр | Значение |
|----------|----------|
| **Фреймворк** | pytest 7.4.4 |
| **HTTP клиент** | httpx 0.26.0 |
| **Асинхронность** | pytest-asyncio |
| **Режим asyncio** | `auto` |
| **Конфигурация** | `pytest.ini` |
| **Директория тестов** | `tests/` |

---

## Структура тестов

```
tests/
├── __init__.py
├── conftest.py           # Общие фикстуры
├── test_api.py           # Тесты публичных эндпоинтов (~990 строк)
├── test_auth.py          # Тесты аутентификации и админки (~412 строк)
└── test_integration.py   # Интеграционные тесты (~232 строки)
```

### Тестовые файлы

| Файл | Описание | Строк |
|------|----------|-------|
| `test_api.py` | Публичные эндпоинты: health, about, specialties, news, FAQ, test | ~990 |
| `test_auth.py` | Auth: регистрация, вход, refresh, logout, admin CRUD | ~412 |
| `test_integration.py` | Интеграция с реальным запущенным API | ~232 |

---

## Запуск тестов

### Все тесты

```bash
pytest
```

**Или с подробным выводом:**
```bash
pytest -v
```

### Отдельные файлы

```bash
# Только публичные эндпоинты
pytest tests/test_api.py

# Только аутентификация
pytest tests/test_auth.py

# Только интеграционные тесты
pytest tests/test_integration.py
```

### Отдельный тест

```bash
# Конкретный класс тестов
pytest tests/test_api.py::TestSpecialties

# Конкретный тест
pytest tests/test_api.py::TestSpecialties::test_get_specialties_success
```

### С отчётом о покрытии

```bash
# Установка pytest-cov
pip install pytest-cov

# Запуск с покрытием
pytest --cov=app --cov-report=html

# Или только покрытие конкретного модуля
pytest --cov=app/presentation --cov-report=term-missing
```

---

## Конфигурация pytest

### pytest.ini

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
asyncio_mode = auto
addopts = -v --tb=short
```

**Параметры:**
- `asyncio_mode = auto` — автоматическое определение асинхронных тестов
- `-v` — подробный вывод
- `--tb=short` — краткий traceback при ошибках

---

## Фикстуры

Фикстуры определены в `tests/conftest.py` и обеспечивают изолированное тестовое окружение.

### Основные фикстуры

#### client

Асинхронный HTTP-клиент для тестового API.

```python
@pytest.fixture
async def client() -> AsyncClient:
    """Создание тестового HTTP клиента."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
```

#### test_session

Сессия базы данных для тестов.

```python
@pytest.fixture
async def test_session() -> AsyncSession:
    """Создание тестовой сессии БД."""
    async with async_session_maker() as session:
        yield session
        # Cleanup после теста
```

#### auth_token

JWT-токен для авторизованных запросов.

```python
@pytest.fixture
async def auth_token(client: AsyncClient, test_session: AsyncSession) -> str:
    """Создание тестового пользователя и получение токена."""
    # Создание пользователя
    # Вход и возврат access_token
```

---

## Примеры тестов

### Unit-тест: Публичный эндпоинт

```python
class TestSpecialties:
    """Тесты для /api/v1/specialties."""

    async def test_get_specialties_success(self, client: AsyncClient):
        """Успешное получение списка специальностей."""
        response = await client.get("/api/v1/specialties")

        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "limit" in data
        assert "pages" in data

    async def test_get_specialties_pagination(self, client: AsyncClient):
        """Проверка пагинации."""
        response = await client.get("/api/v1/specialties?page=2&limit=5")

        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 2
        assert data["limit"] == 5

    async def test_get_specialties_search(self, client: AsyncClient):
        """Проверка поиска специальностей."""
        response = await client.get("/api/v1/specialties?search=программ")

        assert response.status_code == 200
        data = response.json()
        for item in data["items"]:
            assert "программ" in item["name"].lower() or "программ" in item["short_description"].lower()
```

### Unit-тест: Аутентификация

```python
class TestAuth:
    """Тесты для аутентификации."""

    async def test_register_user(self, client: AsyncClient, test_session: AsyncSession):
        """Регистрация нового пользователя."""
        response = await client.post(
            "/auth/register",
            json={
                "email": "test@example.com",
                "username": "testuser",
                "password": "TestPass123!",
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "test@example.com"
        assert data["username"] == "testuser"
        assert "id" in data

    async def test_login_success(self, client: AsyncClient, test_session: AsyncSession):
        """Успешный вход."""
        # Создание тестового пользователя
        await test_session.execute(
            insert(UserModel).values(
                email="login@example.com",
                username="loginuser",
                hashed_password=get_password_hash("correctpassword"),
                is_active=True,
            )
        )
        await test_session.commit()

        response = await client.post(
            "/auth/login",
            json={
                "username": "loginuser",
                "password": "correctpassword",
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
```

### Интеграционный тест

```python
class TestIntegrationSpecialties:
    """Интеграционные тесты /specialties."""

    def test_get_specialties(self, http_client: httpx.Client):
        """Получение списка специальностей."""
        response = http_client.get("/api/v1/specialties")

        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "page" in data
        assert "items" in data
```

---

## Типы тестов

### Unit-тесты (`test_api.py`, `test_auth.py`)

**Цель:** Тестирование отдельных модулей и эндпоинтов с моками зависимостей.

**Особенности:**
- Используют тестовую БД (SQLite in-memory или отдельная PostgreSQL)
- Мокают внешние сервисы (Redis, MinIO)
- Быстрое выполнение

**Примеры:**
- Проверка валидации запросов
- Тестирование бизнес-логики (Use Cases)
- Проверка ответов эндпоинтов

### Интеграционные тесты (`test_integration.py`)

**Цель:** Тестирование полностью запущенного API с реальными зависимостями.

**Особенности:**
- Запуск всех сервисов (PostgreSQL, Redis, MinIO)
- Реальные HTTP-запросы
- Медленнее, но более полные

**Запуск:**
```bash
# Запустить все сервисы
docker-compose up -d

# Запустить интеграционные тесты
pytest tests/test_integration.py
```

---

## Покрытие тестами

### Проверка покрытия

```bash
pytest --cov=app --cov-report=term-missing
```

**Пример вывода:**
```
Name                                    Stmts   Miss  Cover   Missing
---------------------------------------------------------------------
app/core/config.py                         45      5    89%   23-27
app/core/jwt.py                            67      8    88%   45-52
app/domain/models.py                      120      0   100%
app/infrastructure/repositories.py        234     45    81%   120-125, 145-150
app/presentation/routes.py                189     12    94%   56-60
---------------------------------------------------------------------
TOTAL                                    1234    156    87%
```

### Целевое покрытие

- **Минимум:** 80%
- **Цель:** 90%+
- **Критичные модуи:** 95%+ (аутентификация, платежи)

---

## Тестовые данные

### Создание тестовых данных

```python
async def test_get_specialty_from_db(self, client: AsyncClient, test_session: AsyncSession):
    """Получение специальности из БД."""
    # Создание тестовой специальности
    await test_session.execute(
        insert(SpecialtyModel).values(
            code="99.99.99",
            name="Тестовая специальность",
            short_description="Краткое описание",
            description=["Параграф 1", "Параграф 2"],
            exams=["Экзамен 1", "Экзамен 2"],
            images=[],
            is_popular=True,
        )
    )
    await test_session.commit()

    response = await client.get("/api/v1/specialties/99.99.99")

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == "99.99.99"
    assert data["name"] == "Тестовая специальность"
```

### Очистка после тестов

Фикстуры автоматически очищают данные после каждого теста:

```python
@pytest.fixture
async def test_session() -> AsyncSession:
    async with async_session_maker() as session:
        yield session
        # Rollback всех изменений после теста
        await session.rollback()
```

---

## CI/CD Интеграция

### GitHub Actions

```yaml
name: Tests

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_USER: anmicius
          POSTGRES_PASSWORD: test_password
          POSTGRES_DB: anmicius_test
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
      
      redis:
        image: redis:7
        ports:
          - 6379:6379

    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      - name: Run tests
        run: pytest --cov=app --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
```

---

## Troubleshooting

### Тесты падают с ошибкой БД

**Причина:** PostgreSQL не запущен или неверные учётные данные.

**Решение:**
```bash
# Проверить подключение
docker-compose ps postgres

# Протестировать подключение
psql -h localhost -U anmicius -d anmicius_test
```

### Тесты падают с ошибкой асинхронности

**Причина:** Неправильный режим asyncio в pytest.

**Решение:** Убедитесь, что `pytest.ini` содержит:
```ini
asyncio_mode = auto
```

### Интеграционные тесты возвращ 503

**Причина:** API не запущен или зависимости недоступны.

**Решение:**
```bash
docker-compose up -d
docker-compose logs api  # Проверить логи
```

---

## Best Practices

1. **Изоляция тестов** — каждый тест независим
2. **Фикстуры** для общих данных
3. **Один assertion на тест** (или логически связанные)
4. **Название теста** должно описывать сценарий
5. **Покрытие** всех веток кода (success, error, edge cases)
6. **Не тестировать** внешние библиотеки, только свою логику

---

## Связанные документы

- [Архитектура](./architecture.md) — слои приложения, которые тестируются
- [Обработка ошибок](./errors.md) — ожидаемые ошибки в тестах
- [Развёртывание](./deployment.md) — CI/CD интеграция
