from metaway_api.settings import get_settings


async def test_upload_client_photo(client, seed_data, auth_headers) -> None:
    admin = await auth_headers(seed_data["admin_cpf"], seed_data["admin_password"])

    response = await client.post(
        f"/api/v1/clients/{seed_data['client_id']}/photo",
        headers=admin,
        files={"file": ("avatar.png", b"\x89PNG\r\n\x1a\nfake", "image/png")},
    )
    assert response.status_code == 200
    photo_url = response.json()["photo_url"]

    file_response = await client.get(f"/api/v1/files/{photo_url}")
    assert file_response.status_code == 200


async def test_upload_pet_photo(client, seed_data, auth_headers) -> None:
    headers = await auth_headers(seed_data["client_cpf"], seed_data["client_password"])

    response = await client.post(
        f"/api/v1/pets/{seed_data['pet_id']}/photo",
        headers=headers,
        files={"file": ("pet.jpg", b"\xff\xd8\xfffake", "image/jpeg")},
    )
    assert response.status_code == 200
    photo_url = response.json()["photo_url"]

    file_response = await client.get(f"/api/v1/files/{photo_url}")
    assert file_response.status_code == 200


async def test_upload_pet_photo_forbidden(client, seed_data, auth_headers) -> None:
    headers = await auth_headers(seed_data["client_cpf"], seed_data["client_password"])
    response = await client.post(
        f"/api/v1/pets/{seed_data['other_pet_id']}/photo",
        headers=headers,
        files={"file": ("pet.jpg", b"\xff\xd8\xfffake", "image/jpeg")},
    )
    assert response.status_code == 403


async def test_upload_invalid_format(client, seed_data, auth_headers) -> None:
    admin = await auth_headers(seed_data["admin_cpf"], seed_data["admin_password"])
    response = await client.post(
        f"/api/v1/clients/{seed_data['client_id']}/photo",
        headers=admin,
        files={"file": ("arquivo.txt", b"texto", "text/plain")},
    )
    assert response.status_code == 400


async def test_upload_oversized(client, seed_data, auth_headers) -> None:
    admin = await auth_headers(seed_data["admin_cpf"], seed_data["admin_password"])
    settings = get_settings()
    old_limit = settings.upload_max_size_mb
    settings.upload_max_size_mb = 1
    try:
        response = await client.post(
            f"/api/v1/clients/{seed_data['client_id']}/photo",
            headers=admin,
            files={
                "file": ("grande.png", b"a" * (1024 * 1024 + 1), "image/png")
            },
        )
    finally:
        settings.upload_max_size_mb = old_limit
    assert response.status_code == 400
