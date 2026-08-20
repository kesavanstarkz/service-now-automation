from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class RecordAIRequest(BaseModel):
    mode: str = Field("record", pattern="^record$")
    record_type: str = Field("incident", description="Record type (e.g. incident)")
    record_number: str = Field(..., description="ServiceNow record number, e.g. INC0012345")
    action: str = Field(..., description="Action to perform: generate_customer_response | summarize_incident | improve_text")
    custom_instructions: Optional[str] = Field(None, description="Optional human instructions / user prompt tweak")
    text_to_improve: Optional[str] = Field(None, description="Text input for improve_text action")


class DashboardWidget(BaseModel):
    title: str
    value: Any


class VisibleRow(BaseModel):
    number: Optional[str] = None
    shortDescription: Optional[str] = None
    state: Optional[str] = None
    priority: Optional[str] = None


class DashboardAIRequest(BaseModel):
    mode: str = Field("dashboard", pattern="^dashboard$")
    widgets: List[DashboardWidget] = Field(default_factory=list)
    visibleRows: List[VisibleRow] = Field(default_factory=list)
    action: str = Field("summarize_queue", description="Dashboard action, default: summarize_queue")
    custom_instructions: Optional[str] = None


class GuardrailNotice(BaseModel):
    code: str
    message: str
    severity: str = "warning"  # warning | info


class AIResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    mode: str
    action: str
    content: str
    prompt_version: str
    model_used: str
    guardrail_notices: List[GuardrailNotice] = Field(default_factory=list)
    record_number: Optional[str] = None
