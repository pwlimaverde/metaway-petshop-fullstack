async def test_addresses_admin_crud(client, seed_data, auth_headers) -> None:
    admin = await auth_headers(seed_data["admin_cpf"], seed_data["admin_password"])

    created = await client.post(
        f"/api/v1/clients/{seed_data['client_id']}/addresses",
        headers=admin,
        json={
            "logradouro": "Rua Nova",
            "numero": "10",
            "cidade": "Curitiba",
            "bairro": "Centro",
            "complemento": None,
            "estado": "PR",
            "cep": "80000000",
            "tag": "casa",
        },
    )
    assert created.status_code == 201
    address_id = created.json()["id"]

    listed = await client.get(
        f"/api/v1/clients/{seed_data['client_id']}/addresses",
        headers=admin,
    )
    assert listed.status_code == 200

    deleted = await client.delete(f"/api/v1/addresses/{address_id}", headers=admin)
    assert deleted.status_code == 204


async def test_client_cannot_create_address(client, seed_data, auth_headers) -> None:
    headers = await auth_headers(seed_data["client_cpf"], seed_data["client_password"])
    response = await client.post(
        f"/api/v1/clients/{seed_data['client_id']}/addresses",
        headers=headers,
        json={
            "logradouro": "Rua Não Pode",
            "numero": "5",
            "cidade": "Recife",
            "bairro": "Boa Viagem",
            "complemento": None,
            "estado": "PE",
            "cep": "50000000",
            "tag": "casa",
        },
    )
    assert response.status_code == 403


async def test_client_can_create_own_address(client, seed_data, auth_headers) -> None:
    headers = await auth_headers(seed_data["client_cpf"], seed_data["client_password"])
    response = await client.post(
        "/api/v1/clients/me/addresses",
        headers=headers,
        json={
            "logradouro": "Rua Cliente",
            "numero": "22",
            "cidade": "Florianópolis",
            "bairro": "Centro",
            "complemento": None,
            "estado": "SC",
            "cep": "88000000",
            "tag": "apartamento",
        },
    )
    assert response.status_code == 201
    assert response.json()["client_id"] == seed_data["client_id"]


async def test_addresses_ownership(client, seed_data, auth_headers) -> None:
    admin = await auth_headers(seed_data["admin_cpf"], seed_data["admin_password"])
    headers = await auth_headers(seed_data["client_cpf"], seed_data["client_password"])

    # Create address for client
    created = await client.post(
        f"/api/v1/clients/{seed_data['client_id']}/addresses",
        headers=admin,
        json={
            "logradouro": "Rua Ownership",
            "numero": "15",
            "cidade": "SP",
            "bairro": "Centro",
            "complemento": None,
            "estado": "SP",
            "cep": "01000000",
            "tag": "casa",
        },
    )
    address_id = created.json()["id"]

    # Client can list own
    my_list = await client.get("/api/v1/clients/me/addresses", headers=headers)
    assert my_list.status_code == 200

    # Client can update own
    updated = await client.patch(
        f"/api/v1/addresses/{address_id}",
        headers=headers,
        json={"bairro": "Jardins"},
    )
    assert updated.status_code == 200
    assert updated.json()["bairro"] == "Jardins"

    # Client cannot update other's
    forbidden = await client.patch(
        f"/api/v1/addresses/{seed_data['other_address_id']}",
        headers=headers,
        json={"bairro": "Invasão"},
    )
    assert forbidden.status_code == 403

    # Client can delete own
    deleted = await client.delete(f"/api/v1/addresses/{address_id}", headers=headers)
    assert deleted.status_code == 204


async def test_addresses_not_found_branches(client, seed_data, auth_headers) -> None:
    admin = await auth_headers(seed_data["admin_cpf"], seed_data["admin_password"])

    assert (
        await client.post(
            "/api/v1/clients/999999/addresses",
            headers=admin,
            json={
                "logradouro": "X",
                "numero": "1",
                "cidade": "X",
                "bairro": "X",
                "complemento": None,
                "estado": "SP",
                "cep": "01001000",
                "tag": "x",
            },
        )
    ).status_code == 404
    assert (
        await client.get("/api/v1/clients/999999/addresses", headers=admin)
    ).status_code == 404
    assert (
        await client.patch(
            "/api/v1/addresses/999999", headers=admin, json={"bairro": "x"}
        )
    ).status_code == 404
    assert (
        await client.delete("/api/v1/addresses/999999", headers=admin)
    ).status_code == 404
