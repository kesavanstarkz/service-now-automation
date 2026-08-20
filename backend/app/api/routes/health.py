from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.config import settings
from app.database.connection import get_db

router = APIRouter(prefix="/api/v1", tags=["Health"])


@router.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    """
    Health check verifying backend status, config, and SQLite connectivity.
    """
    db_status = "healthy"
    try:
        await db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    return {
        "status": "ok",
        "env": settings.ENV,
        "auth_mode": settings.AUTH_MODE,
        "llm_provider": settings.LLM_PROVIDER,
        "database": db_status,
        "servicenow_instance": settings.SERVICENOW_INSTANCE_URL
    }
