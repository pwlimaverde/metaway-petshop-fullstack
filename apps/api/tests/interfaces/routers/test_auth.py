from datetime import UTC, datetime, timedelta

import jwt

from metaway_api.settings import get_settings


async def test_login_success(client, seed_data) -> None:
    response = await client.post(
        "/api/v1/auth/login",
        data={
            "username": seed_data["admin_cpf"],
            "password": seed_data["admin_password"],
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


async def test_login_wrong_password(client, seed_data) -> None:
    response = await client.post(
        "/api/v1/auth/login",
        data={"username": seed_data["admin_cpf"], "password": "senha_invalida"},
    )
    assert response.status_code == 401


async def test_login_unknown_cpf(client, seed_data) -> None:
    response = await client.post(
        "/api/v1/auth/login",
        data={"username": "99999999999", "password": "qualquer"},
    )
    assert response.status_code == 401


async def test_expired_token_returns_401(client, seed_data) -> None:
    settings = get_settings()
    expired = jwt.encode(
        {
            "sub": str(seed_data["client_user_id"]),
            "role": "CLIENTE",
            "client_id": seed_data["client_id"],
            "exp": datetime.now(UTC) - timedelta(minutes=5),
        },
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )
    response = await client.get(
        "/api/v1/pets",
        headers={"Authorization": f"Bearer {expired}"},
    )
    assert response.status_code == 401


async def test_non_int_sub_token_returns_401(client, seed_data) -> None:
    settings = get_settings()
    token = jwt.encode(
        {
            "sub": "not-an-int",
            "role": "ADMIN",
            "client_id": None,
            "exp": datetime.now(UTC) + timedelta(minutes=30),
        },
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )
    response = await client.get(
        "/api/v1/users",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 401


async def test_missing_user_token_returns_401(client, seed_data) -> None:
    settings = get_settings()
    token = jwt.encode(
        {
            "sub": "999999",
            "role": "ADMIN",
            "client_id": None,
            "exp": datetime.now(UTC) + timedelta(minutes=30),
        },
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )
    response = await client.get(
        "/api/v1/users",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 401


async def test_no_token_returns_401(client) -> None:
    response = await client.get("/api/v1/users")
    assert response.status_code == 401


async def test_login_rate_limit_returns_429(client, seed_data) -> None:
    payload = {"username": seed_data["admin_cpf"], "password": "senha_invalida"}
    for _ in range(5):
        response = await client.post("/api/v1/auth/login", data=payload)
        assert response.status_code == 401

    response = await client.post("/api/v1/auth/login", data=payload)
    assert response.status_code == 429
