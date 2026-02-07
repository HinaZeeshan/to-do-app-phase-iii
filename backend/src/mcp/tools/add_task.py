"""
MCP Tool: add_task

Creates a new task for a user via TaskService.
"""

from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from ...services.task_service import TaskService
from ...schemas.task import TaskCreate
from ..errors import ValidationError, DatabaseError
from ..schemas import AddTaskInput


async def add_task(user_id: UUID, title: str, db: AsyncSession) -> dict:
    """
    Create a new task for the authenticated user.

    Args:
        user_id: Authenticated user ID
        title: Task title (1-500 characters, non-empty)
        db: Database session

    Returns:
        dict: Task object with all fields

    Raises:
        ValidationError: If inputs are invalid
        DatabaseError: If database operation fails
    """
    try:
        # Validate inputs
        input_data = AddTaskInput(user_id=user_id, title=title)

        # Create TaskService
        service = TaskService(db)

        # Create task data
        task_data = TaskCreate(title=input_data.title)

        # Call TaskService (user_id is both parameter and authenticated_user_id)
        task = await service.create_task(
            user_id=input_data.user_id,
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
        if e.status_code == 400:
            raise ValidationError(e.detail)
        else:
            raise DatabaseError(f"Database operation failed: {e.detail}")

    except Exception as e:
        # Unexpected database or system error
        raise DatabaseError(f"Unexpected error: {str(e)}")
