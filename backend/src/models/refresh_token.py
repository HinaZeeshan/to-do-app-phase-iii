"""
RefreshToken model for secure token rotation.
"""

from sqlmodel import Field, SQLModel
from datetime import datetime
from uuid import UUID, uuid4


class RefreshToken(SQLModel, table=True):
    """
    RefreshToken model for managing long-lived sessions.
    Tokens are hashed for security (similar to passwords).
    """
    __tablename__ = "refresh_tokens"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", nullable=False, index=True)
    token_hash: str = Field(max_length=255, nullable=False, index=True)
    expires_at: datetime = Field(nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
