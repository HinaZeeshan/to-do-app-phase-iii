"""
Test User Stories 3, 4, 5: Complete, Delete, Update Tasks via Natural Language.

Tests agent's ability to perform task lifecycle operations from natural language commands.
"""

import pytest
from uuid import UUID, uuid4
from unittest.mock import AsyncMock, patch
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from src.agent.chat_agent import run_agent
from src.mcp.errors import TaskNotFoundError


# Test user ID
TEST_USER_ID = UUID("123e4567-e89b-12d3-a456-426614174000")


def create_mock_task(user_id: UUID, title: str, is_completed: bool = False) -> dict:
    """Create a mock task dict for testing."""
    task_id = uuid4()
    now = datetime.utcnow()
    return {
        "id": str(task_id),
        "user_id": str(user_id),
        "title": title,
        "description": None,
        "is_completed": is_completed,
        "completed_at": now.isoformat() if is_completed else None,
        "created_at": now.isoformat(),
        "updated_at": now.isoformat(),
    }


# ========== User Story 3: Complete Task ==========

@pytest.mark.asyncio
async def test_us3_scenario1_finished_buying_milk():
    """
    US3 Scenario 1: Given I have a task "buy milk", When I send "I finished buying milk",
    Then the agent marks the task as complete and confirms.
    """
    mock_db = AsyncMock(spec=AsyncSession)
    mock_task = create_mock_task(TEST_USER_ID, "buy milk")
    completed_task = {**mock_task, "is_completed": True, "completed_at": datetime.utcnow().isoformat()}

    with patch("src.mcp.tools.list_tasks.list_tasks", new_callable=AsyncMock) as mock_list, \
         patch("src.agent.tool_mapper.complete_task", new_callable=AsyncMock) as mock_complete:
        mock_list.return_value = [mock_task]
        mock_complete.return_value = completed_task

        response = await run_agent(
            user_id=TEST_USER_ID,
            message="I finished buying milk",
            conversation_history=[],
            db=mock_db,
        )

    # Verify response
    assert "marked" in response.response_text.lower() or "done" in response.response_text.lower()
    assert "milk" in response.response_text.lower()

    # Verify tool invocation
    tool = response.tool_invocations[0]
    assert tool.tool_name == "complete_task"
    assert tool.error is None


@pytest.mark.asyncio
async def test_us3_scenario2_partial_title_match():
    """
    US3 Scenario 2: Given I have multiple tasks, When I send "mark the dentist task as done",
    Then the agent identifies the correct task by partial title match.
    """
    mock_db = AsyncMock(spec=AsyncSession)
    mock_task1 = create_mock_task(TEST_USER_ID, "buy milk")
    mock_task2 = create_mock_task(TEST_USER_ID, "call dentist")
    completed_task = {**mock_task2, "is_completed": True}

    with patch("src.mcp.tools.list_tasks.list_tasks", new_callable=AsyncMock) as mock_list, \
         patch("src.agent.tool_mapper.complete_task", new_callable=AsyncMock) as mock_complete:
        mock_list.return_value = [mock_task1, mock_task2]
        mock_complete.return_value = completed_task

        response = await run_agent(
            user_id=TEST_USER_ID,
            message="mark the dentist task as done",
            conversation_history=[],
            db=mock_db,
        )

    assert "dentist" in response.response_text.lower()
    tool = response.tool_invocations[0]
    assert tool.tool_name == "complete_task"


@pytest.mark.asyncio
async def test_us3_scenario4_task_not_found():
    """
    US3 Scenario 4: Given I reference a task that doesn't exist, When I send "mark 'walk the dog' as done",
    Then the agent responds "I couldn't find a task matching 'walk the dog'".
    """
    mock_db = AsyncMock(spec=AsyncSession)

    with patch("src.mcp.tools.list_tasks.list_tasks", new_callable=AsyncMock) as mock_list:
        mock_list.return_value = []  # No tasks

        response = await run_agent(
            user_id=TEST_USER_ID,
            message="mark 'walk the dog' as done",
            conversation_history=[],
            db=mock_db,
        )

    assert "couldn't find" in response.response_text.lower() or "not found" in response.response_text.lower()
    tool = response.tool_invocations[0]
    assert tool.error is not None


# ========== User Story 4: Delete Task ==========

