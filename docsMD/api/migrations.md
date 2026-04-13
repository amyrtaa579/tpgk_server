# Миграции базы данных (Alembic)

Проект использует **Alembic** для управления миграциями схемы PostgreSQL, обеспечивая версионирование и автоматическое применение изменений.

## Обзор

| Параметр | Значение |
|----------|----------|
| **Инструмент** | Alembic 1.13.1 |
| **База данных** | PostgreSQL 15 |
| **ORM** | SQLAlchemy 2.0 (async) |
| **Конфигурация** | `alembic.ini` |
| **Директория миграций** | `alembic/versions/` |
| **Скрипт окружения** | `alembic/env.py` |

---

## Структура файлов

```
alembic/
├── __init__.py
├── env.py              # Конфигурация Alembic, подключение к БД
├── script.py.mako      # Шаблон для новых миграций
└── versions/
    ├── __init__.py
    ├── 001_initial_migration.py     # Первая миграация
    ├── 002_add_news_table.py        # Добавление таблицы новостей
    ├── 003_add_faq_table.py         # Добавление таблицы FAQ
    └── ...                          # Последующие миграции
```

---

## Команды Alembic

### Основные команды

```bash
# Применить все миграции
alembic upgrade head

# Применить до конкретной миграции
alembic upgrade +1              # Следующая миграция
alembic upgrade <revision_id>   # До конкретной версии

# Откатить миграцию
alembic downgrade -1            # Откатить последнюю
alembic downgrade <revision_id> # До конкретной версии

# Проверить статус миграций
alembic current                 # Текущая версия
alembic history                 # История миграций
```

### Создание миграций

```bash
# Автосоздание (на основе изменений моделей)
alembic revision --autogenerate -m "Описание изменений"

# Ручное создание (пустая миграция)
alembic revision -m "Описание изменений"
```

---

## Процесс миграции

### Применение миграций (Production)

```bash
# 1. Подключиться к серверу
ssh user@api.anmicius.ru

# 2. Перейти в директорию проекта
cd /opt/anmicius-api

# 3. Применить миграции
docker-compose exec api alembic upgrade head
```

**Или изнутри контейнера:**
```bash
docker-compose exec api bash
alembic upgrade head
```

### Создание новой миграции

**Сценарий:** Добавление нового поля `phone` в таблицу `users`.

**Шаг 1: Изменение модели**

```python
# app/infrastructure/models.py
class UserModel(Base):
    # ... существующие поля
    phone = Column(String(50), nullable=True)  # Новое поле
```

**Шаг 2: Генерация миграции**

```bash
alembic revision --autogenerate -m "add phone column to users"
```

**Шаг 3: Проверка миграции**

```python
# alembic/versions/xxx_add_phone_column_to_users.py

def upgrade() -> None:
    op.add_column('users', sa.Column('phone', sa.String(50), nullable=True))

def downgrade() -> None:
    op.remove_column('users', 'phone')
```

**Шаг 4: Применение**

```bash
alembic upgrade head
```

---

## Примеры миграций

### Создание таблицы

```python
"""create specialties table

Revision ID: abc123
Revises: 
Create Date: 2024-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSON

revision = 'abc123'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'specialties',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(20), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('short_description', sa.Text(), nullable=True),
        sa.Column('description', JSON(), nullable=True),
        sa.Column('exams', JSON(), nullable=True),
        sa.Column('images', JSON(), nullable=True),
        sa.Column('is_popular', sa.Boolean(), server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), 
                  server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), 
                  server_default=sa.func.now()),
        sa.PrimaryKeyColumn('id'),
        sa.UniqueConstraint('code')
    )
    op.create_index('ix_specialties_code', 'specialties', ['code'])


def downgrade() -> None:
    op.drop_index('ix_specialties_code', 'specialties')
    op.drop_table('specialties')
```

### Добавление внешнего ключа

```python
def upgrade() -> None:
    op.add_column(
        'refresh_tokens',
        sa.Column('user_id', sa.Integer(), nullable=False)
    )
    op.create_foreign_key(
        'fk_refresh_tokens_user_id',
        'refresh_tokens', 'users',
        ['user_id'], ['id'],
        ondelete='CASCADE'
    )


def downgrade() -> None:
    op.drop_constraint('fk_refresh_tokens_user_id', 'refresh_tokens')
    op.drop_column('refresh_tokens', 'user_id')
```

