"""Rate limiting конфигурация."""

from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request
from fastapi.responses import JSONResponse
from app.core.config import get_settings

settings = get_settings()

# Инициализация лимитера
limiter = Limiter(key_func=get_remote_address)


async def rate_limit_exception_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    """Обработчик превышения rate limit."""
    return JSONResponse(
        status_code=429,
        content={
            "detail": "Слишком много запросов",
            "message": f"Превышен лимит запросов. Попробуйте позже.",
        },
    )


def get_rate_limit_limits() -> dict:
    """Получить настройки rate limiting."""
    return {
        # Auth endpoints - строгие лимиты для защиты от brute-force
        "auth_per_minute": "10/minute",  # 10 запросов в минуту
        "auth_per_hour": "30/hour",     # 30 запросов в час
        # Общие лимиты
        "default_per_minute": "60/minute",
        "default_per_hour": "1000/hour",
    }
