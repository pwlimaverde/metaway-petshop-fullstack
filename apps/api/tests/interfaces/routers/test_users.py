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
            "cpf": "11111111111",
            "name": "Sem Vinculo",
            "role": "CLIENTE",
            "password": "StrongPass1!",
        },
    )
    assert response.status_code == 422


async def test_users_full_crud(client, seed_data, auth_headers) -> None:
    admin = await auth_headers(seed_data["admin_cpf"], seed_data["admin_password"])

    # Create client first
    client_resp = await client.post(
        "/api/v1/clients",
        headers=admin,
        json={"name": "Cliente Vinculável", "cpf": "55566677788"},
    )
    assert client_resp.status_code == 201
    client_id = client_resp.json()["id"]

    # Create user
    created = await client.post(
        "/api/v1/users",
        headers=admin,
        json={
            "cpf": "11111111111",
            "name": "Novo Usuário",
            "role": "CLIENTE",
            "password": "StrongPass1!",
            "client_id": client_id,
        },
    )
    assert created.status_code == 201
    user_id = created.json()["id"]

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
        json={"name": "Usuário Atualizado"},
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
        await client.patch(
            "/api/v1/users/999999", headers=admin, json={"name": "N/A"}
        )
    ).status_code == 404
    assert (
        await client.delete("/api/v1/users/999999", headers=admin)
    ).status_code == 404


async def test_create_user_with_missing_client(
    client, seed_data, auth_headers
) -> None:
    admin = await auth_headers(seed_data["admin_cpf"], seed_data["admin_password"])
    response = await client.post(
        "/api/v1/users",
        headers=admin,
        json={
            "cpf": "10101010101",
            "name": "User Sem Cliente",
            "role": "CLIENTE",
            "password": "StrongPass1!",
            "client_id": 999999,
        },
    )
    assert response.status_code == 404


async def test_duplicate_user_cpf(client, seed_data, auth_headers) -> None:
    admin = await auth_headers(seed_data["admin_cpf"], seed_data["admin_password"])
    response = await client.post(
        "/api/v1/users",
        headers=admin,
        json={
            "cpf": seed_data["admin_cpf"],
            "name": "Duplicado",
            "role": "ADMIN",
            "password": "StrongPass1!",
        },
    )
    assert response.status_code == 400


async def test_missing_required_client_name(client, seed_data, auth_headers) -> None:
    admin = await auth_headers(seed_data["admin_cpf"], seed_data["admin_password"])
    response = await client.post(
        "/api/v1/clients",
        headers=admin,
        json={"cpf": "11122233344"},
    )
    assert response.status_code == 422
