"""Главный модуль приложения FastAPI."""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from structlog import get_logger

from app.core.config import get_settings
from app.core.exceptions import AppException, NotFoundException, BadRequestException, ValidationException
from app.infrastructure.database import init_db, close_db
from app.presentation.routes import create_v1_router
from app.presentation.admin_routes import (
    create_auth_router,
    create_admin_users_router,
    create_admin_specialties_router,
    create_admin_news_router,
    create_admin_facts_router,
    create_admin_upload_router,
    create_admin_gallery_router,
    create_admin_faq_router,
    create_admin_documents_router,
    create_admin_about_router,
    create_admin_test_router,
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
    
    yield
    
    # Shutdown
    await close_db()
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
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
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
    app.include_router(create_admin_faq_router())  # Админ: FAQ
    app.include_router(create_admin_documents_router())  # Админ: документы
    app.include_router(create_admin_about_router())  # Админ: о колледже
    app.include_router(create_admin_test_router())  # Админ: тесты
    
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
        return {"status": "ok", "version": settings.app_version}
    
    @app.get("/", tags=["Root"])
    async def root():
        return {
            "name": settings.app_name,
            "version": settings.app_version,
            "docs": "/docs",
        }
    
    return app


app = create_app()
