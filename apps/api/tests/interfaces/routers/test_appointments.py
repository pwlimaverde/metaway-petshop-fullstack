from datetime import UTC, datetime


async def test_appointments_admin_crud(client, seed_data, auth_headers) -> None:
    admin = await auth_headers(seed_data["admin_cpf"], seed_data["admin_password"])

    created = await client.post(
        "/api/v1/appointments",
        headers=admin,
        json={
            "pet_id": seed_data["pet_id"],
            "descricao": "Vacina",
            "valor": "120.50",
            "data": datetime.now(UTC).isoformat(),
        },
    )
    assert created.status_code == 201
    appt_id = created.json()["id"]
    assert created.json()["status"] == "AGENDADO"

    deleted = await client.delete(f"/api/v1/appointments/{appt_id}", headers=admin)
    assert deleted.status_code == 204


async def test_client_cannot_create_appointment(
    client, seed_data, auth_headers
) -> None:
    headers = await auth_headers(seed_data["client_cpf"], seed_data["client_password"])
    response = await client.post(
        "/api/v1/appointments",
        headers=headers,
        json={
            "pet_id": seed_data["pet_id"],
            "descricao": "Não Pode",
            "valor": "50.00",
            "data": datetime.now(UTC).isoformat(),
        },
    )
    assert response.status_code == 403


async def test_appointments_ownership(client, seed_data, auth_headers) -> None:
    admin = await auth_headers(seed_data["admin_cpf"], seed_data["admin_password"])
    headers = await auth_headers(seed_data["client_cpf"], seed_data["client_password"])

    created = await client.post(
        "/api/v1/appointments",
        headers=admin,
        json={
            "pet_id": seed_data["pet_id"],
            "descricao": "Check-up",
            "valor": "80.00",
            "data": datetime.now(UTC).isoformat(),
        },
    )
    appt_id = created.json()["id"]

    listed = await client.get("/api/v1/appointments", headers=headers)
    assert listed.status_code == 200
    listed_ids = {item["id"] for item in listed.json()}
    assert seed_data["other_appointment_id"] not in listed_ids

    own = await client.get(f"/api/v1/appointments/{appt_id}", headers=headers)
    assert own.status_code == 200

    other = await client.get(
        f"/api/v1/appointments/{seed_data['other_appointment_id']}",
        headers=headers,
    )
    assert other.status_code == 403

    updated = await client.patch(
        f"/api/v1/appointments/{appt_id}",
        headers=headers,
        json={"descricao": "Check-up Updated"},
    )
    assert updated.status_code == 403

    # Client still cannot update status of own appointment
    status_updated = await client.patch(
        f"/api/v1/appointments/{appt_id}",
        headers=headers,
        json={"status": "EM_ANDAMENTO"},
    )
    assert status_updated.status_code == 403

    forbidden_delete = await client.delete(
        f"/api/v1/appointments/{appt_id}", headers=headers
    )
    assert forbidden_delete.status_code == 403


async def test_appointments_not_found_branches(client, seed_data, auth_headers) -> None:
    admin = await auth_headers(seed_data["admin_cpf"], seed_data["admin_password"])

    assert (
        await client.post(
            "/api/v1/appointments",
            headers=admin,
            json={
                "pet_id": 999999,
                "descricao": "X",
                "valor": "10.00",
                "data": datetime.now(UTC).isoformat(),
            },
        )
    ).status_code == 404

    assert (
        await client.get("/api/v1/appointments/999999", headers=admin)
    ).status_code == 404
    assert (
        await client.patch(
            "/api/v1/appointments/999999",
            headers=admin,
            json={"descricao": "x"},
        )
    ).status_code == 404
    assert (
        await client.delete("/api/v1/appointments/999999", headers=admin)
    ).status_code == 404


async def test_appointment_update_missing_pet(client, seed_data, auth_headers) -> None:
    admin = await auth_headers(seed_data["admin_cpf"], seed_data["admin_password"])
    response = await client.patch(
        f"/api/v1/appointments/{seed_data['appointment_id']}",
        headers=admin,
        json={"pet_id": 999999},
    )
    assert response.status_code == 404


async def test_appointment_update_foreign_pet(client, seed_data, auth_headers) -> None:
    headers = await auth_headers(seed_data["client_cpf"], seed_data["client_password"])
    response = await client.patch(
        f"/api/v1/appointments/{seed_data['appointment_id']}",
        headers=headers,
        json={"pet_id": seed_data["other_pet_id"]},
    )
    assert response.status_code == 403
