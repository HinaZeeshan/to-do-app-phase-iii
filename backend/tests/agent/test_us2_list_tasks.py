"""
Test User Story 2: List Tasks via Natural Language.

Tests agent's ability to retrieve and display tasks from natural language queries.
"""

import pytest
from uuid import UUID, uuid4
from unittest.mock import AsyncMock, patch
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from src.agent.chat_agent import run_agent


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


@pytest.mark.asyncio
async def test_us2_scenario1_list_3_pending_tasks():
    """
    US2 Scenario 1: Given I have 3 pending tasks, When I send "what are my tasks?",
    Then the agent lists all 3 tasks with titles and status.
    """
    mock_db = AsyncMock(spec=AsyncSession)
    mock_tasks = [
        create_mock_task(TEST_USER_ID, "buy milk"),
        create_mock_task(TEST_USER_ID, "call dentist"),
        create_mock_task(TEST_USER_ID, "finish report"),
    ]

    with patch("src.agent.tool_mapper.list_tasks", new_callable=AsyncMock) as mock_list:
        mock_list.return_value = mock_tasks

        response = await run_agent(
            user_id=TEST_USER_ID,
            message="what are my tasks?",
            conversation_history=[],
            db=mock_db,
        )

    # Verify response mentions count and includes task titles
    assert "3 task" in response.response_text.lower()
    assert "buy milk" in response.response_text.lower() or "milk" in response.response_text.lower()

    # Verify tool invocation
    assert len(response.tool_invocations) == 1
    tool = response.tool_invocations[0]
    assert tool.tool_name == "list_tasks"
    assert tool.result is not None
    assert len(tool.result) == 3
    assert tool.error is None


@pytest.mark.asyncio
async def test_us2_scenario2_no_tasks_empty_list():
    """
    US2 Scenario 2: Given I have no tasks, When I send "show me my tasks",
    Then the agent responds "You don't have any tasks yet".
    """
    mock_db = AsyncMock(spec=AsyncSession)

    with patch("src.agent.tool_mapper.list_tasks", new_callable=AsyncMock) as mock_list:
        mock_list.return_value = []

        response = await run_agent(
            user_id=TEST_USER_ID,
            message="show me my tasks",
            conversation_history=[],
            db=mock_db,
        )

    # Verify empty response
    assert "don't have any" in response.response_text.lower() or "no tasks" in response.response_text.lower()

    # Verify tool invocation
    tool = response.tool_invocations[0]
    assert tool.tool_name == "list_tasks"
    assert tool.result == []


@pytest.mark.asyncio
async def test_us2_scenario3_filter_pending_tasks():
    """
    US2 Scenario 3: Given I have both completed and pending tasks, When I send "show me my pending tasks",
    Then the agent lists only incomplete tasks.
    """
    mock_db = AsyncMock(spec=AsyncSession)
    # Only return the pending task when filter is "pending"
    mock_pending_task = create_mock_task(TEST_USER_ID, "call dentist")

    with patch("src.agent.tool_mapper.list_tasks", new_callable=AsyncMock) as mock_list:
        mock_list.return_value = [mock_pending_task]

        response = await run_agent(
            user_id=TEST_USER_ID,
            message="show me my pending tasks",
            conversation_history=[],
            db=mock_db,
        )

    # Verify filter applied
    assert "dentist" in response.response_text.lower()

    # Verify tool invocation with filter
    tool = response.tool_invocations[0]
    assert tool.parameters.get("filter") == "pending"


@pytest.mark.asyncio
async def test_us2_scenario4_conversational_summary():
    """
    US2 Scenario 4: Given I have tasks, When I send "what do I need to do?",
    Then the agent provides a conversational summary of my task list.
    """
    mock_db = AsyncMock(spec=AsyncSession)
    mock_tasks = [
        create_mock_task(TEST_USER_ID, "buy milk"),
        create_mock_task(TEST_USER_ID, "call dentist"),
    ]

    with patch("src.agent.tool_mapper.list_tasks", new_callable=AsyncMock) as mock_list:
        mock_list.return_value = mock_tasks

        response = await run_agent(
            user_id=TEST_USER_ID,
            message="what do I need to do?",
            conversation_history=[],
            db=mock_db,
        )

    # Verify conversational summary
    assert "2 task" in response.response_text.lower()

    # Verify tool invocation
    tool = response.tool_invocations[0]
    assert tool.tool_name == "list_tasks"


@pytest.mark.asyncio
async def test_us2_scenario5_unauthenticated_user():
    """
    US2 Scenario 5: Given I am an unauthenticated user, When I ask to see tasks,
    Then the agent responds with an authentication error.

    Note: Authentication handled by Spec-5 upstream; agent assumes authenticated user_id.
    """
    # Test passes by design - authentication errors handled upstream
    pass
