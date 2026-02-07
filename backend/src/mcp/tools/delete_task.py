"""
MCP Tool: delete_task

Deletes a task via TaskService.
"""

from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from typing import Optional

from ...services.task_service import TaskService
from ..errors import TaskNotFoundError, ValidationError, UnauthorizedError, DatabaseError
from ..schemas import DeleteTaskInput


async def delete_task(user_id: UUID, task_id: UUID, db: AsyncSession) -> None:
    """
    Delete a task for the authenticated user.

    Args:
        user_id: Authenticated user ID (must own task)
        task_id: Task ID to delete
        db: Database session

    Returns:
        None (success)

    Raises:
        ValidationError: If inputs are invalid
        TaskNotFoundError: If task doesn't exist
        UnauthorizedError: If user doesn't own task
        DatabaseError: If database operation fails
    """
    try:
        # Validate inputs
        input_data = DeleteTaskInput(user_id=user_id, task_id=task_id)

        # Create TaskService
        service = TaskService(db)

        # Delete task (TaskService handles authorization)
        await service.delete_task(
            user_id=input_data.user_id,
            task_id=input_data.task_id,
            authenticated_user_id=str(input_data.user_id),
        )

        # Return None on success
        return None

    except ValueError as e:
        # Pydantic validation error
        raise ValidationError(str(e))

    except HTTPException as e:
        # Convert TaskService errors to MCP errors
        if e.status_code == 404:
            raise TaskNotFoundError(e.detail)
        elif e.status_code == 403:
            raise UnauthorizedError(e.detail)
        elif e.status_code == 400:
            raise ValidationError(e.detail)
        else:
            raise DatabaseError(f"Database operation failed: {e.detail}")

    except Exception as e:
        # Unexpected database or system error
        raise DatabaseError(f"Unexpected error: {str(e)}")
