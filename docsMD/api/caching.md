# Кэширование в Redis

API использует **Redis** для кэширования публичных эндпоинтов, что значительно снижает нагрузку на базу данных и ускоряет время ответа.

## Обзор

| Параметр | Значение |
|----------|----------|
| **Хранилище** | Redis 7 |
| **Тип** | In-memory key-value store |
| **Кодировка** | UTF-8 |
| **Формат данных** | JSON (сериализованный) |
| **Подключение** | Async (redis.asyncio) |

## Архитектура кэширования

### Версионирование групп

Кэш использует систему **версионирования групп** для быстрой инвалидации:

```
anmicius_cache:{group}:v{version}:{key}
```

Пример:
```
anmicius_cache:public:v15:specialties:p1:l10
```

### Принцип работы

```
┌──────────────────┐
│  HTTP Request     │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  Check Cache     │ ← Ключ: "specialties:p1:l10"
└────────┬─────────┘
         │
    ┌────┴────┐
    │  Hit?   │
    └────┬────┘
         │
    ┌────┴─────┐
    │          │
   YES        NO
    │          │
    │          ▼
    │   ┌──────────────────┐
    │   │  Execute Query   │ ← Запрос к БД
    │   └────────┬─────────┘
    │            │
    │            ▼
    │   ┌──────────────────┐
    │   │  Store to Cache  │ ← TTL: 300s (5 мин)
    │   └────────┬─────────┘
    │            │
    ▼            ▼
┌──────────────────┐
│  Return Response  │
└──────────────────┘
```

---

## Время жизни кэша (TTL)

Разные эндпоинты имеют разное TTL в зависимости от частоты обновления данных:

| Эндпоинт | TTL | Группа |
|----------|-----|--------|
| `/api/v1/specialties` (список) | 5 минут | `public` |
| `/api/v1/specialties/{code}` (детали) | 10 минут | `public` |
| `/api/v1/specialties/{code}/facts` | 10 минут | `public` |
| `/api/v1/facts/{fact_id}` | 10 минут | `public` |
| `/api/v1/news` (список) | 5 минут | `public` |
| `/api/v1/news/{slug}` (детали) | 1 час | `public` |
| `/api/v1/faq` | 1 час | `public` |
| `/api/v1/documents` | 1 час | `public` |
| `/api/v1/about` | 1 час | `public` |
| `/api/v1/images` | Не кэшируется | — |
| `/api/v1/test/questions` | Не кэшируется | — |
| `/api/v1/admission` | Не кэшируется | — |

### Формирование ключей

Ключи формируются на основе параметров запроса:

```python
# Специальности с пагинацией
cache_key = f"specialties:p{page}:l{limit}"
if search:
    cache_key += f":s{search}"
if form:
    cache_key += f":f{form}"
if popular:
    cache_key += ":pop"

# Пример: "specialties:p1:l10:sпрограм:f"
```

---

## Инвалидация кэша

### Автоматическая инвалидация

При **любом изменении данных** через админ-панель (POST/PUT/DELETE) кэш группы `public` **автоматически очищается**:

```python
# В каждом admin-роутере
await cache_service.clear_group("public")
```

**Пример:**
```
Админ обновляет специальность → clear_group("public") → 
  версия группы увеличивается с 15 на 16 →
    старые ключи "public:v15:..." становятся невалидными →
      новые запросы используют "public:v16:..."
```

### Ручная инвалидация

Администраторы могут вручную очистить кэш через эндпоинты управления кэшем.

---

## Эндпоинты управления кэшем

Все эндпоинты требуют **роль суперпользователя**.

### GET /admin/cache/stats

Получение статистики кэширования.

**Пример запроса:**

```bash
curl -X GET https://api.anmicius.ru/admin/cache/stats \
  -H "Authorization: Bearer eyJhbGci..."
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

**Поля ответа:**

| Поле | Тип | Описание |
|------|-----|----------|
| `available` | bool | Доступен ли Redis |
| `keys_count` | int | Количество ключей в БД |
| `used_memory` | string | Используемая память (человеко-читаемая) |
| `used_memory_peak` | string | Пиковая память |

---

### POST /admin/cache/clear

Очистка всего кэша приложения.

**Пример запроса:**

```bash
curl -X POST https://api.anmicius.ru/admin/cache/clear \
  -H "Authorization: Bearer eyJhbGci..."
```

**Ответ (200 OK):**

```json
{
  "message": "Кэш успешно очищен"
}
```

---

### POST /admin/cache/clear/{group}

Очистка кэша определённой группы (инкрементирует версию).

**Параметры пути:**

| Параметр | Тип | Описание |
|----------|-----|----------|
| `group` | string | Название группы (например, `public`) |

**Пример запроса:**

```bash
curl -X POST https://api.anmicius.ru/admin/cache/clear/public \
  -H "Authorization: Bearer eyJhbGci..."
