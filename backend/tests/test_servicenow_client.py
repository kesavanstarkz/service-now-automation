import pytest
from app.servicenow.client import ServiceNowClient


@pytest.mark.asyncio
async def test_servicenow_client_fallback():
    client = ServiceNowClient(instance_url="https://dev00000.service-now.com")
    record = await client.get_incident("INC0012345")
    assert record.number == "INC0012345"
    assert record.short_description != ""
    assert len(record.work_notes) >= 0
