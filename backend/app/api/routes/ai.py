from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.ai import RecordAIRequest, DashboardAIRequest, AIResponse
from app.schemas.auth import UserProfile
from app.auth.rbac import require_roles
from app.ai.orchestrator import AIOrchestrator
from app.database.connection import get_db
from app.services.audit_service import AuditService

router = APIRouter(prefix="/api/v1/ai", tags=["AI Operations"])
orchestrator = AIOrchestrator()


@router.post("/generate", response_model=AIResponse)
async def generate_response(
    req: RecordAIRequest,
    user: UserProfile = Depends(require_roles(["AI_USER"])),
    db: AsyncSession = Depends(get_db)
):
    """Generates customer-facing response for an incident."""
    req.action = "generate_customer_response"
    resp = await orchestrator.process_record_request(req)
    await AuditService.log_ai_request(db, user.user_id, mode="record", action=req.action, resp=resp, record_type=req.record_type)
    return resp


@router.post("/summarize", response_model=AIResponse)
async def summarize_incident(
    req: RecordAIRequest,
    user: UserProfile = Depends(require_roles(["AI_USER"])),
    db: AsyncSession = Depends(get_db)
):
    """Summarizes incident details and work notes."""
    req.action = "summarize_incident"
    resp = await orchestrator.process_record_request(req)
    await AuditService.log_ai_request(db, user.user_id, mode="record", action=req.action, resp=resp, record_type=req.record_type)
    return resp


@router.post("/improve", response_model=AIResponse)
async def improve_text(
    req: RecordAIRequest,
    user: UserProfile = Depends(require_roles(["AI_USER"])),
    db: AsyncSession = Depends(get_db)
):
    """Improves and professionalizes draft customer response."""
    req.action = "improve_text"
    resp = await orchestrator.process_record_request(req)
    await AuditService.log_ai_request(db, user.user_id, mode="record", action=req.action, resp=resp, record_type=req.record_type)
    return resp


@router.post("/dashboard-summary", response_model=AIResponse)
async def summarize_dashboard(
    req: DashboardAIRequest,
    user: UserProfile = Depends(require_roles(["AI_USER"])),
    db: AsyncSession = Depends(get_db)
):
    """Summarizes ServiceNow Workspace/Dashboard bounded widget snapshot."""
    req.action = "summarize_queue"
    resp = await orchestrator.process_dashboard_request(req)
    await AuditService.log_ai_request(db, user.user_id, mode="dashboard", action=req.action, resp=resp)
    return resp
