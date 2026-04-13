"""Use cases для аутентификации и управления пользователями."""

from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple

from app.domain.models import User
from app.domain.repositories import IUserRepository
from app.core.jwt import (
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_token,
    validate_password,
    validate_email,
)
from app.core.exceptions import (
    AppException,
    BadRequestException,
    NotFoundException,
    ValidationException,
)


class RegisterUserUseCase:
    """Регистрация нового пользователя."""

    def __init__(self, repository: IUserRepository):
        self.repository = repository

    async def execute(self, email: str, username: str, password: str) -> User:
        # Валидация email
        validate_email(email)
        
        # Проверка существующего email
        existing_user = await self.repository.get_by_email(email)
        if existing_user:
            raise BadRequestException("Пользователь с таким email уже существует")

        # Проверка существующего username
        existing_user = await self.repository.get_by_username(username)
        if existing_user:
            raise BadRequestException("Пользователь с таким username уже существует")

        # Валидация пароля
        validate_password(password)

        # Создание пользователя
        user = await self.repository.create(email, username, password)
        return user


class LoginUserUseCase:
    """Вход пользователя."""

    def __init__(self, repository: IUserRepository):
        self.repository = repository

    async def execute(self, username: str, password: str) -> Tuple[User, str, str]:
        # Поиск пользователя
        user = await self.repository.get_by_username(username)
        if not user:
            raise BadRequestException("Неверный username или пароль")

        # Проверка пароля
        if not verify_password(password, user.hashed_password):
            raise BadRequestException("Неверный username или пароль")

        # Проверка активности
        if not user.is_active:
            raise BadRequestException("Учетная запись заблокирована")

        # Определение scopes пользователя
        scopes = [
            "users:read", "users:write",
            "specialties:read", "specialties:write",
            "news:read", "news:write",
            "facts:read", "facts:write",
            "upload:write",
        ]
        if not user.is_superuser:
            # Обычные пользователи получают только read scopes
            scopes = [
                "users:read",
                "specialties:read",
                "news:read",
                "facts:read",
            ]

        # Создание токенов
        access_token = create_access_token(
            data={"sub": str(user.id), "username": user.username},
            scopes=scopes,
        )
        refresh_token = create_refresh_token(data={"sub": str(user.id), "username": user.username})

        # Сохранение refresh токена
        expires_at = (datetime.now(timezone.utc) + timedelta(days=30)).replace(tzinfo=None)
        await self.repository.save_refresh_token(user.id, refresh_token, expires_at)

        return user, access_token, refresh_token


class RefreshTokenUseCase:
    """Обновление access токена."""

    def __init__(self, repository: IUserRepository):
        self.repository = repository

    async def execute(self, refresh_token: str) -> Tuple[str, str]:
        # Проверка токена
        payload = verify_token(refresh_token, token_type="refresh")
        if not payload:
            raise ValidationException("Неверный refresh токен")

        user_id = int(payload.get("sub"))
        username = payload.get("username")

        # Поиск пользователя
        user = await self.repository.get_by_id(user_id)
        if not user:
            raise NotFoundException("Пользователь не найден")

        if not user.is_active:
            raise BadRequestException("Учетная запись заблокирована")

        # Проверка токена в БД
        db_token = await self.repository.get_refresh_token(refresh_token)
        if not db_token:
            raise ValidationException("Refresh токен не найден")

        if db_token.expires_at < datetime.now().replace(tzinfo=None):
            await self.repository.delete_refresh_token(refresh_token)
            raise ValidationException("Refresh токен истёк")

        # Определение scopes пользователя
        scopes = [
            "users:read", "users:write",
            "specialties:read", "specialties:write",
            "news:read", "news:write",
            "facts:read", "facts:write",
            "upload:write",
        ]
        if not user.is_superuser:
            scopes = [
                "users:read",
                "specialties:read",
                "news:read",
                "facts:read",
            ]

        # Создание новых токенов
        new_access_token = create_access_token(
            data={"sub": str(user.id), "username": user.username},
            scopes=scopes,
        )
        new_refresh_token = create_refresh_token(data={"sub": str(user.id), "username": user.username})

        # Обновление refresh токена в БД
        await self.repository.delete_refresh_token(refresh_token)
        expires_at = (datetime.now(timezone.utc) + timedelta(days=30)).replace(tzinfo=None)
        await self.repository.save_refresh_token(user.id, new_refresh_token, expires_at)

        return new_access_token, new_refresh_token


class LogoutUserUseCase:
    """Выход пользователя."""

    def __init__(self, repository: IUserRepository):
        self.repository = repository

    async def execute(self, refresh_token: str) -> bool:
        return await self.repository.delete_refresh_token(refresh_token)


class GetCurrentUserUseCase:
    """Получение текущего пользователя."""

    def __init__(self, repository: IUserRepository):
        self.repository = repository

    async def execute(self, user_id: int) -> User:
        user = await self.repository.get_by_id(user_id)
        if not user:
            raise NotFoundException("Пользователь не найден")
        return user


class GetAllUsersUseCase:
    """Получение всех пользователей."""

    def __init__(self, repository: IUserRepository):
        self.repository = repository

    async def execute(self, page: int = 1, limit: int = 10) -> dict:
        users, total = await self.repository.get_all(page=page, limit=limit)

        items = [
            {
                "id": u.id,
                "email": u.email,
                "username": u.username,
                "is_active": u.is_active,
                "is_superuser": u.is_superuser,
                "created_at": u.created_at.isoformat(),
            }
            for u in users
        ]

        return {
            "total": total,
            "page": page,
            "limit": limit,
            "items": items,
        }


class UpdateUserUseCase:
    """Обновление пользователя."""

    def __init__(self, repository: IUserRepository):
        self.repository = repository

    async def execute(self, user_id: int, updates: dict) -> User:
        user = await self.repository.get_by_id(user_id)
        if not user:
            raise NotFoundException("Пользователь не найден")

        # Применение обновлений
        from app.domain.models import User
        
        if "email" in updates and updates["email"]:
            # Проверка уникальности email
            existing = await self.repository.get_by_email(updates["email"])
            if existing and existing.id != user_id:
                raise BadRequestException("Пользователь с таким email уже существует")
            user.email = updates["email"]

        if "username" in updates and updates["username"]:
            # Проверка уникальности username
            existing = await self.repository.get_by_username(updates["username"])
            if existing and existing.id != user_id:
                raise BadRequestException("Пользователь с таким username уже существует")
            user.username = updates["username"]

        if "is_active" in updates:
            user.is_active = updates["is_active"]

        if "is_superuser" in updates:
            user.is_superuser = updates["is_superuser"]

        # Обновление пароля
        if "password" in updates and updates["password"]:
            validate_password(updates["password"])
            # Используем update_with_password для инвалидации токенов
            updated_user = await self.repository.update_with_password(user, updates["password"])
            return updated_user

        updated_user = await self.repository.update(user)
        return updated_user


class DeleteUserUseCase:
    """Удаление пользователя."""

    def __init__(self, repository: IUserRepository):
        self.repository = repository

    async def execute(self, user_id: int) -> bool:
        return await self.repository.delete(user_id)
