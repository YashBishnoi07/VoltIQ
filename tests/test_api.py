import pytest
from httpx import AsyncClient, ASGITransport
from api.main import app


@pytest.mark.asyncio
async def test_health_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/health")
        assert res.status_code == 200
        assert res.json()["status"] == "healthy"


@pytest.mark.asyncio
async def test_stations_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/stations")
        assert res.status_code == 200
        data = res.json()
        assert "stations" in data
        assert "total" in data


@pytest.mark.asyncio
async def test_predict_utilization():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.post("/predict/utilization", json={
            "station_type": "DC_Fast",
            "location_type": "urban",
            "power_kw": 120.0,
            "num_ports": 6,
            "mean_sessions": 3.0,
            "std_sessions": 1.0,
            "mean_energy": 45.0,
            "mean_utilization": 0.6,
        })
        assert res.status_code == 200
        body = res.json()
        assert body["predicted_class"] in ["Low", "Medium", "High"]
        assert "confidence" in body
        assert "ethics_notice" in body
