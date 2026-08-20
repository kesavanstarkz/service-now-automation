import logging
from typing import Optional, Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import AIRequestLog, AuditEvent
from app.schemas.ai import AIResponse

logger = logging.getLogger(__name__)


class AuditService:
    @staticmethod
    async def log_ai_request(
        db: AsyncSession,
        user_id: str,
        mode: str,
        action: str,
        resp: AIResponse,
        record_type: Optional[str] = None
    ) -> None:
        try:
            log_entry = AIRequestLog(
                user_id=user_id,
                mode=mode,
                action=action,
                record_type=record_type,
                record_number=resp.record_number,
                prompt_version=resp.prompt_version,
                model_name=resp.model_used,
                status="success",
                guardrails_triggered=[n.model_dump() for n in resp.guardrail_notices]
            )
            db.add(log_entry)
            await db.flush()
        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to log AI request audit record: {str(e)}")

    @staticmethod
    async def log_audit_event(
        db: AsyncSession,
        user_id: str,
        event_type: str,
        resource: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        try:
            event = AuditEvent(
                user_id=user_id,
                event_type=event_type,
                resource=resource,
                details_json=details or {}
            )
            db.add(event)
            await db.flush()
        except Exception as e:
            logger.error(f"Failed to log audit event: {str(e)}")
