#!/usr/bin/env python3
"""Скрипт для создания суперпользователя."""

import asyncio
import sys
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import select

# Добавляем путь к приложению
sys.path.insert(0, '/app')

from app.infrastructure.models import UserModel
from app.core.jwt import get_password_hash
from app.core.config import get_settings

settings = get_settings()


async def create_superuser(email: str, username: str, password: str):
    """Создание суперпользователя."""

    engine = create_async_engine(
        settings.get_database_url,
        echo=False,
    )

    async_session_maker = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session_maker() as session:
        # Проверка существующего пользователя
        result = await session.execute(
            select(UserModel).where(
                (UserModel.email == email) | (UserModel.username == username)
            )
        )
        existing = result.scalar_one_or_none()

        if existing:
            print(f"⚠️  Пользователь уже существует: {existing.username}")
            return False

        # Создание суперпользователя
        user = UserModel(
            email=email,
            username=username,
            hashed_password=get_password_hash(password),
            is_active=True,
            is_superuser=True,
        )

        session.add(user)
        await session.commit()

        print(f"✅ Суперпользователь создан:")
        print(f"   Email: {email}")
        print(f"   Username: {username}")
        print(f"   Password: {'*' * len(password)}")
        print(f"\n📝 Для входа используйте:")
        print(f"   POST /auth/login")
        print(f"   {{\"username\": \"{username}\", \"password\": \"<ваш_пароль>\"}}")

        return True


async def main():
    """Точка входа."""
    # Получаем данные из переменных окружения или используем значения по умолчанию
    email = os.getenv("ADMIN_EMAIL", "admin@anmicius.ru")
    username = os.getenv("ADMIN_USERNAME", "admin")
    password = os.getenv("ADMIN_PASSWORD")
    
    # Если пароль не передан через переменную окружения, запрашиваем ввод
    if not password:
        if len(sys.argv) >= 4:
            # Если переданы аргументы командной строки
            email = sys.argv[1]
            username = sys.argv[2]
            password = sys.argv[3]
        else:
            # Интерактивный ввод пароля
            import getpass
            print("🔐 Создание суперпользователя")
            print(f"Email: {email}")
            print(f"Username: {username}")
            password = getpass.getpass("Пароль: ")
            
            if not password:
                print("❌ Пароль не может быть пустым")
                sys.exit(1)
            
            # Подтверждение пароля
            password_confirm = getpass.getpass("Подтвердите пароль: ")
            if password != password_confirm:
                print("❌ Пароли не совпадают")
                sys.exit(1)

    try:
        await create_superuser(email, username, password)
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
