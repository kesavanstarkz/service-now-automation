from typing import List, Callable
from fastapi import Depends, HTTPException, status
from app.schemas.auth import UserProfile
from app.auth.jwt import get_current_user


def require_roles(allowed_roles: List[str]) -> Callable:
    """
    Enforces Role-Based Access Control (RBAC).
    """
    async def role_checker(user: UserProfile = Depends(get_current_user)) -> UserProfile:
        has_role = any(role in user.roles for role in allowed_roles)
        if not has_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"User lacks required role. Allowed roles: {allowed_roles}"
            )
        return user

    return role_checker
