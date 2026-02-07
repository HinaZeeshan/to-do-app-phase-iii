"""
Tests for add_task MCP tool.

Validates US1 scenarios:
1. Valid inputs → task persisted and returned
2. Empty title → ValidationError
3. Invalid user_id format → ValidationError
4. Title exceeds 500 chars → ValidationError
5. Database unavailable → DatabaseError
"""

import pytest
from uuid import uuid4, UUID
from unittest.mock import AsyncMock, Mock, patch
from sqlalchemy.ext.asyncio import AsyncSession

from src.mcp.tools.add_task import add_task
from src.mcp.errors import ValidationError, DatabaseError
from src.models.task import Task
from datetime import datetime


@pytest.mark.asyncio
async def test_add_task_valid_inputs():
    """
    US1 Scenario 1: Valid inputs → task persisted and returned.
    """
    # Arrange
    user_id = uuid4()
    title = "buy milk"
    mock_db = AsyncMock(spec=AsyncSession)

    # Mock task object
    mock_task = Mock(spec=Task)
    mock_task.id = uuid4()
    mock_task.user_id = user_id
    mock_task.title = title
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

    # Mock TaskService.create_task
    with patch("src.mcp.tools.add_task.TaskService") as MockService:
        mock_service = MockService.return_value
        mock_service.create_task = AsyncMock(return_value=mock_task)

        # Act
        result = await add_task(user_id, title, mock_db)

        # Assert
        assert result["title"] == title
        assert result["user_id"] == str(user_id)
        assert result["is_completed"] is False
        mock_service.create_task.assert_awaited_once()


@pytest.mark.asyncio
async def test_add_task_empty_title():
    """
    US1 Scenario 2: Empty title → ValidationError.
    """
    # Arrange
    user_id = uuid4()
    title = ""  # Empty title
    mock_db = AsyncMock(spec=AsyncSession)

    # Act & Assert
    with pytest.raises(ValidationError, match="title"):
        await add_task(user_id, title, mock_db)


@pytest.mark.asyncio
async def test_add_task_whitespace_only_title():
    """
    US1 Scenario 2 (variant): Whitespace-only title → ValidationError.
    """
    # Arrange
    user_id = uuid4()
    title = "   "  # Whitespace only
    mock_db = AsyncMock(spec=AsyncSession)

    # Act & Assert
    with pytest.raises(ValidationError):
        await add_task(user_id, title, mock_db)


@pytest.mark.asyncio
async def test_add_task_invalid_user_id_format():
    """
    US1 Scenario 3: Invalid user_id format → ValidationError.
    """
    # Arrange
    invalid_user_id = "not-a-uuid"  # Invalid UUID
    title = "buy milk"
    mock_db = AsyncMock(spec=AsyncSession)

    # Act & Assert
    with pytest.raises((ValidationError, ValueError, TypeError)):
        # UUID constructor will raise ValueError/TypeError for invalid format
        await add_task(invalid_user_id, title, mock_db)  # type: ignore


@pytest.mark.asyncio
async def test_add_task_title_exceeds_500_chars():
    """
    US1 Scenario 4: Title exceeds 500 chars → ValidationError.
    """
    # Arrange
    user_id = uuid4()
    title = "a" * 501  # 501 characters
    mock_db = AsyncMock(spec=AsyncSession)

    # Act & Assert
    with pytest.raises(ValidationError, match="500"):
        await add_task(user_id, title, mock_db)


@pytest.mark.asyncio
async def test_add_task_database_unavailable():
    """
    US1 Scenario 5: Database unavailable → DatabaseError.
    """
    # Arrange
    user_id = uuid4()
    title = "buy milk"
    mock_db = AsyncMock(spec=AsyncSession)

    # Mock TaskService to raise database error
    with patch("src.mcp.tools.add_task.TaskService") as MockService:
        mock_service = MockService.return_value
        mock_service.create_task = AsyncMock(
            side_effect=Exception("Database connection failed")
        )

        # Act & Assert
        with pytest.raises(DatabaseError, match="Unexpected error"):
            await add_task(user_id, title, mock_db)


@pytest.mark.asyncio
async def test_add_task_title_exactly_500_chars():
    """
    Edge case: Title exactly 500 chars (should succeed).
    """
    # Arrange
    user_id = uuid4()
    title = "a" * 500  # Exactly 500 characters
    mock_db = AsyncMock(spec=AsyncSession)

    # Mock task object
    mock_task = Mock(spec=Task)
    mock_task.id = uuid4()
    mock_task.user_id = user_id
    mock_task.title = title
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

    # Mock TaskService.create_task
    with patch("src.mcp.tools.add_task.TaskService") as MockService:
        mock_service = MockService.return_value
        mock_service.create_task = AsyncMock(return_value=mock_task)

        # Act
        result = await add_task(user_id, title, mock_db)

        # Assert
        assert result["title"] == title
        assert len(result["title"]) == 500
