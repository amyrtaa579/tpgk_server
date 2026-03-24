"""Сервис для работы с MinIO (загрузка файлов)."""

import io
from datetime import timedelta
from typing import Optional
from minio import Minio
from minio.error import S3Error

from app.core.config import get_settings

settings = get_settings()


def get_minio_client() -> Minio:
    """Получение клиента MinIO."""
    return Minio(
        settings.minio_endpoint,
        access_key=settings.minio_access_key,
        secret_key=settings.minio_secret_key,
        secure=settings.minio_secure,
    )


def ensure_bucket_exists(client: Minio, bucket_name: str) -> bool:
    """Проверка существования бакета."""
    try:
        if not client.bucket_exists(bucket_name):
            client.make_bucket(bucket_name)
        return True
    except S3Error:
        return False


def upload_file(
    client: Minio,
    bucket: str,
    file_data: bytes,
    object_name: str,
    content_type: str = "application/octet-stream",
) -> str:
    """
    Загрузка файла в MinIO.

    Возвращает URL файла.
    """
    ensure_bucket_exists(client, bucket)

    # Загружаем файл
    client.put_object(
        bucket,
        object_name,
        io.BytesIO(file_data),
        len(file_data),
        content_type=content_type,
    )

    # Формируем публичный URL
    # Используем minio_public_url из конфига для публичного доступа
    public_url = settings.minio_public_url.rstrip("/")
    url = f"{public_url}/{object_name}"

    return url


def upload_file_from_bytes(
    bucket: str,
    file_data: bytes,
    object_name: str,
    content_type: str = "application/octet-stream",
) -> str:
    """Загрузка файла из bytes."""
    client = get_minio_client()
    return upload_file(client, bucket, file_data, object_name, content_type)


def delete_file(client: Minio, bucket: str, object_name: str) -> bool:
    """Удаление файла из MinIO."""
    try:
        client.remove_object(bucket, object_name)
        return True
    except S3Error:
        return False


def get_presigned_url(
    client: Minio,
    bucket: str,
    object_name: str,
    expires: timedelta = timedelta(hours=1),
) -> str:
    """Получение временной ссылки на файл."""
    return client.presigned_get_object(
        bucket,
        object_name,
        expires=expires,
    )


def generate_unique_filename(original_filename: str) -> str:
    """Генерация уникального имени файла."""
    import uuid
    from pathlib import Path
    
    path = Path(original_filename)
    extension = path.suffix.lower() if path.suffix else ""
    unique_name = f"{uuid.uuid4().hex}{extension}"
    return unique_name


def get_file_extension(content_type: str) -> str:
    """Получение расширения файла по content type."""
    extension_map = {
        "image/jpeg": ".jpg",
        "image/png": ".png",
        "image/gif": ".gif",
        "image/webp": ".webp",
        "application/pdf": ".pdf",
        "application/msword": ".doc",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
        "application/vnd.ms-excel": ".xls",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": ".xlsx",
        "text/plain": ".txt",
    }
    return extension_map.get(content_type, "")
