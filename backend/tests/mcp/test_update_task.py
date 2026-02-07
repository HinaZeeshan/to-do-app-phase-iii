"""
Tests for update_task MCP tool.

Validates US5 scenarios:
1. User owns task → title updated and returned
2. Empty new_title → ValidationError
3. task_id doesn't exist → TaskNotFoundError
4. User A tries to update user B's task → UnauthorizedError
5. Invalid task_id format → ValidationError
"""

import pytest
from uuid import uuid4, UUID
from unittest.mock import AsyncMock, Mock, patch
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from fastapi import HTTPException

from src.mcp.tools.update_task import update_task
from src.mcp.errors import TaskNotFoundError, ValidationError, UnauthorizedError, DatabaseError
from src.models.task import Task


@pytest.mark.asyncio
async def test_update_task_success():
    """
    US5 Scenario 1: User owns task → title updated and returned.
    """
    # Arrange
    user_id = uuid4()
    task_id = uuid4()
    new_title = "buy almond milk"
    mock_db = AsyncMock(spec=AsyncSession)

    # Mock updated task
    mock_task = Mock(spec=Task)
    mock_task.id = task_id
    mock_task.user_id = user_id
    mock_task.title = new_title
    mock_task.description = None
    mock_task.is_completed = False
    mock_task.completed_at = None
    mock_task.created_at = datetime.utcnow()
    mock_task.updated_at = datetime.utcnow()
    mock_task.model_dump.return_value = {
        "id": str(mock_task.id),
        "user_id": str(mock_task.user_id),
        "title": mock_task.title,
        "description": None,
        "is_completed": False,
        "completed_at": None,
        "created_at": mock_task.created_at.isoformat(),
        "updated_at": mock_task.updated_at.isoformat(),
    }

    # Mock TaskService.update_task
    with patch("src.mcp.tools.update_task.TaskService") as MockService:
        mock_service = MockService.return_value
        mock_service.update_task = AsyncMock(return_value=mock_task)

        # Act
        result = await update_task(user_id, task_id, new_title, mock_db)

        # Assert
        assert result["title"] == new_title
        assert result["id"] == str(task_id)
        assert result["updated_at"] is not None
        mock_service.update_task.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_task_empty_title():
    """
    US5 Scenario 2: Empty new_title → ValidationError.
    """
    # Arrange
    user_id = uuid4()
    task_id = uuid4()
    empty_title = ""
    mock_db = AsyncMock(spec=AsyncSession)

    # Act & Assert
    with pytest.raises(ValidationError):
        await update_task(user_id, task_id, empty_title, mock_db)


@pytest.mark.asyncio
async def test_update_task_not_found():
    """
    US5 Scenario 3: task_id doesn't exist → TaskNotFoundError.
    """
    # Arrange
    user_id = uuid4()
    task_id = uuid4()
    new_title = "new title"
    mock_db = AsyncMock(spec=AsyncSession)

    # Mock TaskService to raise 404
    with patch("src.mcp.tools.update_task.TaskService") as MockService:
        mock_service = MockService.return_value
        mock_service.update_task = AsyncMock(
            side_effect=HTTPException(status_code=404, detail="Task not found")
        )

        # Act & Assert
        with pytest.raises(TaskNotFoundError, match="Task not found"):
            await update_task(user_id, task_id, new_title, mock_db)


@pytest.mark.asyncio
async def test_update_task_unauthorized():
    """
    US5 Scenario 4: User A tries to update user B's task → UnauthorizedError.
    """
    # Arrange
    user_a_id = uuid4()
    user_b_id = uuid4()
    task_id = uuid4()
    new_title = "new title"
    mock_db = AsyncMock(spec=AsyncSession)

    # Mock TaskService to raise 403 (task exists but user doesn't own it)
    with patch("src.mcp.tools.update_task.TaskService") as MockService:
        mock_service = MockService.return_value
        mock_service.update_task = AsyncMock(
            side_effect=HTTPException(
                status_code=403,
                detail="Access forbidden: user_id does not match authenticated user",
            )
        )

        # Act & Assert
        with pytest.raises(UnauthorizedError):
            await update_task(user_a_id, task_id, new_title, mock_db)


@pytest.mark.asyncio
async def test_update_task_invalid_task_id():
    """
    US5 Scenario 5: Invalid task_id format → ValidationError.
    """
    # Arrange
    user_id = uuid4()
    invalid_task_id = "not-a-uuid"
    new_title = "new title"
    mock_db = AsyncMock(spec=AsyncSession)

    # Act & Assert
    with pytest.raises((ValidationError, ValueError, TypeError)):
        await update_task(user_id, invalid_task_id, new_title, mock_db)  # type: ignore


@pytest.mark.asyncio
async def test_update_task_title_too_long():
    """
    Edge case: Title exceeds 500 characters → ValidationError.
    """
    # Arrange
    user_id = uuid4()
    task_id = uuid4()
    long_title = "a" * 501
    mock_db = AsyncMock(spec=AsyncSession)

    # Act & Assert
    with pytest.raises(ValidationError):
        await update_task(user_id, task_id, long_title, mock_db)


@pytest.mark.asyncio
async def test_update_task_database_error():
    """
    Edge case: Database error → DatabaseError.
    """
    # Arrange
    user_id = uuid4()
    task_id = uuid4()
    new_title = "new title"
    mock_db = AsyncMock(spec=AsyncSession)

    # Mock TaskService to raise database error
    with patch("src.mcp.tools.update_task.TaskService") as MockService:
        mock_service = MockService.return_value
        mock_service.update_task = AsyncMock(
            side_effect=Exception("Database connection failed")
        )

        # Act & Assert
        with pytest.raises(DatabaseError):
            await update_task(user_id, task_id, new_title, mock_db)
