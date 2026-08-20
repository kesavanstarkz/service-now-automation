from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class UserProfile(BaseModel):
    user_id: str
    username: str
    email: str
    roles: List[str] = Field(default_factory=lambda: ["AI_USER"])
    preferences: Dict[str, Any] = Field(default_factory=dict)


class UserPreferencesUpdate(BaseModel):
    preferences: Dict[str, Any]