### Изменение типа колонки

```python
def upgrade() -> None:
    op.alter_column(
        'users',
        'email',
        existing_type=sa.String(255),
        type_=sa.String(500),
        existing_nullable=False
    )


def downgrade() -> None:
    op.alter_column(
        'users',
        'email',
        existing_type=sa.String(500),
        type_=sa.String(255),
        existing_nullable=False
    )
```

---

## Конфигурация

### alembic.ini

Основные настройки:

```ini
[alembic]
script_location = alembic
prepend_sys_path = .
version_path_separator = os

# URL базы данных (переопределяется в env.py)
sqlalchemy.url = postgresql+asyncpg://anmicius:password@postgres:5432/anmicius_db
```

### env.py

Настройка подключения и миграций:

```python
from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
from app.infrastructure.models import Base  # Импорт всех моделей

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, 
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

---

## Таблицы базы данных

Полный список таблиц и их назначения:

| Таблица | Описание |
|---------|----------|
| `users` | Пользователи системы |
| `refresh_tokens` | JWT refresh токены (FK → users) |
| `specialties` | Специальности колледжа |
| `specialty_education_options` | Уровни образования (FK → specialties) |
| `interesting_facts` | Факты о специальностях (FK → specialties.code) |
| `news` | Новости |
| `faq` | Часто задаваемые вопросы |
| `documents` | Документы для скачивания |
| `gallery_images` | Фотогалерея |
| `document_files` | Файлы документов |
| `test_questions` | Вопросы профориентационного теста |
| `about_info` | Информация о колледже (singleton) |
| `admission_info` | Приёмная кампания (по годам) |

---

## Проверка статуса

### Текущая версия

```bash
alembic current
```

**Пример вывода:**
```
Current revision(s): abc123def456 (head)
```

### История миграций

```bash
alembic history
```

**Пример вывода:**
```
abc123def456 -> 789xyz012 (head), add admission_info table
456ghi789 -> abc123def456, add test_questions table
<base> -> 456ghi789, initial migration
```

### Статус миграций

```bash
alembic current --verbose
```

---

## Troubleshooting

### Таблица уже существует

**Ошибка:** `sqlalchemy.exc.ProgrammingError: (psycopg2.errors.DuplicateTable) relation "users" already exists`

**Причина:** Миграция пытается создать таблицу, которая уже существует.

**Решение:**
```bash
# Отметить миграцию как применённую без выполнения
alembic stamp head
```

### Конфликт миграций

**Ошибка:** `Multiple head revisions`

**Причина:** Две ветки миграций созданы параллельно.

**Решение:** Создать merge-миграцию:
```bash
alembic merge <rev1> <rev2> -m "merge branches"
```

### Нет изменений при autogenerate

**Причина:** Модели не импортированы в `env.py`.

**Решение:** Убедитесь, что все ORM-модели импортированы в `env.py`:
```python
from app.infrastructure.models import (
    UserModel,
    SpecialtyModel,
    NewsModel,
    # ... все модели
)
```

---

## Best Practices

1. **Всегда тестируйте миграции** на staging перед production
2. **Используйте `downgrade()`** для возможности отката
3. **Не редактируйте применённые миграции** — создавайте новые
4. **Используйте `--autogenerate`** только как отправную точку, проверяйте вручную
5. **Добавляйте индексы** для внешних ключей и часто используемых полей
6. **Резервное копирование** перед применением миграций в production

---

## Автоматизация (CI/CD)

### GitHub Actions пример

```yaml
name: Database Migrations

on:
  push:
    branches: [main]

jobs:
  migrate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Run migrations
        run: |
          docker-compose up -d postgres
          docker-compose exec api alembic upgrade head
```

---

## Связанные документы

- [Архитектура](./architecture.md) — ORM-модели и репозитории
- [Модели и схемы](./models-schemas.md) — SQLAlchemy модели
- [Развёртывание](./deployment.md) — применение миграций в production
