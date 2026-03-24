"""Зависимости для аутентификации."""

from typing import Optional, List
from fastapi import Depends, HTTPException, status, Security
from fastapi.security import OAuth2PasswordBearer, SecurityScopes

from app.core.jwt import verify_token
from app.infrastructure.repositories import UserRepository
from app.infrastructure.database import get_db_session
from sqlalchemy.ext.asyncio import AsyncSession

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login/oauth", auto_error=False)


async def get_current_user_id(
    security_scopes: SecurityScopes,
    token: str = Depends(oauth2_scheme),
) -> int:
    """Получение ID текущего пользователя из токена."""
    # Проверка scopes
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{" ".join(security_scopes.scopes)}"'
    else:
        authenticate_value = "Bearer"
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Не удалось проверить учетные данные",
        headers={"WWW-Authenticate": authenticate_value},
    )
    
    if not token:
        raise credentials_exception
    
    payload = verify_token(token, token_type="access")
    if not payload:
        raise credentials_exception

    user_id = payload.get("sub")
    if not user_id:
        raise credentials_exception
    
    # Проверка scopes в токене
    token_scopes: List[str] = payload.get("scopes", [])
    for scope in security_scopes.scopes:
        if scope not in token_scopes:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Недостаточно прав",
                headers={"WWW-Authenticate": authenticate_value},
            )

    return int(user_id)


async def get_current_user(
    security_scopes: SecurityScopes,
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Получение текущего пользователя."""
    repository = UserRepository(session)
    user = await repository.get_by_id(user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не найден",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Учетная запись заблокирована",
        )

    return {
        "id": user.id,
        "email": user.email,
        "username": user.username,
        "is_active": user.is_active,
        "is_superuser": user.is_superuser,
        "created_at": user.created_at,
    }


async def get_current_superuser(
    current_user: dict = Depends(get_current_user),
) -> dict:
    """Проверка на суперпользователя."""
    if not current_user.get("is_superuser"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Требуется права суперпользователя",
        )
    return current_user
