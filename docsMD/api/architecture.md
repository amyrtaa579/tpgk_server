# Архитектура Anmicius API — Clean Architecture

Проект следует принципам **Clean Architecture** (Роберт Мартин), обеспечивая разделение ответственности, тестируемость и независимость от фреймворков.

## Диаграмма слоёв

```
┌─────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                        │
│  FastAPI Routers  │  Pydantic Schemas  │  Exception Handlers │
├─────────────────────────────────────────────────────────────┤
│                    APPLICATION LAYER                         │
│         Use Cases  │  Auth Dependencies  │  DTO Mapping      │
├─────────────────────────────────────────────────────────────┤
│                     DOMAIN LAYER                             │
│    Business Models (dataclass)  │  Repository Interfaces     │
├─────────────────────────────────────────────────────────────┤
│                  INFRASTRUCTURE LAYER                        │
│  Repository Impl  │  ORM Models  │  Database  │  MinIO  │ Cache │
└─────────────────────────────────────────────────────────────┘
                         ▲
                    CORE LAYER
     Config  │  JWT Utils  │  Exceptions  │  Rate Limiter
```

## Поток зависимостей

```
Presentation → Application → Domain ← Infrastructure
                                     ← Core
```

**Правило зависимостей:** Каждый слой зависит только от внутренних слоёв. Domain не знает ни о чём внешнем.

## Структура проекта

```
app/
├── core/                    # Ядро: утилиты, конфигурация
│   ├── config.py            #   Pydantic Settings (.env)
│   ├── jwt.py               #   JWT создание/проверка, хэширование паролей
│   ├── exceptions.py        #   Кастомные исключения
│   └── rate_limiter.py      #   Конфигурация SlowAPI
│
├── domain/                  # Бизнес-правила (не зависят от фреймворков)
│   ├── models.py            #   Dataclass бизнес-моделей
│   └── repositories.py      #   ABC-интерфейсы репозиториев
│
├── application/             # Бизнес-логика (Use Cases)
│   ├── use_cases.py         #   Публичные Use Cases
│   ├── auth_use_cases.py    #   Auth Use Cases
│   └── dependencies.py      #   FastAPI зависимости (DI)
│
├── infrastructure/          # Реализации (фреймворк-зависимые)
│   ├── models.py            #   SQLAlchemy ORM модели
│   ├── repositories.py      #   Реализации репозиториев
│   ├── database.py          #   Async DB engine & session
│   ├── minio_service.py     #   S3-хранилище
│   ├── cache.py             #   Redis кэширование
│   └── cache_decorator.py   #   Декоратор кэширования
│
└── presentation/            # HTTP слой (фреймворк-зависимый)
    ├── routes.py            #   Публичные эндпоинты
    ├── admin_routes.py      #   Админ эндпоинты (14 роутеров)
    └── schemas.py           #   Pydantic v2 схемы
```

## Подробное описание слоёв

### Core Layer (`app/core/`)

Независимые утилиты и конфигурация, используемые всеми слоями.

#### `config.py`

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "Anmicius API"
    debug: bool = False
    postgres_host: str = "postgres"
    # ... все настройки из .env
    
    class Config:
        env_file = ".env"
```

Все настройки загружаются из `.env` через `pydantic-settings`.

#### `jwt.py`

- **Создание токенов:** `create_access_token()`, `create_refresh_token()`
- **Проверка токенов:** `decode_token()`, `verify_token()`
- **Пароли:** `get_password_hash()`, `verify_password()` (bcrypt, 12 rounds)
- **Валидация:** `validate_password()`, `validate_email()`

Параметры JWT:
| Параметр | Значение |
|----------|----------|
| Алгоритм | HS256 |
| Access TTL | 24 часа |
| Refresh TTL | 30 дней |
| Мин. длина пароля | 12 символов |

#### `exceptions.py`

```python
class AppException(Exception):         # 500
class NotFoundException(AppException):  # 404
class BadRequestException(AppException): # 400
class ValidationException(AppException): # 422
```

#### `rate_limiter.py`

Конфигурация SlowAPI:
- Auth: 10/мин, 30/час
- Default: 60/мин, 1000/час

---

### Domain Layer (`app/domain/`)

**Самый важный слой.** Содержит бизнес-правила, не зависит от фреймворков.

#### `models.py` — Бизнес-модели (dataclass)

```python
@dataclass
class Specialty:
    id: Optional[int] = None
    code: str = ""
    name: str = ""
    short_description: str = ""
    description: list[str] = None
    exams: list[str] = None
    images: list[Image] = None
    documents: list[Image] = None
    education_options: list[SpecialtyEducationOption] = None
