"""Декораторы для кэширования."""

import functools
import inspect
from typing import Optional, Callable
from fastapi import Response
from app.infrastructure.cache import cache_service


def cache(
    key: str,
    group: str = "default",
    ttl: Optional[int] = None,
):
    """
    Декоратор для кэширования результатов функций.

    Args:
        key: Ключ кэша (может содержать {arg_name} для подстановки аргументов)
        group: Группа кэша для групповой очистки
        ttl: Время жизни кэша в секундах
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Получаем имя функции для ключа
            sig = inspect.signature(func)
            bound = sig.bind(*args, **kwargs)
            bound.apply_defaults()

            # Формируем ключ с подстановкой аргументов
            cache_key = key
            for name, value in bound.arguments.items():
                cache_key = cache_key.replace(f"{{{name}}}", str(value))

            # Пробуем получить из кэша
            cached = await cache_service.get(cache_key, group=group)
            if cached is not None:
                return cached

            # Вызываем функцию
            result = await func(*args, **kwargs) if inspect.iscoroutinefunction(func) else func(*args, **kwargs)

            # Сохраняем в кэш
            if result is not None:
                await cache_service.set(cache_key, result, group=group, ttl=ttl)

            return result

        return wrapper
    return decorator
