async def test_contacts_admin_crud(client, seed_data, auth_headers) -> None:
    admin = await auth_headers(seed_data["admin_cpf"], seed_data["admin_password"])

    created = await client.post(
        f"/api/v1/clients/{seed_data['client_id']}/contacts",
        headers=admin,
        json={"tag": "backup", "tipo": "EMAIL", "valor": "backup@example.com"},
    )
    assert created.status_code == 201
    contact_id = created.json()["id"]

    deleted = await client.delete(f"/api/v1/contacts/{contact_id}", headers=admin)
    assert deleted.status_code == 204


async def test_client_cannot_create_contact(client, seed_data, auth_headers) -> None:
    headers = await auth_headers(seed_data["client_cpf"], seed_data["client_password"])
    response = await client.post(
        f"/api/v1/clients/{seed_data['client_id']}/contacts",
        headers=headers,
        json={"tag": "x", "tipo": "EMAIL", "valor": "x@example.com"},
    )
    assert response.status_code == 403


async def test_client_can_create_own_contact(client, seed_data, auth_headers) -> None:
    headers = await auth_headers(seed_data["client_cpf"], seed_data["client_password"])
    response = await client.post(
        "/api/v1/clients/me/contacts",
        headers=headers,
        json={"tag": "pessoal", "tipo": "EMAIL", "valor": "cliente@me.com"},
    )
    assert response.status_code == 201
    assert response.json()["client_id"] == seed_data["client_id"]


async def test_contacts_ownership(client, seed_data, auth_headers) -> None:
    admin = await auth_headers(seed_data["admin_cpf"], seed_data["admin_password"])
    headers = await auth_headers(seed_data["client_cpf"], seed_data["client_password"])

    created = await client.post(
        f"/api/v1/clients/{seed_data['client_id']}/contacts",
        headers=admin,
        json={"tag": "own", "tipo": "EMAIL", "valor": "own@example.com"},
    )
    contact_id = created.json()["id"]

    my_contacts = await client.get("/api/v1/clients/me/contacts", headers=headers)
    assert my_contacts.status_code == 200

    updated = await client.patch(
        f"/api/v1/contacts/{contact_id}",
        headers=headers,
        json={"valor": "novo@email.com"},
    )
    assert updated.status_code == 200
    assert updated.json()["valor"] == "novo@email.com"

    forbidden = await client.patch(
        f"/api/v1/contacts/{seed_data['other_contact_id']}",
        headers=headers,
        json={"valor": "hack@email.com"},
    )
    assert forbidden.status_code == 403

    deleted = await client.delete(f"/api/v1/contacts/{contact_id}", headers=headers)
    assert deleted.status_code == 204


async def test_contacts_not_found_branches(client, seed_data, auth_headers) -> None:
    admin = await auth_headers(seed_data["admin_cpf"], seed_data["admin_password"])

    assert (
        await client.post(
            "/api/v1/clients/999999/contacts",
            headers=admin,
            json={"tag": "x", "tipo": "EMAIL", "valor": "x@y.com"},
        )
    ).status_code == 404
    assert (
        await client.get("/api/v1/clients/999999/contacts", headers=admin)
    ).status_code == 404
    assert (
        await client.patch(
            "/api/v1/contacts/999999", headers=admin, json={"valor": "x"}
        )
    ).status_code == 404
    assert (
        await client.delete("/api/v1/contacts/999999", headers=admin)
    ).status_code == 404