@pytest.mark.asyncio
async def test_us4_scenario1_delete_milk_task():
    """
    US4 Scenario 1: Given I have a task "buy milk", When I send "delete the milk task",
    Then the agent removes the task and confirms.
    """
    mock_db = AsyncMock(spec=AsyncSession)
    mock_task = create_mock_task(TEST_USER_ID, "buy milk")

    with patch("src.mcp.tools.list_tasks.list_tasks", new_callable=AsyncMock) as mock_list, \
         patch("src.agent.tool_mapper.delete_task", new_callable=AsyncMock) as mock_delete:
        mock_list.return_value = [mock_task]
        mock_delete.return_value = None

        response = await run_agent(
            user_id=TEST_USER_ID,
            message="delete the milk task",
            conversation_history=[],
            db=mock_db,
        )

    assert "deleted" in response.response_text.lower() or "removed" in response.response_text.lower()

    tool = response.tool_invocations[0]
    assert tool.tool_name == "delete_task"
    assert tool.error is None


@pytest.mark.asyncio
async def test_us4_scenario2_remove_buy_milk():
    """
    US4 Scenario 2: Given I have a task "buy milk", When I send "remove 'buy milk'",
    Then the agent deletes the task and provides confirmation.
    """
    mock_db = AsyncMock(spec=AsyncSession)
    mock_task = create_mock_task(TEST_USER_ID, "buy milk")

    with patch("src.mcp.tools.list_tasks.list_tasks", new_callable=AsyncMock) as mock_list, \
         patch("src.agent.tool_mapper.delete_task", new_callable=AsyncMock) as mock_delete:
        mock_list.return_value = [mock_task]
        mock_delete.return_value = None

        response = await run_agent(
            user_id=TEST_USER_ID,
            message="remove 'buy milk'",
            conversation_history=[],
            db=mock_db,
        )

    assert "deleted" in response.response_text.lower() or "removed" in response.response_text.lower()


@pytest.mark.asyncio
async def test_us4_scenario3_delete_nonexistent_task():
    """
    US4 Scenario 3: Given I reference a task that doesn't exist, When I send "delete 'walk the dog'",
    Then the agent responds "I couldn't find a task matching 'walk the dog'".
    """
    mock_db = AsyncMock(spec=AsyncSession)

    with patch("src.mcp.tools.list_tasks.list_tasks", new_callable=AsyncMock) as mock_list:
        mock_list.return_value = []

        response = await run_agent(
            user_id=TEST_USER_ID,
            message="delete 'walk the dog'",
            conversation_history=[],
            db=mock_db,
        )

    assert "couldn't find" in response.response_text.lower()
    tool = response.tool_invocations[0]
    assert tool.error is not None


# ========== User Story 5: Update Task ==========

@pytest.mark.asyncio
async def test_us5_scenario1_change_buy_milk_to_almond_milk():
    """
    US5 Scenario 1: Given I have a task "buy milk", When I send "change 'buy milk' to 'buy almond milk'",
    Then the agent updates the task title and confirms.
    """
    mock_db = AsyncMock(spec=AsyncSession)
    mock_task = create_mock_task(TEST_USER_ID, "buy milk")
    updated_task = {**mock_task, "title": "buy almond milk"}

    with patch("src.mcp.tools.list_tasks.list_tasks", new_callable=AsyncMock) as mock_list, \
         patch("src.agent.tool_mapper.update_task", new_callable=AsyncMock) as mock_update:
        mock_list.return_value = [mock_task]
        mock_update.return_value = updated_task

        response = await run_agent(
            user_id=TEST_USER_ID,
            message="change 'buy milk' to 'buy almond milk'",
            conversation_history=[],
            db=mock_db,
        )

    assert "updated" in response.response_text.lower()
    assert "almond milk" in response.response_text.lower()

    tool = response.tool_invocations[0]
    assert tool.tool_name == "update_task"
    assert tool.result["title"] == "buy almond milk"


@pytest.mark.asyncio
async def test_us5_scenario3_update_nonexistent_task():
    """
    US5 Scenario 3: Given I reference a task that doesn't exist, When I send "update 'walk the dog' to 'walk the cat'",
    Then the agent responds "I couldn't find a task matching 'walk the dog'".
    """
    mock_db = AsyncMock(spec=AsyncSession)

    with patch("src.mcp.tools.list_tasks.list_tasks", new_callable=AsyncMock) as mock_list:
        mock_list.return_value = []

        response = await run_agent(
            user_id=TEST_USER_ID,
            message="update 'walk the dog' to 'walk the cat'",
            conversation_history=[],
            db=mock_db,
        )

    assert "couldn't find" in response.response_text.lower()
    tool = response.tool_invocations[0]
    assert tool.error is not None
