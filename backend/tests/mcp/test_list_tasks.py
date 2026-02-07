"""
Tests for list_tasks MCP tool.

Validates US2 scenarios:
1. filter="all" → returns all 5 tasks sorted
2. filter="pending" → returns 3 pending tasks
3. filter="completed" → returns 2 completed tasks
4. No tasks → returns empty list, not error
5. Invalid user_id → ValidationError
"""

import pytest
from uuid import uuid4, UUID
from unittest.mock import AsyncMock, Mock, patch
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta

from src.mcp.tools.list_tasks import list_tasks
from src.mcp.errors import ValidationError, DatabaseError
from src.models.task import Task


def create_mock_task(
    user_id: UUID,
    title: str,
    is_completed: bool,
    created_at: datetime,
) -> Mock:
    """Helper to create mock task."""
    mock_task = Mock(spec=Task)
    mock_task.id = uuid4()
    mock_task.user_id = user_id
    mock_task.title = title
    mock_task.description = None
    mock_task.is_completed = is_completed
    mock_task.completed_at = datetime.utcnow() if is_completed else None
    mock_task.created_at = created_at
    mock_task.updated_at = created_at
    mock_task.model_dump.return_value = {
        "id": str(mock_task.id),
        "user_id": str(mock_task.user_id),
        "title": mock_task.title,
        "description": None,
        "is_completed": mock_task.is_completed,
        "completed_at": (
            mock_task.completed_at.isoformat() if mock_task.completed_at else None
        ),
        "created_at": mock_task.created_at.isoformat(),
        "updated_at": mock_task.updated_at.isoformat(),
    }
    return mock_task


@pytest.mark.asyncio
async def test_list_tasks_filter_all():
    """
    US2 Scenario 1: filter="all" → returns all 5 tasks sorted by created_at descending.
    """
    # Arrange
    user_id = uuid4()
    mock_db = AsyncMock(spec=AsyncSession)

    now = datetime.utcnow()
    # Create 5 tasks (3 pending, 2 completed) with different timestamps
    mock_tasks = [
        create_mock_task(user_id, "task1", False, now - timedelta(hours=5)),
        create_mock_task(user_id, "task2", True, now - timedelta(hours=4)),
        create_mock_task(user_id, "task3", False, now - timedelta(hours=3)),
        create_mock_task(user_id, "task4", True, now - timedelta(hours=2)),
        create_mock_task(user_id, "task5", False, now - timedelta(hours=1)),
    ]

    # Mock TaskService.list_tasks
    with patch("src.mcp.tools.list_tasks.TaskService") as MockService:
        mock_service = MockService.return_value
        mock_service.list_tasks = AsyncMock(return_value=mock_tasks)

        # Act
        result = await list_tasks(user_id, "all", mock_db)

        # Assert
        assert len(result) == 5
        # Should be sorted by created_at descending (task5 first, task1 last)
        assert result[0]["title"] == "task5"
        assert result[4]["title"] == "task1"


@pytest.mark.asyncio
async def test_list_tasks_filter_pending():
    """
    US2 Scenario 2: filter="pending" → returns 3 pending tasks.
    """
    # Arrange
    user_id = uuid4()
    mock_db = AsyncMock(spec=AsyncSession)

    now = datetime.utcnow()
    # Create 5 tasks (3 pending, 2 completed)
    mock_tasks = [
        create_mock_task(user_id, "pending1", False, now - timedelta(hours=5)),
        create_mock_task(user_id, "completed1", True, now - timedelta(hours=4)),
        create_mock_task(user_id, "pending2", False, now - timedelta(hours=3)),
        create_mock_task(user_id, "completed2", True, now - timedelta(hours=2)),
        create_mock_task(user_id, "pending3", False, now - timedelta(hours=1)),
    ]

    # Mock TaskService.list_tasks
    with patch("src.mcp.tools.list_tasks.TaskService") as MockService:
        mock_service = MockService.return_value
        mock_service.list_tasks = AsyncMock(return_value=mock_tasks)

        # Act
        result = await list_tasks(user_id, "pending", mock_db)

        # Assert
        assert len(result) == 3
        assert all(not task["is_completed"] for task in result)
        # Should be sorted by created_at descending
        assert result[0]["title"] == "pending3"
        assert result[2]["title"] == "pending1"


