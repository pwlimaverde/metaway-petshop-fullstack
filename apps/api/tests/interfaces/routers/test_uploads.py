from io import BytesIO

from PIL import Image

from metaway_api.settings import get_settings


def _make_image_bytes(image_format: str) -> bytes:
    image = Image.new("RGB", (1200, 800), color=(255, 0, 0))
    output = BytesIO()
    image.save(output, format=image_format)
    return output.getvalue()


async def test_upload_client_photo(client, seed_data, auth_headers) -> None:
    admin = await auth_headers(seed_data["admin_cpf"], seed_data["admin_password"])

    response = await client.post(
        f"/api/v1/clients/{seed_data['client_id']}/photo",
        headers=admin,
        files={"file": ("avatar.png", _make_image_bytes("PNG"), "image/png")},
    )
    assert response.status_code == 200
    photo_url = response.json()["photo_url"]

    file_response = await client.get(f"/api/v1/files/{photo_url}")
    assert file_response.status_code == 200
    with Image.open(BytesIO(file_response.content)) as image:
        assert image.size == (512, 512)


async def test_upload_pet_photo(client, seed_data, auth_headers) -> None:
    headers = await auth_headers(seed_data["client_cpf"], seed_data["client_password"])

    response = await client.post(
        f"/api/v1/pets/{seed_data['pet_id']}/photo",
        headers=headers,
        files={"file": ("pet.jpg", _make_image_bytes("JPEG"), "image/jpeg")},
    )
    assert response.status_code == 200
    photo_url = response.json()["photo_url"]

    file_response = await client.get(f"/api/v1/files/{photo_url}")
    assert file_response.status_code == 200
    with Image.open(BytesIO(file_response.content)) as image:
        assert image.size == (512, 512)


async def test_upload_pet_photo_forbidden(client, seed_data, auth_headers) -> None:
    headers = await auth_headers(seed_data["client_cpf"], seed_data["client_password"])
    response = await client.post(
        f"/api/v1/pets/{seed_data['other_pet_id']}/photo",
        headers=headers,
        files={"file": ("pet.jpg", _make_image_bytes("JPEG"), "image/jpeg")},
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
            files={"file": ("grande.png", b"a" * (1024 * 1024 + 1), "image/png")},
        )
    finally:
        settings.upload_max_size_mb = old_limit
    assert response.status_code == 400
