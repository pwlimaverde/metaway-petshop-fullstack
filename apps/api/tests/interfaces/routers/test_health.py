async def test_health_endpoint_returns_ok(client) -> None:
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


async def test_metrics_endpoint_returns_data(client) -> None:
    response = await client.get("/api/v1/metrics")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["uptime_seconds"] >= 0
    assert data["memory_mb"] >= 0


async def test_cors_allows_configured_origin(client) -> None:
    from metaway_api.settings import get_settings

    first_origin = get_settings().allowed_origins.split(",")[0].strip()
    response = await client.options(
        "/api/v1/health",
        headers={
            "Origin": first_origin,
            "Access-Control-Request-Method": "GET",
        },
    )
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == first_origin


async def test_cors_blocks_unlisted_origin(client) -> None:
    response = await client.options(
        "/api/v1/health",
        headers={
            "Origin": "http://attacker.example",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert response.status_code == 400
    assert response.headers.get("access-control-allow-origin") is None
