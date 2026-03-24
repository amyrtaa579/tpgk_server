# Тесты для Anmicius API

## Структура тестов

```
tests/
├── __init__.py          # Пакет тестов
├── conftest.py          # Фикстуры и конфигурация pytest
├── test_api.py          # Unit-тесты API (с изолированной БД)
├── test_auth.py         # Unit-тесты аутентификации и админ-панели
└── test_integration.py  # Интеграционные тесты (с реальным API)
```

## Статус тестов

- **Unit-тесты:** 54 теста ✅
- **Интеграционные тесты:** 19 тестов (требуют запущенный API)
- **Покрытие:** 64%

## Типы тестов

### Unit-тесты (`test_api.py`)
- Тестируют отдельные компоненты API
- Используют изолированную in-memory SQLite БД
- Не требуют запущенного API или Docker
- Быстрые и стабильные

### Интеграционные тесты (`test_integration.py`)
- Тестируют API через HTTP
- Требуют запущенного API на `http://localhost:8000`
- Проверяют реальное взаимодействие с PostgreSQL и MinIO

## Запуск тестов

### Быстрый запуск (unit-тесты)
```bash
# Из корня проекта
pytest tests/test_api.py -v

# Или через скрипт
bash scripts/run_tests.sh unit
```

### Интеграционные тесты
```bash
# 1. Убедитесь, что API запущен
docker-compose up -d

# 2. Запустите интеграционные тесты
pytest tests/test_integration.py -v

# Или через скрипт
bash scripts/run_tests.sh integration
```

### Все тесты
```bash
pytest tests/ -v

# Или через скрипт
bash scripts/run_tests.sh all
```

### С отчётом о покрытии
```bash
pytest tests/ -v --cov=app --cov-report=html --cov-report=term-missing

# Или через скрипт
bash scripts/run_tests.sh coverage

# Отчёт откроется в браузере
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

## Покрытие тестами

### Endpoints (публичные):
- ✅ `GET /health` - Health check
- ✅ `GET /` - Root endpoint
- ✅ `GET /api/v1/about` - Информация о колледже
- ✅ `GET /api/v1/admission` - Приёмная кампания
- ✅ `GET /api/v1/specialties` - Список специальностей
- ✅ `GET /api/v1/specialties/{code}` - Детали специальности
- ✅ `GET /api/v1/specialties/{code}/facts` - Факты специальности
- ✅ `GET /api/v1/facts/{id}` - Детали факта
- ✅ `GET /api/v1/news` - Список новостей
- ✅ `GET /api/v1/news/{slug}` - Детали новости
- ✅ `GET /api/v1/faq` - FAQ
- ✅ `GET /api/v1/documents` - Документы
- ✅ `GET /api/v1/images` - Галерея
- ✅ `GET /api/v1/test/questions` - Вопросы теста
- ✅ `POST /api/v1/test/results` - Результаты теста

### Endpoints (аутентификация и админка):
- ✅ `POST /auth/register` - Регистрация
- ✅ `POST /auth/login` - Вход
- ✅ `POST /auth/refresh` - Обновление токена
- ✅ `POST /auth/logout` - Выход
- ✅ `GET /auth/me` - Текущий пользователь
- ✅ `GET /admin/users` - Список пользователей
- ✅ `GET /admin/users/{id}` - Пользователь по ID
- ✅ `PATCH /admin/users/{id}` - Обновление пользователя
- ✅ `DELETE /admin/users/{id}` - Удаление пользователя
- ✅ `GET /admin/specialties` - Список специальностей
- ✅ `POST /admin/specialties` - Создание специальности
- ✅ `GET /admin/specialties/{id}` - Специальность по ID
- ✅ `PUT /admin/specialties/{id}` - Обновление специальности
- ✅ `DELETE /admin/specialties/{id}` - Удаление специальности
- ✅ `GET /admin/news` - Список новостей
- ✅ `POST /admin/news` - Создание новости
- ✅ `GET /admin/news/{id}` - Новость по ID
- ✅ `PUT /admin/news/{id}` - Обновление новости
- ✅ `DELETE /admin/news/{id}` - Удаление новости
- ✅ `GET /admin/facts` - Список фактов
- ✅ `POST /admin/facts` - Создание факта
- ✅ `GET /admin/facts/{id}` - Факт по ID
- ✅ `PUT /admin/facts/{id}` - Обновление факта
- ✅ `DELETE /admin/facts/{id}` - Удаление факта
- ✅ `GET /admin/faq` - Список FAQ
- ✅ `POST /admin/faq` - Создание FAQ
- ✅ `GET /admin/faq/{id}` - FAQ по ID
- ✅ `PUT /admin/faq/{id}` - Обновление FAQ
- ✅ `DELETE /admin/faq/{id}` - Удаление FAQ
- ✅ `GET /admin/documents` - Список документов
- ✅ `POST /admin/documents` - Создание документа
- ✅ `DELETE /admin/documents/{id}` - Удаление документа
- ✅ `GET /admin/images` - Список изображений
- ✅ `POST /admin/images` - Создание элемента галереи
- ✅ `DELETE /admin/images/{id}` - Удаление изображения
- ✅ `GET /admin/test/questions` - Список вопросов теста
- ✅ `POST /admin/test/questions` - Создание вопроса
- ✅ `DELETE /admin/test/questions/{id}` - Удаление вопроса
- ✅ `GET /admin/about` - Информация о колледже
- ✅ `PUT /admin/about` - Обновление информации
- ✅ `POST /admin/upload/image` - Загрузка изображения
- ✅ `POST /admin/upload/document` - Загрузка документа

### Функциональность:
- ✅ Пагинация
- ✅ Поиск и фильтрация
- ✅ Обработка ошибок (400, 404, 422)
- ✅ Валидация данных
- ✅ Подсчёт просмотров новостей
- ✅ JWT аутентификация
- ✅ Проверка прав суперпользователя

## Конфигурация

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

### Фикстуры (conftest.py)
- `test_engine` - Движок SQLAlchemy для тестов
- `test_session` - Сессия БД с изолированными данными
- `client` - HTTP клиент для тестирования API
- `test_settings` - Тестовые настройки

## Добавление новых тестов

1. Создайте новый файл `test_<feature>.py` в папке `tests/`
2. Используйте готовые фикстуры из `conftest.py`
3. Следуйте naming convention: `test_<description>`

Пример:
```python
async def test_my_feature(client: AsyncClient, test_session: AsyncSession):
    """Описание теста."""
    response = await client.get("/api/v1/my-endpoint")
    
    assert response.status_code == 200
    data = response.json()
    assert "expected_field" in data
```

## Устранение проблем

### Ошибка "no such table"
Убедитесь, что фикстура `test_engine` создаёт таблицы перед тестами.

### Ошибка подключения к API
Для интеграционных тестов убедитесь, что API запущен:
```bash
docker-compose up -d api
```

### Проблемы с asyncio
Если возникают проблемы с event loop, добавьте в начало теста:
```python
@pytest.mark.asyncio
async def test_example():
    ...
```
