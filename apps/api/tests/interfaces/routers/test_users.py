async def test_client_cannot_access_users(client, seed_data, auth_headers) -> None:
    headers = await auth_headers(seed_data["client_cpf"], seed_data["client_password"])
    response = await client.get("/api/v1/users", headers=headers)
    assert response.status_code == 403


async def test_create_client_user_without_client_id_fails(
    client, seed_data, auth_headers
) -> None:
    headers = await auth_headers(seed_data["admin_cpf"], seed_data["admin_password"])
    response = await client.post(
        "/api/v1/users",
        headers=headers,
        json={
            "cpf": "81618495950",
            "name": "Sem Client",
            "role": "CLIENTE",
            "password": "StrongPass123!",
        },
    )
    assert response.status_code == 422


async def test_users_full_crud(client, seed_data, auth_headers) -> None:
    admin = await auth_headers(seed_data["admin_cpf"], seed_data["admin_password"])

    # Create client first
    client_resp = await client.post(
        "/api/v1/clients",
        headers=admin,
        json={"name": "Cliente Vinculável", "cpf": "16155940789"},
    )
    assert client_resp.status_code == 201
    client_id = client_resp.json()["id"]

    # Create user
    created = await client.post(
        "/api/v1/users",
        headers=admin,
        json={
            "cpf": "47525534144",
            "name": "Novo Usuário Cliente",
            "role": "CLIENTE",
            "password": "StrongPass123!",
            "client_id": client_id,
        },
    )
    assert created.status_code == 201
    user_id = created.json()["id"]
    assert created.json()["name"] == "Novo Usuário Cliente"

    # List
    listed = await client.get("/api/v1/users", headers=admin)
    assert listed.status_code == 200
    assert any(item["id"] == user_id for item in listed.json())

    # Get
    detail = await client.get(f"/api/v1/users/{user_id}", headers=admin)
    assert detail.status_code == 200

    # Update
    updated = await client.patch(
        f"/api/v1/users/{user_id}",
        headers=admin,
        json={
            "role": "ADMIN",
            "name": "Usuário Atualizado",
            "client_id": None,
        },
    )
    assert updated.status_code == 200
    assert updated.json()["name"] == "Usuário Atualizado"

    # Delete
    deleted = await client.delete(f"/api/v1/users/{user_id}", headers=admin)
    assert deleted.status_code == 204


async def test_users_not_found_branches(client, seed_data, auth_headers) -> None:
    admin = await auth_headers(seed_data["admin_cpf"], seed_data["admin_password"])

    assert (await client.get("/api/v1/users/999999", headers=admin)).status_code == 404
    assert (
        await client.patch("/api/v1/users/999999", headers=admin, json={"name": "N/A"})
    ).status_code == 404
    assert (
        await client.delete("/api/v1/users/999999", headers=admin)
    ).status_code == 404


async def test_create_user_with_missing_client(client, seed_data, auth_headers) -> None:
    admin = await auth_headers(seed_data["admin_cpf"], seed_data["admin_password"])
    response = await client.post(
        "/api/v1/users",
        headers=admin,
        json={
            "cpf": "92832764851",
            "name": "Cliente Inexistente",
            "role": "CLIENTE",
            "password": "StrongPass123!",
            "client_id": 999999,
        },
    )
    assert response.status_code == 404


async def test_create_multiple_users_for_same_client(
    client, seed_data, auth_headers
) -> None:
    admin = await auth_headers(seed_data["admin_cpf"], seed_data["admin_password"])
    created_client = await client.post(
        "/api/v1/clients",
        headers=admin,
        json={"name": "Cliente Multi Usuários", "cpf": "47525534144"},
    )
    assert created_client.status_code == 201
    client_id = created_client.json()["id"]

    first_user = await client.post(
        "/api/v1/users",
        headers=admin,
        json={
            "cpf": "62704828105",
            "name": "Responsável Principal",
            "role": "CLIENTE",
            "password": "StrongPass123!",
            "client_id": client_id,
        },
    )
    assert first_user.status_code == 201

    second_user = await client.post(
        "/api/v1/users",
        headers=admin,
        json={
            "cpf": "92832764851",
            "name": "Responsável Secundário",
            "role": "CLIENTE",
            "password": "StrongPass123!",
            "client_id": client_id,
        },
    )
    assert second_user.status_code == 201
    assert second_user.json()["client_id"] == client_id


async def test_duplicate_user_cpf(client, seed_data, auth_headers) -> None:
    admin = await auth_headers(seed_data["admin_cpf"], seed_data["admin_password"])
    response = await client.post(
        "/api/v1/users",
        headers=admin,
        json={
            "cpf": seed_data["admin_cpf"],
            "name": "Duplicado",
            "role": "ADMIN",
            "password": "StrongPass123!",
        },
    )
    assert response.status_code == 400


async def test_missing_required_client_name(client, seed_data, auth_headers) -> None:
    admin = await auth_headers(seed_data["admin_cpf"], seed_data["admin_password"])
    response = await client.post(
        "/api/v1/clients",
        headers=admin,
        json={"cpf": "16155940789"},
    )
    assert response.status_code == 422


async def test_create_user_with_invalid_cpf(client, seed_data, auth_headers) -> None:
    admin = await auth_headers(seed_data["admin_cpf"], seed_data["admin_password"])
    response = await client.post(
        "/api/v1/users",
        headers=admin,
        json={
            "cpf": "12345678900",
            "name": "CPF Invalido",
            "role": "ADMIN",
            "password": "Strong123!",
        },
    )
    assert response.status_code == 422


async def test_create_user_with_weak_password(client, seed_data, auth_headers) -> None:
    admin = await auth_headers(seed_data["admin_cpf"], seed_data["admin_password"])
    response = await client.post(
        "/api/v1/users",
        headers=admin,
        json={
            "cpf": "62704828105",
            "name": "Senha Fraca",
            "role": "ADMIN",
            "password": "abcdef",
        },
    )
    assert response.status_code == 422


async def test_change_my_password(client, seed_data, auth_headers) -> None:
    headers = await auth_headers(seed_data["client_cpf"], seed_data["client_password"])

    changed = await client.patch(
        "/api/v1/users/me/password",
        headers=headers,
        json={
            "current_password": seed_data["client_password"],
            "new_password": "NewPass123!",
        },
    )
    assert changed.status_code == 204

    old_login = await client.post(
        "/api/v1/auth/login",
        data={
            "username": seed_data["client_cpf"],
            "password": seed_data["client_password"],
        },
    )
    assert old_login.status_code == 401

    new_login = await client.post(
        "/api/v1/auth/login",
        data={"username": seed_data["client_cpf"], "password": "NewPass123!"},
    )
    assert new_login.status_code == 200


async def test_change_my_password_with_wrong_current_password(
    client, seed_data, auth_headers
) -> None:
    headers = await auth_headers(seed_data["client_cpf"], seed_data["client_password"])

    response = await client.patch(
        "/api/v1/users/me/password",
        headers=headers,
        json={"current_password": "senha_errada", "new_password": "NewPass123!"},
    )
    assert response.status_code == 400