```

Все модели — это чистые dataclass без привязки к БД или фреймворкам.

Ключевые модели:
- `Specialty` — специальность колледжа
- `InterestingFact` — интересный факт о специальности
- `News` — новостная статья
- `FAQ` — часто задаваемый вопрос
- `Document` — документ для скачивания
- `GalleryImage` — изображение галереи
- `TestQuestion` — вопрос профориентационного теста
- `TestResult` — результат теста
- `AboutInfo` — информация о колледже
- `AdmissionInfo` — приёмная кампания
- `User` — пользователь системы

#### `repositories.py` — Интерфейсы репозиториев (ABC)

```python
from abc import ABC, abstractmethod

class ISpecialtyRepository(ABC):
    @abstractmethod
    async def get_all(self, page: int, limit: int, search: str = None, ...) -> tuple[list[Specialty], int]: ...
    
    @abstractmethod
    async def get_by_code(self, code: str) -> Specialty | None: ...
    
    @abstractmethod
    async def create(self, specialty: Specialty) -> Specialty: ...
```

Каждый интерфейс определяет контракт для работы с соответствующей сущностью.

**Преимущество:** Application слой работает только с интерфейсами, не зная о SQLAlchemy, PostgreSQL и т.д.

---

### Application Layer (`app/application/`)

Оркестрирует бизнес-логику через Use Cases.

#### `use_cases.py` — Публичные Use Cases

Каждый Use Case — это класс, инкапсулирующий одну бизнес-операцию:

```python
class GetSpecialtiesUseCase:
    def __init__(self, repo: ISpecialtyRepository):
        self.repo = repo
    
    async def execute(self, page: int, limit: int, search: str = None, ...) -> dict:
        items, total = await self.repo.get_all(page, limit, search, ...)
        return {
            "items": items,
            "total": total,
            "page": page,
            "limit": limit,
            "pages": (total + limit - 1) // limit
        }
```

Публичные Use Cases:
| Use Case | Описание |
|----------|----------|
| `GetAboutInfoUseCase` | Получить информацию о колледже |
| `GetAdmissionInfoUseCase` | Получить приёмную кампанию |
| `GetSpecialtiesUseCase` | Список специальностей с фильтрами |
| `GetSpecialtyByCodeUseCase` | Детали специальности + факты |
| `GetNewsUseCase` | Список новостей |
| `GetNewsBySlugUseCase` | Детали новости + инкремент просмотров |
| `GetFAQUseCase` | FAQ с фильтром по категории |
| `GetDocumentsUseCase` | Документы с фильтром |
| `GetGalleryUseCase` | Фотогалерея |
| `GetTestQuestionsUseCase` | Все вопросы теста |
| `SubmitTestAnswersUseCase` | Обработка ответов, расчёт рекомендации |

#### `auth_use_cases.py` — Auth Use Cases

| Use Case | Описание |
|----------|----------|
| `RegisterUserUseCase` | Регистрация с валидацией |
| `LoginUserUseCase` | Аутентификация + выдача токенов |
| `RefreshTokenUseCase` | Обновление пары токенов |
| `LogoutUserUseCase` | Удаление refresh токена |
| `GetCurrentUserUseCase` | Получить текущего пользователя |
| `GetAllUsersUseCase` | Список пользователей (superuser) |
| `UpdateUserUseCase` | Обновить пользователя |
| `DeleteUserUseCase` | Удалить пользователя |

#### `dependencies.py` — FastAPI DI

```python
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_db_session)
) -> User:
    """Извлечь текущего пользователя из JWT токена."""
    # ... декодирование, проверка, загрузка из БД
```

---

### Infrastructure Layer (`app/infrastructure/`)

Реализации репозиториев и интеграция с внешними системами.

#### `models.py` — SQLAlchemy ORM

```python
class SpecialtyModel(Base):
    __tablename__ = "specialties"
    
    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    code = mapped_column(String(20), unique=True, nullable=False)
    name = mapped_column(String(255), nullable=False)
    description = mapped_column(JSON, default=list)
    # ...
```

Таблицы БД:
| Таблица | Описание |
|---------|----------|
| `specialties` | Специальности |
| `specialty_education_options` | Уровни образования (FK → specialties) |
| `interesting_facts` | Факты (FK → specialties.code) |
| `news` | Новости |
| `faq` | FAQ |
| `documents` | Документы |
| `gallery_images` | Галерея |
| `document_files` | Файлы документов |
| `test_questions` | Вопросы теста |
| `about_info` | О колледже |
| `admission_info` | Приёмная кампания |
| `users` | Пользователи |
| `refresh_tokens` | Refresh токены (FK → users) |

#### `repositories.py` — Реализации

```python
class SpecialtyRepository(ISpecialtyRepository):
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_code(self, code: str) -> Specialty | None:
        stmt = select(SpecialtyModel).where(SpecialtyModel.code == code)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None
```

Каждый репозиторий:
1. Принимает `AsyncSession` в конструкторе
2. Реализует интерфейс из Domain
3. Конвертирует ORM → Domain model

#### `database.py` — Подключение к БД

```python
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

