"""
Pydantic schemas for Task API requests and responses.
"""

from pydantic import BaseModel, Field, validator
from datetime import datetime
from uuid import UUID
from typing import Optional


class TaskResponse(BaseModel):
    """Response schema for single task."""

    id: UUID
    user_id: UUID
    title: str
    description: Optional[str] = None
    is_completed: bool
    completed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # Allows conversion from SQLModel instances


class TaskListResponse(BaseModel):
    """Response schema for list of tasks."""

    data: list[TaskResponse]
    meta: dict = Field(
        default_factory=lambda: {
            "timestamp": datetime.utcnow().isoformat(),
            "count": 0,
        }
    )

    class Config:
        json_schema_extra = {
            "example": {
                "data": [
                    {
                        "id": "550e8400-e29b-41d4-a716-446655440000",
                        "user_id": "123e4567-e89b-12d3-a456-426614174000",
                        "title": "Buy groceries",
                        "is_completed": False,
                        "completed_at": None,
                        "created_at": "2026-01-14T10:00:00Z",
                        "updated_at": "2026-01-14T10:00:00Z",
                    }
                ],
                "meta": {"timestamp": "2026-01-14T12:00:00Z", "count": 1},
            }
        }


class TaskCreate(BaseModel):
    """Request schema for creating a new task."""

    title: str = Field(..., min_length=1, max_length=500, description="Task title")
    description: Optional[str] = Field(None, max_length=1000, description="Task description")

    @validator("title")
    def title_not_empty(cls, v):
        if not v.strip():
            raise ValueError("Title cannot be empty or whitespace only")
        return v.strip()


class TaskUpdate(BaseModel):
    """Request schema for updating an existing task."""

    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = Field(None, max_length=1000)
    is_completed: Optional[bool] = None

    @validator("title")
    def title_not_empty(cls, v):
        if v is not None and not v.strip():
            raise ValueError("Title cannot be empty or whitespace only")
        return v.strip() if v else v
