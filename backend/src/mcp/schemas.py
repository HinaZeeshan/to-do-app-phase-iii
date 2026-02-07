"""
MCP Tool Input Validation Schemas

Pydantic models for validating MCP tool inputs.
"""

from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional


class AddTaskInput(BaseModel):
    """Input validation for add_task tool."""

    user_id: UUID = Field(..., description="Authenticated user ID")
    title: str = Field(..., min_length=1, max_length=500, description="Task title")


class ListTasksInput(BaseModel):
    """Input validation for list_tasks tool."""

    user_id: UUID = Field(..., description="Authenticated user ID")
    filter: str = Field(
        "all",
        pattern="^(all|pending|completed)$",
        description="Task filter: all, pending, or completed",
    )


class CompleteTaskInput(BaseModel):
    """Input validation for complete_task tool."""

    user_id: UUID = Field(..., description="Authenticated user ID (must own task)")
    task_id: UUID = Field(..., description="Task ID to complete")


class DeleteTaskInput(BaseModel):
    """Input validation for delete_task tool."""

    user_id: UUID = Field(..., description="Authenticated user ID (must own task)")
    task_id: UUID = Field(..., description="Task ID to delete")


class UpdateTaskInput(BaseModel):
    """Input validation for update_task tool."""

    user_id: UUID = Field(..., description="Authenticated user ID (must own task)")
    task_id: UUID = Field(..., description="Task ID to update")
    new_title: str = Field(
        ..., min_length=1, max_length=500, description="New task title"
    )
