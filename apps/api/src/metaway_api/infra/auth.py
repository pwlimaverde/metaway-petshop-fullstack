from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from metaway_api.domain.enums import UserRole
from metaway_api.infra.database import get_db_session
from metaway_api.infra.models import User
from metaway_api.infra.repositories import UserRepository
from metaway_api.settings import get_settings

settings = get_settings()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.api_prefix}/auth/login")

_UNAUTHORIZED_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Credenciais inválidas.",
    headers={"WWW-Authenticate": "Bearer"},
)


def _normalize_role(role: str | UserRole) -> str:
    if isinstance(role, UserRole):
        return role.value
    return role


def create_access_token(user: User) -> str:
    expires_at = datetime.now(UTC) + timedelta(minutes=settings.jwt_expire_minutes)
    payload = {
        "sub": str(user.id),
        "role": _normalize_role(user.role),
        "client_id": user.client_id,
        "exp": expires_at,
    }
    return jwt.encode(
        payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm
    )


def decode_access_token(token: str) -> dict[str, Any]:
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
    except JWTError as exc:
        raise _UNAUTHORIZED_EXCEPTION from exc

    if "sub" not in payload or "role" not in payload or "exp" not in payload:
        raise _UNAUTHORIZED_EXCEPTION
    return payload


def is_admin(user: User) -> bool:
    return _normalize_role(user.role) == UserRole.ADMIN.value


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_db_session),
) -> User:
    payload = decode_access_token(token)
    user_id = payload.get("sub")
    if user_id is None:
        raise _UNAUTHORIZED_EXCEPTION

    try:
        parsed_user_id = int(user_id)
    except (TypeError, ValueError) as exc:
        raise _UNAUTHORIZED_EXCEPTION from exc

    user = await UserRepository(session).get_by_id(parsed_user_id)
    if user is None:
        raise _UNAUTHORIZED_EXCEPTION
    return user


def require_roles(*roles: UserRole | str):
    allowed = {_normalize_role(role) for role in roles}

    async def dependency(current_user: User = Depends(get_current_user)) -> User:
        if _normalize_role(current_user.role) not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você não tem permissão para este recurso.",
            )
        return current_user

    return dependency


def check_ownership(resource_client_id: int | None, current_user: User) -> None:
    if is_admin(current_user):
        return
    if current_user.client_id is None or resource_client_id != current_user.client_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado para este recurso.",
        )
