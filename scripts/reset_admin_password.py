#!/usr/bin/env python3
"""Скрипт для сброса пароля администратора."""

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import select, update
from app.infrastructure.models import User as UserModel
from app.core.security import get_password_hash
from app.core.config import get_settings

settings = get_settings()


async def reset_password(
    username: str = "admin",
    new_password: str = "Admin123!"
):
    """Сбросить пароль администратора."""
    
    engine = create_async_engine(settings.get_database_url, echo=False)
    
    async with engine.begin() as conn:
        # Проверяем существующего пользователя
        result = await conn.execute(
            select(UserModel.id, UserModel.email, UserModel.is_superuser).where(UserModel.username == username)
        )
        user = result.fetchone()
        
        if user:
            print(f"Пользователь '{username}' найден.")
            print(f"  Email: {user[1]}")
            print(f"  Superuser: {user[2]}")
            
            # Сбрасываем пароль
            hashed_password = get_password_hash(new_password)
            await conn.execute(
                update(UserModel).where(UserModel.username == username).values(hashed_password=hashed_password)
            )
            print(f"\n✅ Пароль сброшен для: {username}")
            print(f"Email: admin@anmicius.ru")
            print(f"Пароль: {new_password}")
            print("\nТеперь вы можете войти на https://admin.anmicius.ru/login")
        else:
            print(f"❌ Пользователь '{username}' не найден")
    
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(reset_password())
