"""Сервис кэширования на Redis."""

import json
from typing import Optional, Any
from redis.asyncio import Redis
from redis.exceptions import RedisError
from app.core.config import get_settings
from structlog import get_logger

logger = get_logger()
settings = get_settings()


class CacheService:
    """Сервис для работы с кэшем в Redis."""

    def __init__(self):
        self.redis: Optional[Redis] = None
        self._prefix = "anmicius_cache"
        self._version_key = f"{self._prefix}:version"

    async def connect(self) -> None:
        """Подключение к Redis."""
        try:
            self.redis = Redis(
                host=settings.redis_host,
                port=settings.redis_port,
                db=settings.redis_db,
                password=settings.redis_password,
                decode_responses=True,
            )
            await self.redis.ping()
            print(f"✓ Подключено к Redis: {settings.redis_host}:{settings.redis_port}")
        except RedisError as e:
            print(f"⚠ Не удалось подключиться к Redis: {e}")
            self.redis = None

    async def disconnect(self) -> None:
        """Отключение от Redis."""
        if self.redis:
            await self.redis.close()
            self.redis = None

    async def is_available(self) -> bool:
        """Проверка доступности Redis."""
        if not self.redis:
            return False
        try:
            await self.redis.ping()
            return True
        except RedisError:
            return False

    def _make_key(self, key: str) -> str:
        """Создание полного ключа с префиксом."""
        return f"{self._prefix}:{key}"

    async def _get_version(self, group: str) -> int:
        """Получение версии для группы кэша."""
        version_key = self._make_key(f"{self._version_key}:{group}")
        version = await self.redis.get(version_key) if self.redis else None
        return int(version) if version else 1

    async def _increment_version(self, group: str) -> int:
        """Увеличение версии для группы кэша."""
        version_key = self._make_key(f"{self._version_key}:{group}")
        if self.redis:
            return await self.redis.incr(version_key)
        return 1

    async def get(self, key: str, group: str = "default") -> Optional[Any]:
        """Получение данных из кэша."""
        if not await self.is_available():
            return None

        try:
            version = await self._get_version(group)
            full_key = self._make_key(f"{group}:v{version}:{key}")
            data = await self.redis.get(full_key)

            if data is None:
                return None

            return json.loads(data)
        except json.JSONDecodeError as e:
            logger.warning("Некорректные данные в кэше", key=key, group=group, error=str(e))
            return None
        except RedisError as e:
            logger.error("Ошибка Redis при получении данных", key=key, group=group, error=str(e))
            return None

    async def set(
        self,
        key: str,
        value: Any,
        group: str = "default",
        ttl: Optional[int] = None,
    ) -> bool:
        """Сохранение данных в кэш."""
        if not await self.is_available():
            return False

        try:
            version = await self._get_version(group)
            full_key = self._make_key(f"{group}:v{version}:{key}")
            ttl = ttl or settings.redis_ttl_default

            await self.redis.set(full_key, json.dumps(value), ex=ttl)
            return True
        except TypeError as e:
            logger.warning("Некорректный тип данных для кэширования", key=key, group=group, error=str(e))
            return False
        except RedisError as e:
            logger.error("Ошибка Redis при сохранении данных", key=key, group=group, error=str(e))
            return False

    async def delete(self, key: str, group: str = "default") -> bool:
        """Удаление ключа из кэша."""
        if not await self.is_available():
            return False

        try:
            version = await self._get_version(group)
            full_key = self._make_key(f"{group}:v{version}:{key}")
            await self.redis.delete(full_key)
            return True
        except RedisError as e:
            logger.error("Ошибка Redis при удалении данных", key=key, group=group, error=str(e))
            return False

    async def clear_group(self, group: str) -> bool:
        """Очистка всей группы кэша (увеличением версии)."""
        if not await self.is_available():
            return False

        try:
            await self._increment_version(group)
            return True
        except RedisError as e:
            logger.error("Ошибка Redis при очистке группы", group=group, error=str(e))
            return False

    async def clear_pattern(self, pattern: str) -> bool:
        """Очистка ключей по паттерну."""
        if not await self.is_available():
            return False

        try:
            full_pattern = self._make_key(pattern)
            cursor = 0
            while True:
                cursor, keys = await self.redis.scan(cursor, match=full_pattern, count=100)
                if keys:
                    await self.redis.delete(*keys)
                if cursor == 0:
                    break
            return True
        except RedisError as e:
            logger.error("Ошибка Redis при очистке по паттерну", pattern=pattern, error=str(e))
            return False

    async def clear_all(self) -> bool:
        """Очистка всего кэша приложения."""
        if not await self.is_available():
            return False

        try:
            await self.clear_pattern("*")
            return True
        except RedisError as e:
            logger.error("Ошибка Redis при полной очистке кэша", error=str(e))
            return False

    async def get_stats(self) -> dict:
        """Получение статистики кэша."""
        if not await self.is_available():
            return {"available": False}

        try:
            info = await self.redis.info("memory")
            keys_count = await self.redis.dbsize()

            return {
                "available": True,
                "keys_count": keys_count,
                "used_memory": info.get("used_memory_human", "N/A"),
                "used_memory_peak": info.get("used_memory_peak_human", "N/A"),
            }
        except RedisError as e:
            logger.error("Ошибка Redis при получении статистики", error=str(e))
            return {"available": False, "error": "Failed to get stats"}


# Глобальный экземпляр сервиса
cache_service = CacheService()


async def init_cache() -> None:
    """Инициализация кэша при старте приложения."""
    await cache_service.connect()


async def close_cache() -> None:
    """Закрытие соединения с кэшем."""
    await cache_service.disconnect()


async def get_cache() -> CacheService:
    """Получение сервиса кэша (для зависимостей)."""
    return cache_service