engine = create_async_engine(settings.database_url, echo=settings.debug)
session_factory = async_sessionmaker(engine, expire_on_commit=False)

async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with session_factory() as session:
        yield session
```

#### `minio_service.py` — S3-хранилище

```python
async def upload_file_from_bytes(
    client: Minio,
    file_bytes: bytes,
    folder: str,
    extension: str
) -> str:
    """Загрузить файл в MinIO, вернуть публичный URL."""
```

Структура bucket `anmicius-media`:
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

#### `cache.py` — Redis кэширование

```python
class CacheService:
    async def get(self, key: str) -> Any | None: ...
    async def set(self, key: str, value: Any, ttl: int = 300) -> None: ...
    async def clear_group(self, group: str) -> None: ...
```

Версионирование: `anmicius_cache:{group}:v{version}:{key}`

---

### Presentation Layer (`app/presentation/`)

HTTP-интерфейс: роутеры, схемы, обработчики.

#### `schemas.py` — Pydantic v2 схемы

```python
class SpecialtyListItemSchema(BaseModel):
    id: int
    code: str
    name: str
    short_description: str
    
    model_config = ConfigDict(from_attributes=True)
```

Все схемы разделены:
- **Response** — для ответов API
- **Create/Update** — для запросов
- **ListItem** — для списков (урезанные поля)

#### `routes.py` — Публичные эндпоинты

```python
router = APIRouter(prefix="/api/v1")

@router.get("/specialties", response_model=SpecialtiesResponse)
async def get_specialties(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=50),
    use_case: GetSpecialtiesUseCase = Depends(),
    cache: CacheService = Depends(),
) -> SpecialtiesResponse:
    # ... кэш → use_case → ответ
```

#### `admin_routes.py` — Админ эндпоинты

14 отдельных роутеров, каждый — функция-фабрика:

```python
def create_admin_specialties_router(
    use_case_factory, cache_service, minio_service
) -> APIRouter:
    router = APIRouter(prefix="/admin/specialties", tags=["Admin - Specialties"])
    
    @router.get("/")
    async def list_specialties(...): ...
    
    @router.post("/")
    async def create_specialty(...): ...
    
    return router
```

---

## Паттерны проектирования

### Dependency Injection (DI)

FastAPI встроенный DI через `Depends()`:

```python
@router.get("/specialties")
async def get_specialties(
    session: AsyncSession = Depends(get_db_session),
    cache: CacheService = Depends(get_cache_service),
    use_case: GetSpecialtiesUseCase = Depends(get_specialties_use_case),
):
```

### Repository Pattern

Изолирует работу с БД:

```python
# Domain: интерфейс
class IRepository(ABC):
    @abstractmethod
    async def get_by_id(self, id: int) -> Entity | None: ...

# Infrastructure: реализация
class SpecialtyRepository(IRepository):
    async def get_by_id(self, id: int) -> Specialty | None: ...
```

### Use Case Pattern

Каждая бизнес-операция — отдельный класс:

```python
class SubmitTestAnswersUseCase:
    """Один Use Case = одна операция."""
    async def execute(self, answers: list[TestAnswer]) -> TestResult:
        # валидация → расчёт → результат
```

### Data Mapper

Конвертация ORM → Domain:

```python
def _to_domain(self, model: SpecialtyModel) -> Specialty:
    return Specialty(
        id=model.id,
        code=model.code,
        name=model.name,
        description=model.description or [],
        # ...
    )
```

---

## Преимущества такой архитектуры

| Преимущество | Описание |
|-------------|----------|
| **Тестируемость** | Domain и Application слои тестируются без БД |
| **Заменяемость** | Можно заменить PostgreSQL на MongoDB, изменив только Infrastructure |
| **Понятность** | Каждый слой имеет чёткую ответственность |
| **Независимость** | Бизнес-логика не зависит от FastAPI, SQLAlchemy и т.д. |
| **Масштабируемость** | Легко добавлять новые Use Cases без изменения существующих |

---

## Диаграмма потока запроса

```
HTTP Request
     │
     ▼
┌─────────────┐
│  Router      │  ← Presentation: валидация входных данных (Pydantic)
│  (FastAPI)   │
└──────┬───────┘
       │
       ▼
┌─────────────┐
│  Use Case    │  ← Application: бизнес-логика, оркестрация
│  (Service)   │
└──────┬───────┘
       │
       ▼
┌─────────────┐
│ Repository   │  ← Infrastructure: запрос к БД/кэшу/MinIO
│ (SQLAlchemy) │
└──────┬───────┘
       │
       ▼
┌─────────────┐
│  Database    │  ← PostgreSQL / Redis / MinIO
│  / Cache     │
└─────────────┘
       │
       ▼ (обратный поток)
Domain Model → Pydantic Schema → JSON Response
```
