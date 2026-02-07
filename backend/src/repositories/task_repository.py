"""
Task repository for database operations.
"""

from uuid import UUID, uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from datetime import datetime

from ..models.task import Task


class TaskRepository:
    """Repository for task database operations."""

    def __init__(self, db: AsyncSession):
        """
        Initialize repository with database session.

        Args:
            db: Async SQLAlchemy session
        """
        self.db = db

    async def list_tasks(self, user_id: UUID) -> List[Task]:
        """
        Retrieve all tasks for a specific user, ordered by creation date descending.

        Args:
            user_id: UUID of the user whose tasks to retrieve

        Returns:
            List of Task objects ordered by created_at DESC
        """
        statement = (
            select(Task)
            .where(Task.user_id == user_id)
            .order_by(Task.created_at.desc())
        )
        result = await self.db.execute(statement)
        tasks = result.scalars().all()
        return list(tasks)

    async def create_task(self, user_id: UUID, title: str, description: str | None = None) -> Task:
        """
        Create a new task for a user.

        Args:
            user_id: UUID of the user creating the task
            title: Task title (already validated and stripped)
            description: Optional task description

        Returns:
            Newly created Task object
        """
        task = Task(
            id=uuid4(),
            user_id=user_id,
            title=title,
            description=description,
            is_completed=False,
            completed_at=None,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        self.db.add(task)
        await self.db.commit()
        await self.db.refresh(task)
        return task

    async def get_task_by_id(self, user_id: UUID, task_id: UUID) -> Task | None:
        """
        Retrieve a specific task by ID for a user.

        Args:
            user_id: UUID of the user who owns the task
            task_id: UUID of the task to retrieve

        Returns:
            Task object if found and belongs to user, None otherwise
        """
        statement = (
            select(Task)
            .where(Task.user_id == user_id)
            .where(Task.id == task_id)
        )
        result = await self.db.execute(statement)
        task = result.scalar_one_or_none()
        return task

    async def complete_task(self, task: Task) -> Task:
        """
        Mark a task as completed.

        Args:
            task: Task object to mark as complete

        Returns:
            Updated Task object with is_completed=True and completed_at timestamp
        """
        task.is_completed = True
        task.completed_at = datetime.utcnow()
        task.updated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(task)
        return task

    async def update_task(
        self,
        task: Task,
        title: str | None = None,
        description: str | None = None,
        is_completed: bool | None = None
    ) -> Task:
        """
        Update task fields (title and/or completion status).

        Args:
            task: Task object to update
            title: Optional new title (already validated and stripped)
            description: Optional new description
            is_completed: Optional completion status

        Returns:
            Updated Task object
        """
        if title is not None:
            task.title = title

        if description is not None:
            task.description = description

        if is_completed is not None:
            task.is_completed = is_completed
            # Set or clear completed_at based on completion status
            if is_completed:
                if task.completed_at is None:
                    task.completed_at = datetime.utcnow()
            else:
                task.completed_at = None

        task.updated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(task)
        return task

    async def delete_task(self, task: Task) -> None:
        """
        Delete a task from the database.

        Args:
            task: Task object to delete

        Returns:
            None
        """
        await self.db.delete(task)
        await self.db.commit()
