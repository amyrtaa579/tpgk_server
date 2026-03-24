#!/usr/bin/env python3
"""Скрипт для создания суперпользователя."""

import asyncio
import sys
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
        print(f"   Password: {password}")
        print(f"\n📝 Для входа используйте:")
        print(f"   POST /auth/login")
        print(f"   {{\"username\": \"{username}\", \"password\": \"{password}\"}}")
        
        return True


async def main():
    """Точка входа."""
    # Данные по умолчанию
    email = "admin@anmicius.ru"
    username = "admin"
    password = "Admin@123"
    
    # Можно передать через аргументы
    if len(sys.argv) >= 4:
        email = sys.argv[1]
        username = sys.argv[2]
        password = sys.argv[3]
    
    try:
        await create_superuser(email, username, password)
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
