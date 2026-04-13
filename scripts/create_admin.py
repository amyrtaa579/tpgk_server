#!/usr/bin/env python3
"""Скрипт для создания или сброса пароля администратора."""

import asyncio
import sys
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import select
from app.infrastructure.models import User as UserModel
from app.core.security import get_password_hash
from app.core.config import get_settings

settings = get_settings()


async def create_or_reset_admin(
    email: str = "admin@anmicius.ru",
    username: str = "admin",
    password: str = "Admin123!"
):
    """Создать администратора или сбросить пароль."""
    
    engine = create_async_engine(settings.get_database_url, echo=False)
    async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session_maker() as session:
        # Проверяем существующего пользователя
        result = await session.execute(
            select(UserModel).where(UserModel.username == username)
        )
        user = result.scalar_one_or_none()
        
        if user:
            print(f"Пользователь '{username}' найден.")
            print(f"  Email: {user.email}")
            print(f"  Superuser: {user.is_superuser}")
            
            # Сбрасываем пароль
            user.hashed_password = get_password_hash(password)
            user.is_superuser = True
            user.is_active = True
            await session.commit()
            print(f"\nПароль сброшен для: {username}")
            print(f"Email: {email}")
            print(f"Пароль: {password}")
            print("\nТеперь вы можете войти на https://admin.anmicius.ru/login")
        else:
            # Создаём нового
            new_user = UserModel(
                email=email,
                username=username,
                hashed_password=get_password_hash(password),
                is_superuser=True,
                is_active=True
            )
            session.add(new_user)
            await session.commit()
            print(f"Создан администратор: {username}")
            print(f"Email: {email}")
            print(f"Пароль: {password}")
            print("\nТеперь вы можете войти на https://admin.anmicius.ru/login")
    
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(create_or_reset_admin())
