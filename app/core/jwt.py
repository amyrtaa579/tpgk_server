"""JWT утилиты для аутентификации."""

import re
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import get_settings
from app.core.exceptions import ValidationException

settings = get_settings()

# Настройки JWT
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 часа
REFRESH_TOKEN_EXPIRE_DAYS = 30

# Контекст для хеширования паролей с усиленными настройками
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверка пароля."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Хеширование пароля."""
    return pwd_context.hash(password)


def validate_password(password: str) -> None:
    """
    Валидация пароля.
    
    Требования:
    - Минимум 12 символов
    - Хотя бы одна заглавная буква
    - Хотя бы одна строчная буква
    - Хотя бы одна цифра
    - Хотя бы один специальный символ
    """
    if len(password) < 12:
        raise ValidationException("Пароль должен быть не менее 12 символов")
    
    if not re.search(r"[A-Z]", password):
        raise ValidationException("Пароль должен содержать хотя бы одну заглавную букву")
    
    if not re.search(r"[a-z]", password):
        raise ValidationException("Пароль должен содержать хотя бы одну строчную букву")
    
    if not re.search(r"\d", password):
        raise ValidationException("Пароль должен содержать хотя бы одну цифру")
    
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        raise ValidationException("Пароль должен содержать хотя бы один специальный символ (!@#$%^&*(),.?\":{}|<>)")


def validate_email(email: str) -> None:
    """
    Валидация email.
    
    Требования:
    - Стандартный формат email
    """
    email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if not re.match(email_pattern, email):
        raise ValidationException("Неверный формат email")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None, scopes: Optional[list[str]] = None) -> str:
    """Создание access токена."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire, "type": "access"})
    if scopes:
        to_encode.update({"scopes": scopes})
    else:
        # По умолчанию выдаем все scopes для суперпользователя
        to_encode.update({"scopes": [
            "users:read", "users:write",
            "specialties:read", "specialties:write",
            "news:read", "news:write",
            "facts:read", "facts:write",
            "upload:write",
        ]})
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret_key, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """Создание refresh токена."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret_key, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Optional[dict]:
    """Декодирование токена."""
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


def verify_token(token: str, token_type: str = "access") -> Optional[dict]:
    """Проверка токена."""
    payload = decode_token(token)
    if payload is None:
        return None
    
    if payload.get("type") != token_type:
        return None
    
    return payload
