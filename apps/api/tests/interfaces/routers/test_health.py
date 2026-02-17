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
