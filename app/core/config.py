from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Настройки приложения."""

    # Application
    app_name: str = "Anmicius API"
    app_version: str = "1.0.0"
    debug: bool = False
    environment: str = "development"

    # Database
    postgres_user: str = "anmicius"
    postgres_password: str = "anmicius_secret_password_change_in_production"
    postgres_db: str = "anmicius_db"
    postgres_host: str = "postgres"
    postgres_port: int = 5432
    database_url: str | None = None

    @property
    def get_database_url(self) -> str:
        if self.database_url:
            return self.database_url
        return f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"

    # MinIO
    minio_endpoint: str = "minio:9000"
    minio_access_key: str = "minioadmin_change_in_production"
    minio_secret_key: str = "minioadmin_change_in_production"
    minio_bucket: str = "anmicius-media"
    minio_secure: bool = False
    minio_public_url: str = "https://minio.anmicius.ru/anmicius-media"

    # CORS
    cors_origins: str = "https://anmicius.ru,https://api.anmicius.ru,https://minio.anmicius.ru,https://admin.anmicius.ru"

    @property
    def get_cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",")]

    # API
    api_v1_prefix: str = "/api/v1"

    # JWT - ОБЯЗАТЕЛЬНО измените в production!
    jwt_secret_key: str = "CHANGE_THIS_JWT_SECRET_KEY_IN_PRODUCTION"

    # Redis
    redis_host: str = "redis"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: str | None = None
    redis_ttl_default: int = 300  # 5 минут
    redis_ttl_long: int = 3600  # 1 час

    # API Pagination
    pagination_min_limit: int = 1
    pagination_max_limit: int = 50
    pagination_default_limit: int = 10

    # SSL/HTTPS (опционально)
    ssl_email: str | None = None
    main_domain: str | None = None

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache
def get_settings() -> Settings:
    """Получить кэшированный экземпляр настроек."""
    return Settings()
