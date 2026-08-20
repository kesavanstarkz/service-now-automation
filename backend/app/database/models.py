from datetime import datetime, timezone
import uuid
from sqlalchemy import Column, String, DateTime, Text, Integer, JSON
from app.database.connection import Base


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False)
    role = Column(String(50), nullable=False, default="AI_USER")
    preferences_json = Column(JSON, nullable=True, default=dict)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class AIRequestLog(Base):
    __tablename__ = "ai_request_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(100), nullable=False, index=True)
    mode = Column(String(50), nullable=False)  # record | dashboard
    action = Column(String(100), nullable=False)  # generate_customer_response | summarize_incident | etc.
    record_type = Column(String(50), nullable=True)
    record_number = Column(String(50), nullable=True)
    prompt_version = Column(String(20), nullable=False)
    model_name = Column(String(100), nullable=False)
    status = Column(String(20), nullable=False, default="success")
    guardrails_triggered = Column(JSON, nullable=True, default=list)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(100), nullable=False, index=True)
    event_type = Column(String(100), nullable=False)  # RECORD_FETCH | AI_GENERATE | AUTH_LOGIN
    resource = Column(String(255), nullable=True)
    details_json = Column(JSON, nullable=True, default=dict)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