@pytest.mark.asyncio
async def test_list_tasks_filter_completed():
    """
    US2 Scenario 3: filter="completed" → returns 2 completed tasks.
    """
    # Arrange
    user_id = uuid4()
    mock_db = AsyncMock(spec=AsyncSession)

    now = datetime.utcnow()
    # Create 5 tasks (3 pending, 2 completed)
    mock_tasks = [
        create_mock_task(user_id, "pending1", False, now - timedelta(hours=5)),
        create_mock_task(user_id, "completed1", True, now - timedelta(hours=4)),
        create_mock_task(user_id, "pending2", False, now - timedelta(hours=3)),
        create_mock_task(user_id, "completed2", True, now - timedelta(hours=2)),
        create_mock_task(user_id, "pending3", False, now - timedelta(hours=1)),
    ]

    # Mock TaskService.list_tasks
    with patch("src.mcp.tools.list_tasks.TaskService") as MockService:
        mock_service = MockService.return_value
        mock_service.list_tasks = AsyncMock(return_value=mock_tasks)

        # Act
        result = await list_tasks(user_id, "completed", mock_db)

        # Assert
        assert len(result) == 2
        assert all(task["is_completed"] for task in result)
        # Should be sorted by created_at descending
        assert result[0]["title"] == "completed2"
        assert result[1]["title"] == "completed1"


@pytest.mark.asyncio
async def test_list_tasks_no_tasks():
    """
    US2 Scenario 4: No tasks → returns empty list, not error.
    """
    # Arrange
    user_id = uuid4()
    mock_db = AsyncMock(spec=AsyncSession)

    # Mock TaskService.list_tasks returning empty list
    with patch("src.mcp.tools.list_tasks.TaskService") as MockService:
        mock_service = MockService.return_value
        mock_service.list_tasks = AsyncMock(return_value=[])

        # Act
        result = await list_tasks(user_id, "all", mock_db)

        # Assert
        assert result == []
        assert isinstance(result, list)


@pytest.mark.asyncio
async def test_list_tasks_invalid_user_id():
    """
    US2 Scenario 5: Invalid user_id → ValidationError.
    """
    # Arrange
    invalid_user_id = "not-a-uuid"
    mock_db = AsyncMock(spec=AsyncSession)

    # Act & Assert
    with pytest.raises((ValidationError, ValueError, TypeError)):
        await list_tasks(invalid_user_id, "all", mock_db)  # type: ignore


@pytest.mark.asyncio
async def test_list_tasks_invalid_filter():
    """
    Edge case: Invalid filter value → ValidationError.
    """
    # Arrange
    user_id = uuid4()
    invalid_filter = "invalid_filter"
    mock_db = AsyncMock(spec=AsyncSession)

    # Act & Assert
    with pytest.raises(ValidationError, match="pattern"):
        await list_tasks(user_id, invalid_filter, mock_db)


@pytest.mark.asyncio
async def test_list_tasks_database_error():
    """
    Edge case: Database error → DatabaseError.
    """
    # Arrange
    user_id = uuid4()
    mock_db = AsyncMock(spec=AsyncSession)

    # Mock TaskService to raise database error
    with patch("src.mcp.tools.list_tasks.TaskService") as MockService:
        mock_service = MockService.return_value
        mock_service.list_tasks = AsyncMock(
            side_effect=Exception("Database connection failed")
        )

        # Act & Assert
        with pytest.raises(DatabaseError):
            await list_tasks(user_id, "all", mock_db)
