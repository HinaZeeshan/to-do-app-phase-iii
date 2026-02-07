"""
Task service layer with business logic and validation.
"""

from uuid import UUID
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from ..models.task import Task
from ..repositories.task_repository import TaskRepository
from ..schemas.task import TaskCreate, TaskUpdate


class TaskService:
    """Service for task business logic."""

    def __init__(self, db: AsyncSession):
        """
        Initialize service with database session.

        Args:
            db: Async SQLAlchemy session
        """
        self.repository = TaskRepository(db)

    async def list_tasks(self, user_id: UUID, authenticated_user_id: str) -> List[Task]:
        """
        List all tasks for a user with authentication validation.

        Args:
            user_id: UUID from URL path parameter
            authenticated_user_id: User ID from JWT token

        Returns:
            List of Task objects for the authenticated user

        Raises:
            HTTPException: 403 if user_id doesn't match JWT user_id
        """
        # Validate URL user_id matches JWT user_id (Zero Trust principle)
        if str(user_id) != authenticated_user_id:
            raise HTTPException(
                status_code=403,
                detail="Access forbidden: user_id does not match authenticated user"
            )

        # Retrieve tasks from repository
        tasks = await self.repository.list_tasks(user_id)
        return tasks

    async def create_task(
        self,
        user_id: UUID,
        task_data: TaskCreate,
        authenticated_user_id: str
    ) -> Task:
        """
        Create a new task with authentication validation.

        Args:
            user_id: UUID from URL path parameter
            task_data: TaskCreate schema with validated title
            authenticated_user_id: User ID from JWT token

        Returns:
            Newly created Task object

        Raises:
            HTTPException: 403 if user_id doesn't match JWT user_id
            HTTPException: 400 if title is empty after stripping
        """
        # Validate URL user_id matches JWT user_id (Zero Trust principle)
        if str(user_id) != authenticated_user_id:
            raise HTTPException(
                status_code=403,
                detail="Access forbidden: user_id does not match authenticated user"
            )

        # Additional validation: ensure title is not empty (already handled by Pydantic validator)
        if not task_data.title or not task_data.title.strip():
            raise HTTPException(
                status_code=400,
                detail="Title cannot be empty or whitespace only"
            )

        # Create task via repository
        task = await self.repository.create_task(user_id, task_data.title, task_data.description)
        return task

    async def complete_task(
        self,
        user_id: UUID,
        task_id: UUID,
        authenticated_user_id: str
    ) -> Task:
        """
        Mark a task as complete with authentication validation.

        Args:
            user_id: UUID from URL path parameter
            task_id: UUID of the task to mark complete
            authenticated_user_id: User ID from JWT token

        Returns:
            Updated Task object with is_completed=True

        Raises:
            HTTPException: 403 if user_id doesn't match JWT user_id
            HTTPException: 404 if task not found or doesn't belong to user
        """
        # Validate URL user_id matches JWT user_id (Zero Trust principle)
        if str(user_id) != authenticated_user_id:
            raise HTTPException(
                status_code=403,
                detail="Access forbidden: user_id does not match authenticated user"
            )

        # Retrieve task
        task = await self.repository.get_task_by_id(user_id, task_id)
        if not task:
            raise HTTPException(
                status_code=404,
                detail="Task not found"
            )

        # Idempotency: if already completed, return as-is without error
        if task.is_completed:
            return task

        # Mark as complete
        updated_task = await self.repository.complete_task(task)
        return updated_task

    async def get_task(
        self,
        user_id: UUID,
        task_id: UUID,
        authenticated_user_id: str
    ) -> Task:
        """
        Retrieve a specific task by ID with authentication validation.

        Args:
            user_id: UUID from URL path parameter
            task_id: UUID of the task to retrieve
            authenticated_user_id: User ID from JWT token

        Returns:
            Task object with all details

        Raises:
            HTTPException: 403 if user_id doesn't match JWT user_id
            HTTPException: 404 if task not found or doesn't belong to user
        """
        # Validate URL user_id matches JWT user_id (Zero Trust principle)
        if str(user_id) != authenticated_user_id:
            raise HTTPException(
                status_code=403,
                detail="Access forbidden: user_id does not match authenticated user"
            )

        # Retrieve task
        task = await self.repository.get_task_by_id(user_id, task_id)
        if not task:
            raise HTTPException(
                status_code=404,
                detail="Task not found"
            )

        return task

    async def update_task(
        self,
        user_id: UUID,
        task_id: UUID,
        task_data: TaskUpdate,
        authenticated_user_id: str
    ) -> Task:
        """
        Update task details with authentication validation.

        Args:
            user_id: UUID from URL path parameter
            task_id: UUID of the task to update
            task_data: TaskUpdate schema with optional title and is_completed
            authenticated_user_id: User ID from JWT token

        Returns:
            Updated Task object

        Raises:
            HTTPException: 403 if user_id doesn't match JWT user_id
            HTTPException: 404 if task not found or doesn't belong to user
            HTTPException: 400 if title is provided but empty
        """
        # Validate URL user_id matches JWT user_id (Zero Trust principle)
        if str(user_id) != authenticated_user_id:
            raise HTTPException(
                status_code=403,
                detail="Access forbidden: user_id does not match authenticated user"
            )

        # Retrieve task
        task = await self.repository.get_task_by_id(user_id, task_id)
        if not task:
            raise HTTPException(
                status_code=404,
                detail="Task not found"
            )

        # Validate title if provided (Pydantic validator already handles this)
        if task_data.title is not None and not task_data.title.strip():
            raise HTTPException(
                status_code=400,
                detail="Title cannot be empty or whitespace only"
            )

        # Update task via repository
        updated_task = await self.repository.update_task(
            task,
            title=task_data.title,
            description=task_data.description,
            is_completed=task_data.is_completed
        )
        return updated_task

    async def delete_task(
        self,
        user_id: UUID,
        task_id: UUID,
        authenticated_user_id: str
    ) -> None:
        """
        Delete a task with authentication validation.

        Args:
            user_id: UUID from URL path parameter
            task_id: UUID of the task to delete
            authenticated_user_id: User ID from JWT token

        Returns:
            None

        Raises:
            HTTPException: 403 if user_id doesn't match JWT user_id
            HTTPException: 404 if task not found or doesn't belong to user
        """
        # Validate URL user_id matches JWT user_id (Zero Trust principle)
        if str(user_id) != authenticated_user_id:
            raise HTTPException(
                status_code=403,
                detail="Access forbidden: user_id does not match authenticated user"
            )

        # Retrieve task
        task = await self.repository.get_task_by_id(user_id, task_id)
        if not task:
            raise HTTPException(
                status_code=404,
                detail="Task not found"
            )

        # Delete task via repository
        await self.repository.delete_task(task)
