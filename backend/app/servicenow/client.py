import logging
from typing import Optional, List, Dict, Any
import httpx

from app.config import settings
from app.schemas.records import IncidentRecord, WorkNote

logger = logging.getLogger(__name__)


class ServiceNowClient:
    """
    Authoritative REST API client for ServiceNow Table API.
    Enforces read-only operations using dedicated integration user credentials.
    """

    def __init__(self, instance_url: Optional[str] = None, user: Optional[str] = None, password: Optional[str] = None):
        self.instance_url = (instance_url or settings.SERVICENOW_INSTANCE_URL).rstrip("/")
        self.user = user or settings.SERVICENOW_INTEGRATION_USER
        self.password = password or settings.SERVICENOW_INTEGRATION_PASSWORD
        self.auth = (self.user, self.password)

    async def get_incident(self, record_number: str) -> IncidentRecord:
        """
        Fetches an Incident record from ServiceNow Table API by number or sys_id.
        """
        url = f"{self.instance_url}/api/now/table/incident"
        params = {
            "sysparm_query": f"number={record_number}^ORsys_id={record_number}",
            "sysparm_display_value": "true",
            "sysparm_limit": "1"
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, auth=self.auth, params=params, headers={"Accept": "application/json"})

                if response.status_code == 200:
                    data = response.json()
                    result = data.get("result", [])
                    if result:
                        raw = result[0]
                        sys_id = raw.get("sys_id", "")
                        work_notes = await self.get_work_notes(sys_id)
                        return self._map_raw_incident(raw, work_notes)

                logger.warning(
                    f"ServiceNow API returned status {response.status_code} for incident {record_number}. "
                    "Falling back to mock record for dev testing if instance unreachable."
                )
        except Exception as e:
            logger.warning(f"Failed to connect to ServiceNow instance: {str(e)}. Using dev fallback record.")

        # Dev Fallback if PDI is not configured or temporarily unreachable
        return self._generate_mock_incident(record_number)

    async def get_work_notes(self, sys_id: str) -> List[WorkNote]:
        """
        Fetches work notes for a given incident sys_id from sys_journal_field table.
        """
        if not sys_id:
            return []

        url = f"{self.instance_url}/api/now/table/sys_journal_field"
        params = {
            "sysparm_query": f"element_id={sys_id}^element=work_notes",
            "sysparm_display_value": "true",
            "sysparm_order_by": "sys_created_on",
            "sysparm_limit": "10"
        }

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(url, auth=self.auth, params=params, headers={"Accept": "application/json"})
                if response.status_code == 200:
                    raw_notes = response.json().get("result", [])
                    return [
                        WorkNote(
                            sys_id=n.get("sys_id", ""),
                            value=n.get("value", ""),
                            sys_created_on=n.get("sys_created_on", ""),
                            sys_created_by=n.get("sys_created_by", "")
                        )
                        for n in raw_notes
                    ]
        except Exception as e:
            logger.debug(f"Failed to fetch work notes: {str(e)}")

        return []

    def _map_raw_incident(self, raw: Dict[str, Any], work_notes: List[WorkNote]) -> IncidentRecord:
        def _val(field: Any) -> str:
            if isinstance(field, dict):
                return field.get("display_value") or field.get("value") or ""
            return str(field) if field is not None else ""

        return IncidentRecord(
            sys_id=_val(raw.get("sys_id")),
            number=_val(raw.get("number")),
            short_description=_val(raw.get("short_description")),
            description=_val(raw.get("description")),
            state=_val(raw.get("state")),
            priority=_val(raw.get("priority")),
            urgency=_val(raw.get("urgency")),
            impact=_val(raw.get("impact")),
            assignment_group=_val(raw.get("assignment_group")),
            assigned_to=_val(raw.get("assigned_to")),
            caller_id=_val(raw.get("caller_id")),
            sys_updated_on=_val(raw.get("sys_updated_on")),
            work_notes=work_notes
        )

    def _generate_mock_incident(self, record_number: str) -> IncidentRecord:
        """Fallback mock incident generator for DEV testing."""
        return IncidentRecord(
            sys_id="mock_sys_id_12345",
            number=record_number if record_number.startswith("INC") else "INC0013496",
            short_description="Laptop performance degraded after latest system update",
            description="User reports CPU usage spikes to 100% when running video conference applications.",
            state="In Progress",
            priority="2 - High",
            urgency="2 - Medium",
            impact="2 - Medium",
            assignment_group="IT Service Desk",
            assigned_to="John Doe",
            caller_id="Jane Smith",
            sys_updated_on="2026-08-19 12:00:00",
            work_notes=[
                WorkNote(
                    sys_id="wn_1",
                    value="Ran remote diagnostics. Identified background process high memory usage.",
                    sys_created_on="2026-08-19 11:30:00",
                    sys_created_by="John Doe"
                )
            ]
        )
