from typing import List, Optional
from pydantic import BaseModel, Field


class WorkNote(BaseModel):
    sys_id: str
    value: str
    sys_created_on: Optional[str] = None
    sys_created_by: Optional[str] = None


class IncidentRecord(BaseModel):
    sys_id: str
    number: str
    short_description: Optional[str] = ""
    description: Optional[str] = ""
    state: Optional[str] = ""
    priority: Optional[str] = ""
    urgency: Optional[str] = ""
    impact: Optional[str] = ""
    assignment_group: Optional[str] = ""
    assigned_to: Optional[str] = ""
    caller_id: Optional[str] = ""
    sys_updated_on: Optional[str] = ""
    work_notes: List[WorkNote] = Field(default_factory=list)
