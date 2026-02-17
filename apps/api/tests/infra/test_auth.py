from datetime import UTC, datetime, timedelta

import pytest
from fastapi import HTTPException
from jose import jwt

from metaway_api.domain.enums import UserRole
from metaway_api.infra.auth import (
    check_ownership,
    create_access_token,
    decode_access_token,
    is_admin,
)
from metaway_api.infra.models import User
from metaway_api.infra.security import hash_password
from metaway_api.settings import get_settings


def _make_user(
    *,
    user_id: int = 1,
    role: UserRole = UserRole.ADMIN,
    client_id: int | None = None,
) -> User:
    user = User(
        cpf="52998224725",
        name="Test",
        role=role,
        password_hash=hash_password("x"),
        client_id=client_id,
    )
    user.id = user_id
    return user


def test_create_access_token_contains_claims() -> None:
    user = _make_user(user_id=42, role=UserRole.CLIENTE, client_id=10)
    token = create_access_token(user)
    settings = get_settings()
    payload = jwt.decode(
        token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm]
    )
    assert payload["sub"] == "42"
    assert payload["role"] == "CLIENTE"
    assert payload["client_id"] == 10
    assert "exp" in payload


def test_decode_access_token_valid() -> None:
    settings = get_settings()
    token = jwt.encode(
        {
            "sub": "1",
            "role": "ADMIN",
            "client_id": None,
            "exp": datetime.now(UTC) + timedelta(minutes=30),
        },
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )
    payload = decode_access_token(token)
    assert payload["sub"] == "1"
    assert payload["role"] == "ADMIN"


def test_decode_access_token_expired() -> None:
    settings = get_settings()
    token = jwt.encode(
        {
            "sub": "1",
            "role": "ADMIN",
            "client_id": None,
            "exp": datetime.now(UTC) - timedelta(minutes=5),
        },
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )
    with pytest.raises(HTTPException) as exc_info:
        decode_access_token(token)
    assert exc_info.value.status_code == 401


def test_decode_access_token_missing_fields() -> None:
    settings = get_settings()
    token = jwt.encode(
        {"sub": "1", "exp": datetime.now(UTC) + timedelta(minutes=30)},
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )
    with pytest.raises(HTTPException):
        decode_access_token(token)


def test_decode_access_token_invalid_signature() -> None:
    token = jwt.encode(
        {
            "sub": "1",
            "role": "ADMIN",
            "client_id": None,
            "exp": datetime.now(UTC) + timedelta(minutes=30),
        },
        "wrong_secret",
        algorithm="HS256",
    )
    with pytest.raises(HTTPException) as exc_info:
        decode_access_token(token)
    assert exc_info.value.status_code == 401


def test_is_admin() -> None:
    admin = _make_user(role=UserRole.ADMIN)
    cliente = _make_user(role=UserRole.CLIENTE)
    assert is_admin(admin) is True
    assert is_admin(cliente) is False


def test_check_ownership_admin_bypasses() -> None:
    admin = _make_user(role=UserRole.ADMIN)
    check_ownership(999, admin)  # Should not raise


def test_check_ownership_matching_client() -> None:
    user = _make_user(role=UserRole.CLIENTE, client_id=10)
    check_ownership(10, user)  # Should not raise


def test_check_ownership_different_client() -> None:
    user = _make_user(role=UserRole.CLIENTE, client_id=10)
    with pytest.raises(HTTPException) as exc_info:
        check_ownership(20, user)
    assert exc_info.value.status_code == 403


def test_check_ownership_no_client_id() -> None:
    user = _make_user(role=UserRole.CLIENTE, client_id=None)
    with pytest.raises(HTTPException) as exc_info:
        check_ownership(10, user)
    assert exc_info.value.status_code == 403
