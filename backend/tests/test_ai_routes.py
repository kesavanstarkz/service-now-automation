import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_health_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"


@pytest.mark.asyncio
async def test_generate_ai_response_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        payload = {
            "mode": "record",
            "record_type": "incident",
            "record_number": "INC0013496",
            "action": "generate_customer_response"
        }
        response = await ac.post("/api/v1/ai/generate", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["mode"] == "record"
        assert "content" in data


@pytest.mark.asyncio
async def test_dashboard_summary_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        payload = {
            "mode": "dashboard",
            "widgets": [{"title": "Incidents assigned to you", "value": 5}],
            "visibleRows": [{"number": "INC0012345", "shortDescription": "VPN drop"}],
            "action": "summarize_queue"
        }
        response = await ac.post("/api/v1/ai/dashboard-summary", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["mode"] == "dashboard"
