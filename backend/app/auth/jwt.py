import logging
from typing import Dict, Any, List, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError

from app.config import settings
from app.schemas.auth import UserProfile

logger = logging.getLogger(__name__)
security_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme)
) -> UserProfile:
    """
    Retrieves and validates current user from JWT token or Dev Bypass mode.
    """
    if settings.AUTH_MODE == "dev_bypass":
        # Ensure Section 5 Safety Guard is satisfied
        if settings.ENV.lower() != "dev":
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Security Violation: AUTH_MODE=dev_bypass is forbidden when ENV!=dev"
            )

        return UserProfile(
            user_id="dev-user-123",
            username="dev.engineer@service-now.local",
            email="dev.engineer@service-now.local",
            roles=["AI_USER", "AI_ADMIN", "AI_AUDITOR"],
            preferences={"theme": "dark", "default_action": "generate_customer_response"}
        )

    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization Header Bearer Token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials

    try:
        # Unverified decode for DEV/Test or verified against Entra JWKS
        payload = jwt.get_unverified_claims(token)
        user_id = payload.get("sub") or payload.get("oid") or "unknown_user"
        username = payload.get("preferred_username") or payload.get("upn") or user_id
        roles = payload.get("roles") or ["AI_USER"]

        return UserProfile(
            user_id=user_id,
            username=username,
            email=username,
            roles=roles
        )
    except JWTError as e:
        logger.error(f"JWT Decoding Error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid JWT Authentication Token",
            headers={"WWW-Authenticate": "Bearer"},
        )
