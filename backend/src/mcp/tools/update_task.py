"""
MCP Tool: update_task

Updates task title via TaskService.
"""

from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from ...services.task_service import TaskService
from ...schemas.task import TaskUpdate
from ..errors import TaskNotFoundError, ValidationError, UnauthorizedError, DatabaseError
from ..schemas import UpdateTaskInput


async def update_task(
    user_id: UUID, task_id: UUID, new_title: str, db: AsyncSession
) -> dict:
    """
    Update task title for the authenticated user.

    Args:
        user_id: Authenticated user ID (must own task)
        task_id: Task ID to update
        new_title: New task title (1-500 characters, non-empty)
        db: Database session

    Returns:
        dict: Updated task object with new title and refreshed updated_at timestamp

    Raises:
        ValidationError: If inputs are invalid
        TaskNotFoundError: If task doesn't exist
        UnauthorizedError: If user doesn't own task
        DatabaseError: If database operation fails
    """
    try:
        # Validate inputs
        input_data = UpdateTaskInput(
            user_id=user_id, task_id=task_id, new_title=new_title
        )

        # Create TaskService
        service = TaskService(db)

        # Create update data
        task_data = TaskUpdate(title=input_data.new_title)

        # Update task (TaskService handles authorization)
        task = await service.update_task(
            user_id=input_data.user_id,
            task_id=input_data.task_id,
            task_data=task_data,
            authenticated_user_id=str(input_data.user_id),
        )

        # Return serialized task
        return task.model_dump()

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
