"""
MCP Tool: list_tasks

Retrieves task list for a user with filtering via TaskService.
"""

from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from typing import List

from ...services.task_service import TaskService
from ..errors import ValidationError, DatabaseError
from ..schemas import ListTasksInput


async def list_tasks(
    user_id: UUID, filter: str, db: AsyncSession
) -> List[dict]:
    """
    Retrieve filtered task list for the authenticated user.

    Args:
        user_id: Authenticated user ID
        filter: Filter type ("all", "pending", or "completed")
        db: Database session

    Returns:
        List[dict]: List of task objects sorted by created_at descending

    Raises:
        ValidationError: If inputs are invalid
        DatabaseError: If database operation fails
    """
    try:
        # Validate inputs
        input_data = ListTasksInput(user_id=user_id, filter=filter)

        # Create TaskService
        service = TaskService(db)

        # Retrieve all tasks for user
        tasks = await service.list_tasks(
            user_id=input_data.user_id,
            authenticated_user_id=str(input_data.user_id),
        )

        # Apply filter
        if input_data.filter == "pending":
            tasks = [task for task in tasks if not task.is_completed]
        elif input_data.filter == "completed":
            tasks = [task for task in tasks if task.is_completed]
        # "all" requires no filtering

        # Sort by created_at descending (newest first)
        tasks.sort(key=lambda task: task.created_at, reverse=True)

        # Return serialized tasks
        return [task.model_dump() for task in tasks]

    except ValueError as e:
        # Pydantic validation error
        raise ValidationError(str(e))

    except HTTPException as e:
        # Convert TaskService errors to MCP errors
        if e.status_code == 403:
            raise ValidationError(e.detail)
        else:
            raise DatabaseError(f"Database operation failed: {e.detail}")

    except Exception as e:
        # Unexpected database or system error
        raise DatabaseError(f"Unexpected error: {str(e)}")
