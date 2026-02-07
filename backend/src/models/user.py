"""
User model representing an authenticated account.
Password hashing managed by Better Auth; this is schema definition only.
"""

from sqlmodel import Field, SQLModel
from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional


class User(SQLModel, table=True):
    """
    User model representing an authenticated account.
    Password hashing managed by Better Auth; this is schema definition only.
    """
    __tablename__ = "users"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(max_length=255, nullable=False, unique=True, index=True)
    password_hash: str = Field(max_length=255, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    last_login: Optional[datetime] = Field(default=None, nullable=True)
    is_active: bool = Field(default=True, nullable=False)