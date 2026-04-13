"""Главный модуль приложения FastAPI."""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from slowapi.errors import RateLimitExceeded
from structlog import get_logger

from app.core.config import get_settings
from app.core.exceptions import AppException, NotFoundException, BadRequestException, ValidationException
from app.infrastructure.database import init_db, close_db, async_session_maker
from app.infrastructure.cache import init_cache, close_cache
from app.presentation.routes import create_v1_router
from app.presentation.admin_routes import (
    create_auth_router,
    create_admin_users_router,
    create_admin_specialties_router,
    create_admin_news_router,
    create_admin_facts_router,
    create_admin_upload_router,
    create_admin_gallery_router,
    create_admin_document_files_router,
    create_admin_faq_router,
    create_admin_documents_router,
    create_admin_about_router,
    create_admin_test_router,
    create_admin_cache_router,
    create_admin_admission_router,
    get_rate_limit_exception_handler,
)

logger = get_logger()
settings = get_settings()

# Security схемы
bearer_auth = HTTPBearer(auto_error=False)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения."""
    # Startup
    logger.info("Запуск приложения", name=settings.app_name, version=settings.app_version)
    await init_db()
    logger.info("База данных инициализирована")
    await init_cache()
    logger.info("Кэш инициализирован")

    yield

    # Shutdown
    await close_db()
    await close_cache()
    logger.info("Приложение остановлено")


def create_app() -> FastAPI:
    """Создание и настройка приложения FastAPI."""

    # Настройка OAuth2 для Swagger UI - ДО создания app
    from fastapi.security import OAuth2PasswordBearer
    oauth2_scheme = OAuth2PasswordBearer(
        tokenUrl="/auth/login/oauth",
        auto_error=False,
        scopes={
            "users:read": "Read information about users",
            "users:write": "Create and update users",
            "specialties:read": "Read specialties",
            "specialties:write": "Create and update specialties",
            "news:read": "Read news",
            "news:write": "Create and update news",
            "facts:read": "Read facts",
            "facts:write": "Create and update facts",
            "upload:write": "Upload files",
        },
    )

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="API для колледжа Anmicius",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.get_cors_origins,
        allow_credentials=False,  # Отключено для безопасности с конкретными origins
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type"],
    )
    
    # Регистрация роутеров
    app.include_router(create_v1_router())  # Публичные API v1
    app.include_router(create_auth_router())  # Аутентификация
    app.include_router(create_admin_users_router())  # Админ: пользователи
    app.include_router(create_admin_specialties_router())  # Админ: специальности
    app.include_router(create_admin_news_router())  # Админ: новости
    app.include_router(create_admin_facts_router())  # Админ: факты
    app.include_router(create_admin_upload_router())  # Админ: загрузка файлов
    app.include_router(create_admin_gallery_router())  # Админ: галерея
    app.include_router(create_admin_document_files_router())  # Админ: файлы документов
    app.include_router(create_admin_faq_router())  # Админ: FAQ
    app.include_router(create_admin_documents_router())  # Админ: документы
    app.include_router(create_admin_about_router())  # Админ: о колледже
    app.include_router(create_admin_test_router())  # Админ: тесты
    app.include_router(create_admin_cache_router())  # Админ: кэш
    app.include_router(create_admin_admission_router())  # Админ: приёмная кампания

    # Обработчик исключений rate limiting
    app.add_exception_handler(RateLimitExceeded, get_rate_limit_exception_handler())
    
    # Обработчики исключений
    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.message, "status_code": exc.status_code},
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        errors = []
        for error in exc.errors():
            errors.append(f"{error['loc']}: {error['msg']}")
        return JSONResponse(
            status_code=422,
            content={"detail": "; ".join(errors), "status_code": 422},
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        logger.error("Необработанное исключение", error=str(exc))
        return JSONResponse(
            status_code=500,
            content={"detail": "Внутренняя ошибка сервера", "status_code": 500},
        )
    
    # Health check
    @app.get("/health", tags=["Health"])
    async def health_check():
        """Проверка здоровья приложения и зависимостей."""
        from app.infrastructure.cache import cache_service
        from app.infrastructure.minio_service import get_minio_client
        from app.infrastructure.database import get_db_session
        from sqlalchemy import select, text
        
        health_status = {
            "status": "ok",
            "version": settings.app_version,
            "services": {}
        }
        all_ok = True
        
        # Проверка БД (критично)
        try:
            async with async_session_maker() as session:
                await session.execute(text("SELECT 1"))
            health_status["services"]["database"] = {"status": "ok"}
        except Exception as e:
            health_status["services"]["database"] = {"status": "error", "message": str(e)}
            health_status["status"] = "degraded"
            all_ok = False
        
        # Проверка Redis (некритично, кэш опционален)
        try:
            redis_available = await cache_service.is_available()
            if redis_available:
                health_status["services"]["redis"] = {"status": "ok"}
            else:
                health_status["services"]["redis"] = {"status": "unavailable", "message": "Redis not configured"}
        except Exception as e:
            health_status["services"]["redis"] = {"status": "error", "message": str(e)}
        
        # Проверка MinIO (некритично для health check)
        try:
            minio_client = get_minio_client()
            minio_client.bucket_exists(settings.minio_bucket)
            health_status["services"]["minio"] = {"status": "ok"}
        except Exception as e:
            health_status["services"]["minio"] = {"status": "unavailable", "message": "MinIO not configured"}
        
        return health_status
    
    @app.get("/", tags=["Root"])
    async def root():
        return {
            "name": settings.app_name,
            "version": settings.app_version,
            "docs": "/docs",
        }
    
    return app


app = create_app()
