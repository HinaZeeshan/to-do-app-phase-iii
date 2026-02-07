"""
Authentication event log for security monitoring.
"""

from sqlmodel import Field, SQLModel, Enum
from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional
import enum


class EventType(str, enum.Enum):
    SIGNUP = "signup"
    LOGIN = "login"
    LOGOUT = "logout"
    LOGIN_FAILED = "login_failed"


class AuthenticationEvent(SQLModel, table=True):
    """Authentication event log for security monitoring."""
    __tablename__ = "auth_events"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: Optional[UUID] = Field(default=None, nullable=True, index=True)
    event_type: EventType = Field(nullable=False, index=True)
    ip_address: Optional[str] = Field(default=None, max_length=45)
    user_agent: Optional[str] = Field(default=None, max_length=500)
    success: bool = Field(nullable=False)
    failure_reason: Optional[str] = Field(default=None, max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False, index=True)