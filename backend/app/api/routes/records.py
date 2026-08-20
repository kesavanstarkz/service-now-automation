from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.records import IncidentRecord
from app.schemas.auth import UserProfile
from app.auth.jwt import get_current_user
from app.auth.rbac import require_roles
from app.servicenow.client import ServiceNowClient
from app.database.connection import get_db
from app.services.audit_service import AuditService

router = APIRouter(prefix="/api/v1/records", tags=["Records"])


@router.get("/{record_type}/{record_id}", response_model=IncidentRecord)
async def get_record(
    record_type: str,
    record_id: str,
    user: UserProfile = Depends(require_roles(["AI_USER"])),
    db: AsyncSession = Depends(get_db)
):
    """
    Fetches authoritative record data from ServiceNow Table API.
    """
    if record_type.lower() != "incident":
        raise HTTPException(status_code=400, detail=f"Unsupported record type: {record_type}. DEV phase targets 'incident'.")

    sn_client = ServiceNowClient()
    record = await sn_client.get_incident(record_id)

    await AuditService.log_audit_event(
        db, user_id=user.user_id, event_type="RECORD_FETCH", resource=f"{record_type}:{record_id}"
    )

    return record
