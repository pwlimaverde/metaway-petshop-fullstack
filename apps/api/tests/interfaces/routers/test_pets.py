

async def test_pets_admin_crud(client, seed_data, auth_headers) -> None:
    admin = await auth_headers(seed_data["admin_cpf"], seed_data["admin_password"])

    created = await client.post(
        "/api/v1/pets",
        headers=admin,
        json={
            "client_id": seed_data["client_id"],
            "breed_id": seed_data["breed_id"],
            "name": "Thor",
            "birth_date": "2022-03-04",
        },
    )
    assert created.status_code == 201
    pet_id = created.json()["id"]

    deleted = await client.delete(f"/api/v1/pets/{pet_id}", headers=admin)
    assert deleted.status_code == 204


async def test_client_cannot_create_pet(client, seed_data, auth_headers) -> None:
    headers = await auth_headers(seed_data["client_cpf"], seed_data["client_password"])
    response = await client.post(
        "/api/v1/pets",
        headers=headers,
        json={
            "client_id": seed_data["client_id"],
            "breed_id": seed_data["breed_id"],
            "name": "Não Pode",
            "birth_date": "2022-03-04",
        },
    )
    assert response.status_code == 403


async def test_pets_ownership(client, seed_data, auth_headers) -> None:
    admin = await auth_headers(seed_data["admin_cpf"], seed_data["admin_password"])
    headers = await auth_headers(seed_data["client_cpf"], seed_data["client_password"])

    created = await client.post(
        "/api/v1/pets",
        headers=admin,
        json={
            "client_id": seed_data["client_id"],
            "breed_id": seed_data["breed_id"],
            "name": "Buddy",
            "birth_date": "2022-03-04",
        },
    )
    pet_id = created.json()["id"]

    listed = await client.get("/api/v1/pets", headers=headers)
    assert listed.status_code == 200
    listed_ids = {item["id"] for item in listed.json()}
    assert seed_data["other_pet_id"] not in listed_ids

    own_detail = await client.get(f"/api/v1/pets/{pet_id}", headers=headers)
    assert own_detail.status_code == 200

    other = await client.get(
        f"/api/v1/pets/{seed_data['other_pet_id']}", headers=headers
    )
    assert other.status_code == 403

    updated = await client.patch(
        f"/api/v1/pets/{pet_id}",
        headers=headers,
        json={"name": "Buddy Updated"},
    )
    assert updated.status_code == 200

    forbidden_delete = await client.delete(
        f"/api/v1/pets/{pet_id}", headers=headers
    )
    assert forbidden_delete.status_code == 403


async def test_pets_not_found_branches(client, seed_data, auth_headers) -> None:
    admin = await auth_headers(seed_data["admin_cpf"], seed_data["admin_password"])

    assert (
        await client.post(
            "/api/v1/pets",
            headers=admin,
            json={
                "client_id": 999999,
                "breed_id": seed_data["breed_id"],
                "name": "X",
                "birth_date": "2022-01-01",
            },
        )
    ).status_code == 404

    assert (
        await client.post(
            "/api/v1/pets",
            headers=admin,
            json={
                "client_id": seed_data["client_id"],
                "breed_id": 999999,
                "name": "X",
                "birth_date": "2022-01-01",
            },
        )
    ).status_code == 404

    assert (await client.get("/api/v1/pets/999999", headers=admin)).status_code == 404
    assert (
        await client.patch("/api/v1/pets/999999", headers=admin, json={"name": "x"})
    ).status_code == 404
    assert (
        await client.delete("/api/v1/pets/999999", headers=admin)
    ).status_code == 404


async def test_pet_transfer_forbidden(client, seed_data, auth_headers) -> None:
    headers = await auth_headers(seed_data["client_cpf"], seed_data["client_password"])
    response = await client.patch(
        f"/api/v1/pets/{seed_data['pet_id']}",
        headers=headers,
        json={"client_id": seed_data["other_client_id"]},
    )
    assert response.status_code == 403


async def test_pet_update_missing_breed(client, seed_data, auth_headers) -> None:
    admin = await auth_headers(seed_data["admin_cpf"], seed_data["admin_password"])
    response = await client.patch(
        f"/api/v1/pets/{seed_data['pet_id']}",
        headers=admin,
        json={"breed_id": 999999},
    )
    assert response.status_code == 404


async def test_pets_unlinked_client(
    client, seed_data, auth_headers, unlinked_client_user
) -> None:
    headers = await auth_headers(
        unlinked_client_user["cpf"], unlinked_client_user["password"]
    )
    response = await client.get("/api/v1/pets", headers=headers)
    assert response.status_code == 200
    assert response.json() == []


async def test_upload_pet_photo_missing(client, seed_data, auth_headers) -> None:
    admin = await auth_headers(seed_data["admin_cpf"], seed_data["admin_password"])
    response = await client.post(
        "/api/v1/pets/999999/photo",
        headers=admin,
        files={"file": ("pet.png", b"\x89PNG\r\n\x1a\nx", "image/png")},
    )
    assert response.status_code == 404