```

**Ответ (200 OK):**

```json
{
  "message": "Кэш группы 'public' очищен"
}
```

---

## Реализация

### Сервис кэширования

Сервис расположен в `app/infrastructure/cache.py`.

**Класс `CacheService`:**

```python
class CacheService:
    async def connect(self) -> None:
        """Подключение к Redis."""
    
    async def get(self, key: str, group: str = "default") -> Optional[Any]:
        """Получение данных из кэша."""
    
    async def set(self, key: str, value: Any, group: str = "default", 
                  ttl: Optional[int] = None) -> bool:
        """Сохранение данных в кэш."""
    
    async def clear_group(self, group: str) -> bool:
        """Очистка группы кэша (увеличением версии)."""
    
    async def clear_all(self) -> bool:
        """Очистка всего кэша."""
```

### Метод `_increment_version`

```python
async def _increment_version(self, group: str) -> int:
    """Увеличение версии для группы кэша."""
    version_key = self._make_key(f"{self._version_key}:{group}")
    if self.redis:
        return await self.redis.incr(version_key)
    return 1
```

Это обеспечивает **быструю инвалидацию** без удаления ключей — старые ключи просто перестают использоваться.

---

## Примеры использования

### В публичном эндпоинте

```python
@router.get("/specialties", response_model=SpecialtiesResponse)
async def get_specialties(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=50),
    search: Optional[str] = Query(None),
    session: AsyncSession = Depends(get_db_session),
):
    # Формируем ключ кэша
    cache_key = f"specialties:p{page}:l{limit}"
    if search:
        cache_key += f":s{search}"
    
    # Пробуем получить из кэша
    cached = await cache_service.get(cache_key, group="public")
    if cached is not None:
        return cached
    
    # Выполняем запрос к БД
    repository = SpecialtyRepository(session)
    use_case = GetSpecialtiesUseCase(repository)
    result = await use_case.execute(page=page, limit=limit, search=search)
    
    # Сохраняем в кэш
    await cache_service.set(cache_key, result, group="public", ttl=300)
    return result
```

### В админ-эндпоинте (с инвалидацией)

```python
@router.post("/specialties")
async def create_specialty(
    code: str = Form(...),
    name: str = Form(...),
    session: AsyncSession = Depends(get_db_session),
):
    repository = SpecialtyRepository(session)
    specialty = await repository.create(code=code, name=name, ...)
    
    # Очищаем кэш публичных эндпоинтов
    await cache_service.clear_group("public")
    
    return {"id": specialty.id, "code": specialty.code}
```

---

## Переменные окружения

| Переменная | Описание | По умолчанию |
|------------|----------|-------------|
| `REDIS_HOST` | Хост Redis | `redis` |
| `REDIS_PORT` | Порт Redis | `6379` |
| `REDIS_DB` | Номер БД | `0` |
| `REDIS_PASSWORD` | Пароль (опционально) | `None` |
| `REDIS_TTL_DEFAULT` | TTL по умолчанию (сек) | `300` (5 минут) |
| `REDIS_TTL_LONG` | Длительный TTL (сек) | `3600` (1 час) |

---

## Отказоустойчивость

### Redis недоступен

Если Redis недоступен, API **продолжает работать** — запросы выполняются напрямую к базе данных:

```python
async def get(self, key: str, group: str = "default") -> Optional[Any]:
    if not await self.is_available():
        return None  # Кэш пропущен, запрос к БД
```

**Health Check** покажет статус Redis:

```json
{
  "status": "degraded",
  "services": {
    "database": {"status": "ok"},
    "redis": {"status": "error", "message": "Connection refused"},
    "minio": {"status": "ok"}
  }
}
```

---

## Производительность

### Преимущества кэширования

| Метрика | Без кэша | С кэшем |
|---------|----------|---------|
| Время ответа | 50-200ms | 5-15ms |
| Нагрузка на БД | Высокая | Низкая |
| Черезput | Ограничен БД | Высокий |

### Рекомендации

1. **Мониторинг** использования памяти Redis
2. **Настройка максимального объема** (maxmemory)
3. **Политика eviction** (allkeys-lru)
4. **Периодический анализ** hot keys

---

## Troubleshooting

### Кэш не очищается

**Причина:** Redis недоступен или ошибка соединения.

**Решение:**
```bash
docker-compose ps redis
docker-compose logs redis
```

### Старые данные после обновления

**Причина:** Кэш ещё не инвалидирован.

**Решение:** Вручную очистить кэш:
```bash
curl -X POST https://api.anmicius.ru/admin/cache/clear/public \
  -H "Authorization: Bearer TOKEN"
```

---

## Связанные документы

- [Публичные эндпоинты](./public-endpoints.md) — кэшируемые эндпоинты
- [Админ-эндпоинты](./admin-endpoints.md) — управление кэшем
- [Health Check](./public-endpoints.md#health-check) — проверка состояния Redis
- [Архитектура](./architecture.md) — обзор системы
