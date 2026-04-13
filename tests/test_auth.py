"""Тесты для аутентификации и админ-панели."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert, select

from app.infrastructure.models import UserModel, RefreshTokenModel
from app.core.jwt import get_password_hash


# =============================================================================
# Auth Tests
# =============================================================================

class TestAuth:
    """Тесты для аутентификации."""

    async def test_register_user(self, client: AsyncClient, test_session: AsyncSession):
        """Регистрация нового пользователя."""
        response = await client.post(
            "/auth/register",
            json={
                "email": "test@example.com",
                "username": "testuser",
                "password": "TestPass123!",  # Пароль соответствует требованиям: 12+ символов, заглавные, строчные, цифры, спецсимволы
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "test@example.com"
        assert data["username"] == "testuser"
        assert "id" in data

    async def test_register_duplicate_email(self, client: AsyncClient, test_session: AsyncSession):
        """Регистрация с существующим email."""
        # Создаем пользователя
        await test_session.execute(
            insert(UserModel).values(
                email="existing@example.com",
                username="existing",
                hashed_password=get_password_hash("password"),
                is_active=True,
                is_superuser=False,
            )
        )
        await test_session.commit()
        
        # Пытаемся зарегистрироваться с тем же email
        response = await client.post(
            "/auth/register",
            json={
                "email": "existing@example.com",
                "username": "newuser",
                "password": "password123",
            }
        )
        
        assert response.status_code == 400

    async def test_register_duplicate_username(self, client: AsyncClient, test_session: AsyncSession):
        """Регистрация с существующим username."""
        await test_session.execute(
            insert(UserModel).values(
                email="unique@example.com",
                username="taken",
                hashed_password=get_password_hash("password"),
                is_active=True,
                is_superuser=False,
            )
        )
        await test_session.commit()
        
        response = await client.post(
            "/auth/register",
            json={
                "email": "new@example.com",
                "username": "taken",
                "password": "password123",
            }
        )
        
        assert response.status_code == 400

    async def test_login_success(self, client: AsyncClient, test_session: AsyncSession):
        """Успешный вход."""
        # Создаем пользователя
        await test_session.execute(
            insert(UserModel).values(
                email="login@example.com",
                username="loginuser",
                hashed_password=get_password_hash("correctpassword"),
                is_active=True,
                is_superuser=False,
            )
        )
        await test_session.commit()
        
        response = await client.post(
            "/auth/login",
            json={
                "username": "loginuser",
                "password": "correctpassword",
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    async def test_login_wrong_password(self, client: AsyncClient, test_session: AsyncSession):
        """Вход с неправильным паролем."""
        await test_session.execute(
            insert(UserModel).values(
                email="wrong@example.com",
                username="wrongpass",
                hashed_password=get_password_hash("correctpassword"),
                is_active=True,
                is_superuser=False,
            )
        )
        await test_session.commit()
        
        response = await client.post(
            "/auth/login",
            json={
                "username": "wrongpass",
                "password": "wrongpassword",
            }
        )
        
        assert response.status_code == 400

    async def test_login_inactive_user(self, client: AsyncClient, test_session: AsyncSession):
        """Вход заблокированного пользователя."""
        await test_session.execute(
            insert(UserModel).values(
                email="inactive@example.com",
                username="inactive",
                hashed_password=get_password_hash("password"),
                is_active=False,
                is_superuser=False,
            )
        )
        await test_session.commit()
        
        response = await client.post(
            "/auth/login",
            json={
                "username": "inactive",
                "password": "password",
            }
        )
        
        assert response.status_code == 400

    async def test_refresh_token(self, client: AsyncClient, test_session: AsyncSession):
        """Обновление токена."""
        # Создаем пользователя и получаем токены
        await test_session.execute(
            insert(UserModel).values(
                email="refresh@example.com",
                username="refreshuser",
                hashed_password=get_password_hash("password"),
                is_active=True,
                is_superuser=False,
            )
        )
        await test_session.commit()
        
        # Логин
        login_response = await client.post(
            "/auth/login",
            json={"username": "refreshuser", "password": "password"}
        )
        tokens = login_response.json()
        
        # Refresh
        refresh_response = await client.post(
            "/auth/refresh",
            json={"refresh_token": tokens["refresh_token"]}
        )
        
        assert refresh_response.status_code == 200
        data = refresh_response.json()
        assert "access_token" in data
        assert "refresh_token" in data

    async def test_get_me(self, client: AsyncClient, test_session: AsyncSession):
        """Получение информации о текущем пользователе."""
        # Создаем пользователя и получаем токены
        await test_session.execute(
            insert(UserModel).values(
                email="me@example.com",
                username="meuser",
                hashed_password=get_password_hash("password"),
                is_active=True,
                is_superuser=False,
            )
        )
        await test_session.commit()
        
        # Логин
        login_response = await client.post(
            "/auth/login",
            json={"username": "meuser", "password": "password"}
        )
        tokens = login_response.json()
        
        # Получаем информацию о себе
        response = await client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {tokens['access_token']}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "meuser"
        assert data["email"] == "me@example.com"

    async def test_get_me_unauthorized(self, client: AsyncClient):
        """Получение информации без токена."""
        response = await client.get("/auth/me")
        assert response.status_code == 401


# =============================================================================
# Admin Users Tests
# =============================================================================

class TestAdminUsers:
    """Тесты для админ-панели (пользователи)."""

    async def _get_admin_token(self, client: AsyncClient, test_session: AsyncSession):
        """Получение токена суперпользователя."""
        await test_session.execute(
            insert(UserModel).values(
                email="admin@example.com",
                username="admin",
                hashed_password=get_password_hash("adminpass"),
                is_active=True,
                is_superuser=True,
            )
        )
        await test_session.commit()
        
        login_response = await client.post(
            "/auth/login",
            json={"username": "admin", "password": "adminpass"}
        )
        return login_response.json()

    async def test_get_all_users(self, client: AsyncClient, test_session: AsyncSession):
        """Получение списка пользователей (админ)."""
        tokens = await self._get_admin_token(client, test_session)
        
        response = await client.get(
            "/admin/users",
            headers={"Authorization": f"Bearer {tokens['access_token']}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "items" in data

    async def test_get_all_users_unauthorized(self, client: AsyncClient):
        """Получение списка пользователей без авторизации."""
        response = await client.get("/admin/users")
        assert response.status_code == 401

    async def test_get_all_users_not_superuser(self, client: AsyncClient, test_session: AsyncSession):
        """Получение списка пользователей (не суперпользователь)."""
        # Создаем обычного пользователя
        await test_session.execute(
            insert(UserModel).values(
                email="user@example.com",
                username="regularuser",
                hashed_password=get_password_hash("password"),
                is_active=True,
                is_superuser=False,
            )
        )
        await test_session.commit()
        
        login_response = await client.post(
            "/auth/login",
            json={"username": "regularuser", "password": "password"}
        )
        tokens = login_response.json()
        
        response = await client.get(
            "/admin/users",
            headers={"Authorization": f"Bearer {tokens['access_token']}"}
        )
        
        assert response.status_code == 403


# =============================================================================
# Admin Upload Tests
# =============================================================================

class TestAdminUpload:
    """Тесты для загрузки файлов."""

    async def _get_admin_token(self, client: AsyncClient, test_session: AsyncSession):
        """Получение токена суперпользователя."""
        # Проверяем, есть ли уже админ
        result = await test_session.execute(
            select(UserModel).where(UserModel.username == "admin")
        )
        admin = result.scalar_one_or_none()
        
        if not admin:
            await test_session.execute(
                insert(UserModel).values(
                    email="admin@example.com",
                    username="admin",
                    hashed_password=get_password_hash("adminpass"),
                    is_active=True,
                    is_superuser=True,
                )
            )
            await test_session.commit()
        
        login_response = await client.post(
            "/auth/login",
            json={"username": "admin", "password": "adminpass"}
        )
        return login_response.json()

    async def test_upload_image_unauthorized(self, client: AsyncClient):
        """Загрузка изображения без авторизации."""
        response = await client.post(
            "/admin/upload/image",
            files={"file": ("test.jpg", b"fake image data", "image/jpeg")}
        )
        assert response.status_code == 401

    # NOTE: Полноценные тесты загрузки требуют работающий MinIO
    # Эти тесты проверяют только авторизацию и валидацию


# =============================================================================
# Admin Specialties CRUD Tests
# =============================================================================

class TestAdminSpecialties:
    """Тесты для CRUD специальностей (админ)."""

    async def _get_admin_token(self, client: AsyncClient, test_session: AsyncSession):
        """Получение токена суперпользователя."""
        await test_session.execute(
            insert(UserModel).values(
                email="admin@example.com",
                username="admin",
                hashed_password=get_password_hash("adminpass"),
                is_active=True,
                is_superuser=True,
            )
        )
        await test_session.commit()
        
        login_response = await client.post(
            "/auth/login",
            json={"username": "admin", "password": "adminpass"}
        )
        return login_response.json()

    async def test_get_specialties_list(self, client: AsyncClient, test_session: AsyncSession):
        """Получение списка специальностей (админ)."""
        tokens = await self._get_admin_token(client, test_session)
        
        response = await client.get(
            "/admin/specialties",
            headers={"Authorization": f"Bearer {tokens['access_token']}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data

    async def test_create_specialty(self, client: AsyncClient, test_session: AsyncSession):
        """Создание специальности (админ)."""
        tokens = await self._get_admin_token(client, test_session)
        
        response = await client.post(
            "/admin/specialties",
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
            data={
                "code": "99.99.99",
                "name": "Тестовая специальность",
                "short_description": "Описание",
                "description": "[]",
                "duration": "3 г.",
                "budget_places": 10,
                "paid_places": 5,
                "qualification": "Специалист",
                "exams": "[]",
                "images": "[]",
                "is_popular": False,
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == "99.99.99"
