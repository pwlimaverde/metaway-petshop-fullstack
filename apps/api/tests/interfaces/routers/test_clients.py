async def test_clients_full_crud_admin(client, seed_data, auth_headers) -> None:
    admin = await auth_headers(seed_data["admin_cpf"], seed_data["admin_password"])

    created = await client.post(
        "/api/v1/clients",
        headers=admin,
        json={"name": "Cliente Novo", "cpf": "47525534144"},
    )
    assert created.status_code == 201
    client_id = created.json()["id"]
    assert created.json()["cpf"] == "47525534144"

    listed = await client.get("/api/v1/clients", headers=admin)
    assert listed.status_code == 200
    assert any(item["id"] == client_id for item in listed.json())

    detail = await client.get(f"/api/v1/clients/{client_id}", headers=admin)
    assert detail.status_code == 200
    assert detail.json()["cpf"] == "47525534144"

    updated = await client.patch(
        f"/api/v1/clients/{client_id}",
        headers=admin,
        json={"name": "Cliente Alterado", "cpf": "62704828105"},
    )
    assert updated.status_code == 200
    assert updated.json()["name"] == "Cliente Alterado"
    assert updated.json()["cpf"] == "62704828105"

    deleted = await client.delete(f"/api/v1/clients/{client_id}", headers=admin)
    assert deleted.status_code == 204


async def test_client_me_endpoints(client, seed_data, auth_headers) -> None:
    headers = await auth_headers(seed_data["client_cpf"], seed_data["client_password"])

    me = await client.get("/api/v1/clients/me", headers=headers)
    assert me.status_code == 200
    assert me.json()["id"] == seed_data["client_id"]
    assert me.json()["cpf"] == seed_data["client_cpf"]

    updated = await client.patch(
        "/api/v1/clients/me",
        headers=headers,
        json={"name": "Meu Nome Novo"},
    )
    assert updated.status_code == 200
    assert updated.json()["name"] == "Meu Nome Novo"


async def test_client_cannot_list_clients(client, seed_data, auth_headers) -> None:
    headers = await auth_headers(seed_data["client_cpf"], seed_data["client_password"])
    response = await client.get("/api/v1/clients", headers=headers)
    assert response.status_code == 403


async def test_clients_not_found_branches(client, seed_data, auth_headers) -> None:
    admin = await auth_headers(seed_data["admin_cpf"], seed_data["admin_password"])

    assert (
        await client.get("/api/v1/clients/999999", headers=admin)
    ).status_code == 404
    assert (
        await client.patch("/api/v1/clients/999999", headers=admin, json={"name": "X"})
    ).status_code == 404
    assert (
        await client.delete("/api/v1/clients/999999", headers=admin)
    ).status_code == 404
