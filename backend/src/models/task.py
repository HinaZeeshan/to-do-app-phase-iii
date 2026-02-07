"""
SQLModel Task entity for database.
Represents tasks table schema.
"""

from sqlmodel import Field, SQLModel
from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional


class Task(SQLModel, table=True):
    """
    Task model representing a user's task item.

    Attributes:
        id: Unique task identifier (UUID)
        user_id: Owner user identifier (foreign key)
        title: Task description (1-500 chars, non-empty)
        is_completed: Completion status (default False)
        completed_at: Timestamp when marked complete (null if incomplete)
        created_at: Creation timestamp
        updated_at: Last modification timestamp
    """

    __tablename__ = "tasks"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True, nullable=False)
    title: str = Field(max_length=500, nullable=False)
    description: Optional[str] = Field(default=None, max_length=1000, nullable=True)
    is_completed: bool = Field(default=False, nullable=False)
    completed_at: Optional[datetime] = Field(default=None, nullable=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    class Config:
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "title": "Buy groceries",
                "is_completed": False,
                "completed_at": None,
                "created_at": "2026-01-14T10:00:00Z",
                "updated_at": "2026-01-14T10:00:00Z",
            }
        }
