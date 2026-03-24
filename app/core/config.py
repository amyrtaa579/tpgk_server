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
    postgres_password: str = "anmicius_secret_password"
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
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
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

    # JWT
    jwt_secret_key: str = "anmicius_super_secret_jwt_key_change_in_production"

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache
def get_settings() -> Settings:
    """Получить кэшированный экземпляр настроек."""
    return Settings()
