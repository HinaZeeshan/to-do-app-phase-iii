"""
Tests for delete_task MCP tool.

Validates US4 scenarios:
1. User owns task → permanently deleted
2. task_id doesn't exist → TaskNotFoundError
3. User A tries to delete user B's task → UnauthorizedError
4. Delete same task twice → TaskNotFoundError on second call
5. Invalid task_id format → ValidationError
"""

import pytest
from uuid import uuid4, UUID
from unittest.mock import AsyncMock, Mock, patch
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from src.mcp.tools.delete_task import delete_task
from src.mcp.errors import TaskNotFoundError, ValidationError, UnauthorizedError, DatabaseError


@pytest.mark.asyncio
async def test_delete_task_success():
    """
    US4 Scenario 1: User owns task → permanently deleted.
    """
    # Arrange
    user_id = uuid4()
    task_id = uuid4()
    mock_db = AsyncMock(spec=AsyncSession)

    # Mock TaskService.delete_task
    with patch("src.mcp.tools.delete_task.TaskService") as MockService:
        mock_service = MockService.return_value
        mock_service.delete_task = AsyncMock(return_value=None)

        # Act
        result = await delete_task(user_id, task_id, mock_db)

        # Assert
        assert result is None
        mock_service.delete_task.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_task_not_found():
    """
    US4 Scenario 2: task_id doesn't exist → TaskNotFoundError.
    """
    # Arrange
    user_id = uuid4()
    task_id = uuid4()
    mock_db = AsyncMock(spec=AsyncSession)

    # Mock TaskService to raise 404
    with patch("src.mcp.tools.delete_task.TaskService") as MockService:
        mock_service = MockService.return_value
        mock_service.delete_task = AsyncMock(
            side_effect=HTTPException(status_code=404, detail="Task not found")
        )

        # Act & Assert
        with pytest.raises(TaskNotFoundError, match="Task not found"):
            await delete_task(user_id, task_id, mock_db)


@pytest.mark.asyncio
async def test_delete_task_unauthorized():
    """
    US4 Scenario 3: User A tries to delete user B's task → UnauthorizedError.
    """
    # Arrange
    user_a_id = uuid4()
    task_id = uuid4()
    mock_db = AsyncMock(spec=AsyncSession)

    # Mock TaskService to raise 403
    with patch("src.mcp.tools.delete_task.TaskService") as MockService:
        mock_service = MockService.return_value
        mock_service.delete_task = AsyncMock(
            side_effect=HTTPException(
                status_code=403,
                detail="Access forbidden: user_id does not match authenticated user",
            )
        )

        # Act & Assert
        with pytest.raises(UnauthorizedError):
            await delete_task(user_a_id, task_id, mock_db)


@pytest.mark.asyncio
async def test_delete_task_twice():
    """
    US4 Scenario 4: Delete same task twice → TaskNotFoundError on second call.
    """
    # Arrange
    user_id = uuid4()
    task_id = uuid4()
    mock_db = AsyncMock(spec=AsyncSession)

    # Mock TaskService: first call succeeds, second call raises 404
    with patch("src.mcp.tools.delete_task.TaskService") as MockService:
        mock_service = MockService.return_value

        # First call: success
        mock_service.delete_task = AsyncMock(return_value=None)
        result = await delete_task(user_id, task_id, mock_db)
        assert result is None

        # Second call: task not found
        mock_service.delete_task = AsyncMock(
            side_effect=HTTPException(status_code=404, detail="Task not found")
        )

        # Act & Assert
        with pytest.raises(TaskNotFoundError, match="Task not found"):
            await delete_task(user_id, task_id, mock_db)


@pytest.mark.asyncio
async def test_delete_task_invalid_task_id():
    """
    US4 Scenario 5: Invalid task_id format → ValidationError.
    """
    # Arrange
    user_id = uuid4()
    invalid_task_id = "not-a-uuid"
    mock_db = AsyncMock(spec=AsyncSession)

    # Act & Assert
    with pytest.raises((ValidationError, ValueError, TypeError)):
        await delete_task(user_id, invalid_task_id, mock_db)  # type: ignore


@pytest.mark.asyncio
async def test_delete_task_database_error():
    """
    Edge case: Database error → DatabaseError.
    """
    # Arrange
    user_id = uuid4()
    task_id = uuid4()
    mock_db = AsyncMock(spec=AsyncSession)

    # Mock TaskService to raise database error
    with patch("src.mcp.tools.delete_task.TaskService") as MockService:
        mock_service = MockService.return_value
        mock_service.delete_task = AsyncMock(
            side_effect=Exception("Database connection failed")
        )

        # Act & Assert
        with pytest.raises(DatabaseError):
            await delete_task(user_id, task_id, mock_db)
