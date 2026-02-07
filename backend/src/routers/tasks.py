"""
Task API endpoints.
"""

from uuid import UUID
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from ..database import get_db
from ..auth.dependencies import get_current_user_id
from ..services.task_service import TaskService
from ..schemas.task import TaskListResponse, TaskResponse, TaskCreate, TaskUpdate


router = APIRouter(prefix="/api", tags=["tasks"])


@router.get("/{user_id}/tasks", response_model=TaskListResponse)
async def list_tasks(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    authenticated_user_id: str = Depends(get_current_user_id)
):
    """
    Retrieve all tasks for the authenticated user.

    Args:
        user_id: User ID from URL path (must match JWT user_id)
        db: Database session dependency
        authenticated_user_id: User ID extracted from JWT token

    Returns:
        TaskListResponse with list of tasks and metadata

    Raises:
        HTTPException 401: Invalid or missing JWT token
        HTTPException 403: URL user_id doesn't match JWT user_id
    """
    service = TaskService(db)
    tasks = await service.list_tasks(user_id, authenticated_user_id)

    # Convert to response models
    task_responses = [TaskResponse.model_validate(task) for task in tasks]

    # Build response with metadata
    response = TaskListResponse(
        data=task_responses,
        meta={
            "timestamp": datetime.utcnow().isoformat(),
            "count": len(task_responses)
        }
    )

    return response


@router.post(
    "/{user_id}/tasks",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_task(
    user_id: UUID,
    task_data: TaskCreate,
    db: AsyncSession = Depends(get_db),
    authenticated_user_id: str = Depends(get_current_user_id)
):
    """
    Create a new task for the authenticated user.

    Args:
        user_id: User ID from URL path (must match JWT user_id)
        task_data: TaskCreate schema with title
        db: Database session dependency
        authenticated_user_id: User ID extracted from JWT token

    Returns:
        TaskResponse with newly created task details

    Raises:
        HTTPException 400: Invalid task data (empty title)
        HTTPException 401: Invalid or missing JWT token
        HTTPException 403: URL user_id doesn't match JWT user_id
    """
    service = TaskService(db)
    task = await service.create_task(user_id, task_data, authenticated_user_id)

    # Convert to response model
    return TaskResponse.model_validate(task)


@router.patch("/{user_id}/tasks/{id}/complete", response_model=TaskResponse)
async def complete_task(
    user_id: UUID,
    id: UUID,
    db: AsyncSession = Depends(get_db),
    authenticated_user_id: str = Depends(get_current_user_id)
):
    """
    Mark a task as complete for the authenticated user.

    Args:
        user_id: User ID from URL path (must match JWT user_id)
        id: Task ID to mark complete
        db: Database session dependency
        authenticated_user_id: User ID extracted from JWT token

    Returns:
        TaskResponse with updated task details (is_completed=True, completed_at timestamp)

    Raises:
        HTTPException 401: Invalid or missing JWT token
        HTTPException 403: URL user_id doesn't match JWT user_id
        HTTPException 404: Task not found or doesn't belong to user

    Notes:
        - Idempotent: marking an already-completed task returns success
        - Sets both is_completed=True and completed_at=current_timestamp
    """
    service = TaskService(db)
    task = await service.complete_task(user_id, id, authenticated_user_id)

    # Convert to response model
    return TaskResponse.model_validate(task)


@router.get("/{user_id}/tasks/{id}", response_model=TaskResponse)
async def get_task(
    user_id: UUID,
    id: UUID,
    db: AsyncSession = Depends(get_db),
    authenticated_user_id: str = Depends(get_current_user_id)
):
    """
    Retrieve a specific task by ID for the authenticated user.

    Args:
        user_id: User ID from URL path (must match JWT user_id)
        id: Task ID to retrieve
        db: Database session dependency
        authenticated_user_id: User ID extracted from JWT token

    Returns:
        TaskResponse with complete task details

    Raises:
        HTTPException 401: Invalid or missing JWT token
        HTTPException 403: URL user_id doesn't match JWT user_id
        HTTPException 404: Task not found or doesn't belong to user
    """
    service = TaskService(db)
    task = await service.get_task(user_id, id, authenticated_user_id)

    # Convert to response model
    return TaskResponse.model_validate(task)


@router.put("/{user_id}/tasks/{id}", response_model=TaskResponse)
async def update_task(
    user_id: UUID,
    id: UUID,
    task_data: TaskUpdate,
    db: AsyncSession = Depends(get_db),
    authenticated_user_id: str = Depends(get_current_user_id)
):
    """
    Update task details (title and/or completion status) for the authenticated user.

    Args:
        user_id: User ID from URL path (must match JWT user_id)
        id: Task ID to update
        task_data: TaskUpdate schema with optional title and is_completed fields
        db: Database session dependency
        authenticated_user_id: User ID extracted from JWT token

    Returns:
        TaskResponse with updated task details

    Raises:
        HTTPException 400: Invalid task data (empty title)
        HTTPException 401: Invalid or missing JWT token
        HTTPException 403: URL user_id doesn't match JWT user_id
        HTTPException 404: Task not found or doesn't belong to user

    Notes:
        - Only provided fields are updated (partial update)
        - Changing is_completed to true sets completed_at timestamp
        - Changing is_completed to false clears completed_at timestamp
    """
    service = TaskService(db)
    task = await service.update_task(user_id, id, task_data, authenticated_user_id)

    # Convert to response model
    return TaskResponse.model_validate(task)


@router.delete(
    "/{user_id}/tasks/{id}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_task(
    user_id: UUID,
    id: UUID,
    db: AsyncSession = Depends(get_db),
    authenticated_user_id: str = Depends(get_current_user_id)
):
    """
    Delete a task for the authenticated user.

    Args:
        user_id: User ID from URL path (must match JWT user_id)
        id: Task ID to delete
        db: Database session dependency
        authenticated_user_id: User ID extracted from JWT token

    Returns:
        204 No Content on success

    Raises:
        HTTPException 401: Invalid or missing JWT token
        HTTPException 403: URL user_id doesn't match JWT user_id
        HTTPException 404: Task not found or doesn't belong to user
    """
    service = TaskService(db)
    await service.delete_task(user_id, id, authenticated_user_id)

    # Return 204 No Content (no body)
