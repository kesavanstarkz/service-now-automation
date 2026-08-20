from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.schemas.auth import UserProfile, UserPreferencesUpdate
from app.auth.jwt import get_current_user
from app.database.connection import get_db
from app.database.models import User

router = APIRouter(prefix="/api/v1/user", tags=["User Profile"])


@router.get("/profile", response_model=UserProfile)
async def get_profile(user: UserProfile = Depends(get_current_user)):
    return user


@router.get("/preferences")
async def get_preferences(user: UserProfile = Depends(get_current_user)):
    return {"preferences": user.preferences}


@router.put("/preferences")
async def update_preferences(
    body: UserPreferencesUpdate,
    user: UserProfile = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(User).where(User.username == user.username)
    res = await db.execute(stmt)
    db_user = res.scalar_one_or_none()

    if not db_user:
        db_user = User(
            id=user.user_id,
            username=user.username,
            email=user.email,
            role=user.roles[0] if user.roles else "AI_USER",
            preferences_json=body.preferences
        )
        db.add(db_user)
    else:
        db_user.preferences_json = body.preferences

    await db.flush()
    return {"status": "updated", "preferences": body.preferences}
