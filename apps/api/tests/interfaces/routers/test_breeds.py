async def test_breeds_admin_crud(client, seed_data, auth_headers) -> None:
    admin = await auth_headers(seed_data["admin_cpf"], seed_data["admin_password"])

    created = await client.post(
        "/api/v1/breeds", headers=admin, json={"descricao": "Bulldog"}
    )
    assert created.status_code == 201
    breed_id = created.json()["id"]

    deleted = await client.delete(f"/api/v1/breeds/{breed_id}", headers=admin)
    assert deleted.status_code == 204


async def test_breeds_client_read_only(client, seed_data, auth_headers) -> None:
    admin = await auth_headers(seed_data["admin_cpf"], seed_data["admin_password"])
    headers = await auth_headers(seed_data["client_cpf"], seed_data["client_password"])

    created = await client.post(
        "/api/v1/breeds", headers=admin, json={"descricao": "Border Collie"}
    )
    breed_id = created.json()["id"]

    listed = await client.get("/api/v1/breeds", headers=headers)
    assert listed.status_code == 200
    assert any(item["id"] == breed_id for item in listed.json())

    detail = await client.get(f"/api/v1/breeds/{breed_id}", headers=headers)
    assert detail.status_code == 200

    forbidden = await client.patch(
        f"/api/v1/breeds/{breed_id}",
        headers=headers,
        json={"descricao": "Não Pode"},
    )
    assert forbidden.status_code == 403


async def test_breeds_not_found_branches(client, seed_data, auth_headers) -> None:
    admin = await auth_headers(seed_data["admin_cpf"], seed_data["admin_password"])

    assert (await client.get("/api/v1/breeds/999999", headers=admin)).status_code == 404
    assert (
        await client.patch(
            "/api/v1/breeds/999999", headers=admin, json={"descricao": "X"}
        )
    ).status_code == 404
    assert (
        await client.delete("/api/v1/breeds/999999", headers=admin)
    ).status_code == 404


async def test_duplicate_breed(client, seed_data, auth_headers) -> None:
    admin = await auth_headers(seed_data["admin_cpf"], seed_data["admin_password"])

    response = await client.post(
        "/api/v1/breeds", headers=admin, json={"descricao": "Labrador"}
    )
    assert response.status_code == 400


async def test_update_breed_to_duplicate(client, seed_data, auth_headers) -> None:
    admin = await auth_headers(seed_data["admin_cpf"], seed_data["admin_password"])

    created = await client.post(
        "/api/v1/breeds", headers=admin, json={"descricao": "Unique Breed"}
    )
    breed_id = created.json()["id"]

    response = await client.patch(
        f"/api/v1/breeds/{breed_id}",
        headers=admin,
        json={"descricao": "Labrador"},
    )
    assert response.status_code == 400
