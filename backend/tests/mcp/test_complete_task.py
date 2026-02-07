"""
Tests for complete_task MCP tool.

Validates US3 scenarios:
1. User owns pending task → marked complete with timestamp
2. task_id doesn't exist → TaskNotFoundError
3. User A tries to complete user B's task → UnauthorizedError
4. Already completed task → idempotent, returns task
5. Invalid task_id format → ValidationError
"""

import pytest
from uuid import uuid4, UUID
from unittest.mock import AsyncMock, Mock, patch
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from fastapi import HTTPException

from src.mcp.tools.complete_task import complete_task
from src.mcp.errors import TaskNotFoundError, ValidationError, UnauthorizedError, DatabaseError
from src.models.task import Task


@pytest.mark.asyncio
async def test_complete_task_success():
    """
    US3 Scenario 1: User owns pending task → marked complete with timestamp.
    """
    # Arrange
    user_id = uuid4()
    task_id = uuid4()
    mock_db = AsyncMock(spec=AsyncSession)

    # Mock completed task
    mock_task = Mock(spec=Task)
    mock_task.id = task_id
    mock_task.user_id = user_id
    mock_task.title = "buy milk"
    mock_task.description = None
    mock_task.is_completed = True
    mock_task.completed_at = datetime.utcnow()
    mock_task.created_at = datetime.utcnow()
    mock_task.updated_at = datetime.utcnow()
    mock_task.model_dump.return_value = {
        "id": str(mock_task.id),
        "user_id": str(mock_task.user_id),
        "title": mock_task.title,
        "description": None,
        "is_completed": True,
        "completed_at": mock_task.completed_at.isoformat(),
        "created_at": mock_task.created_at.isoformat(),
        "updated_at": mock_task.updated_at.isoformat(),
    }

    # Mock TaskService.complete_task
    with patch("src.mcp.tools.complete_task.TaskService") as MockService:
        mock_service = MockService.return_value
        mock_service.complete_task = AsyncMock(return_value=mock_task)

        # Act
        result = await complete_task(user_id, task_id, mock_db)

        # Assert
        assert result["is_completed"] is True
        assert result["completed_at"] is not None
        assert result["id"] == str(task_id)
        mock_service.complete_task.assert_awaited_once()


@pytest.mark.asyncio
async def test_complete_task_not_found():
    """
    US3 Scenario 2: task_id doesn't exist → TaskNotFoundError.
    """
    # Arrange
    user_id = uuid4()
    task_id = uuid4()
    mock_db = AsyncMock(spec=AsyncSession)

    # Mock TaskService to raise 404
    with patch("src.mcp.tools.complete_task.TaskService") as MockService:
        mock_service = MockService.return_value
        mock_service.complete_task = AsyncMock(
            side_effect=HTTPException(status_code=404, detail="Task not found")
        )

        # Act & Assert
        with pytest.raises(TaskNotFoundError, match="Task not found"):
            await complete_task(user_id, task_id, mock_db)


@pytest.mark.asyncio
async def test_complete_task_unauthorized():
    """
    US3 Scenario 3: User A tries to complete user B's task → UnauthorizedError.
    """
    # Arrange
    user_a_id = uuid4()
    user_b_id = uuid4()
    task_id = uuid4()
    mock_db = AsyncMock(spec=AsyncSession)

    # Mock TaskService to raise 403 (task exists but user doesn't own it)
    with patch("src.mcp.tools.complete_task.TaskService") as MockService:
        mock_service = MockService.return_value
        mock_service.complete_task = AsyncMock(
            side_effect=HTTPException(
                status_code=403,
                detail="Access forbidden: user_id does not match authenticated user",
            )
        )

        # Act & Assert
        with pytest.raises(UnauthorizedError):
            await complete_task(user_a_id, task_id, mock_db)


@pytest.mark.asyncio
async def test_complete_task_already_completed():
    """
    US3 Scenario 4: Already completed task → idempotent, returns task.
    """
    # Arrange
    user_id = uuid4()
    task_id = uuid4()
    mock_db = AsyncMock(spec=AsyncSession)

    # Mock already completed task
    mock_task = Mock(spec=Task)
    mock_task.id = task_id
    mock_task.user_id = user_id
    mock_task.title = "buy milk"
    mock_task.description = None
    mock_task.is_completed = True
    mock_task.completed_at = datetime.utcnow()
    mock_task.created_at = datetime.utcnow()
    mock_task.updated_at = datetime.utcnow()
    mock_task.model_dump.return_value = {
        "id": str(mock_task.id),
        "user_id": str(mock_task.user_id),
        "title": mock_task.title,
        "description": None,
        "is_completed": True,
        "completed_at": mock_task.completed_at.isoformat(),
        "created_at": mock_task.created_at.isoformat(),
        "updated_at": mock_task.updated_at.isoformat(),
    }

    # Mock TaskService.complete_task (idempotent - returns task as-is)
    with patch("src.mcp.tools.complete_task.TaskService") as MockService:
        mock_service = MockService.return_value
        mock_service.complete_task = AsyncMock(return_value=mock_task)

        # Act
        result = await complete_task(user_id, task_id, mock_db)

        # Assert
        assert result["is_completed"] is True
        assert result["completed_at"] is not None
        # Should not raise error (idempotent)


@pytest.mark.asyncio
async def test_complete_task_invalid_task_id():
    """
    US3 Scenario 5: Invalid task_id format → ValidationError.
    """
    # Arrange
    user_id = uuid4()
    invalid_task_id = "not-a-uuid"
    mock_db = AsyncMock(spec=AsyncSession)

    # Act & Assert
    with pytest.raises((ValidationError, ValueError, TypeError)):
        await complete_task(user_id, invalid_task_id, mock_db)  # type: ignore


@pytest.mark.asyncio
async def test_complete_task_database_error():
    """
    Edge case: Database error → DatabaseError.
    """
    # Arrange
    user_id = uuid4()
    task_id = uuid4()
    mock_db = AsyncMock(spec=AsyncSession)

    # Mock TaskService to raise database error
    with patch("src.mcp.tools.complete_task.TaskService") as MockService:
        mock_service = MockService.return_value
        mock_service.complete_task = AsyncMock(
            side_effect=Exception("Database connection failed")
        )

        # Act & Assert
        with pytest.raises(DatabaseError):
            await complete_task(user_id, task_id, mock_db)
