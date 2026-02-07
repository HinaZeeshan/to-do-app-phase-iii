"""
Integration tests for AI Chat Agent.

Tests determinism, performance, and edge case handling.
"""

import pytest
from uuid import UUID, uuid4
from unittest.mock import AsyncMock, patch
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from src.agent.chat_agent import run_agent


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
async def test_determinism_identical_inputs_identical_outputs():
    """
    T096: Determinism test - run identical request 10 times, verify identical responses.

    Constitutional requirement: identical inputs → identical outputs 100% of time.
    """
    message = "remind me to buy milk"
    conversation_history = []
    mock_db = AsyncMock(spec=AsyncSession)
    mock_task = create_mock_task(TEST_USER_ID, "buy milk")

    # Run same request 10 times
    responses = []
    for _ in range(10):
        with patch("src.agent.tool_mapper.add_task", new_callable=AsyncMock) as mock_add:
            mock_add.return_value = mock_task
            response = await run_agent(TEST_USER_ID, message, conversation_history, mock_db)
            responses.append(response)

    # Verify all responses are identical
    first_response_text = responses[0].response_text
    first_tool_name = responses[0].tool_invocations[0].tool_name
    first_tool_params = responses[0].tool_invocations[0].parameters

    for response in responses[1:]:
        # Response text should be identical (deterministic formatting)
        assert response.response_text == first_response_text
        # Tool invocation should be identical
        assert response.tool_invocations[0].tool_name == first_tool_name
        assert response.tool_invocations[0].parameters == first_tool_params


@pytest.mark.asyncio
async def test_performance_agent_processing_under_500ms():
    """
    T097: Performance test - measure agent processing time, target <500ms.

    Note: This tests agent logic only, excluding mock tool execution time.
    """
    mock_db = AsyncMock(spec=AsyncSession)
    mock_task = create_mock_task(TEST_USER_ID, "buy milk")

    with patch("src.agent.tool_mapper.list_tasks", new_callable=AsyncMock) as mock_list:
        mock_list.return_value = [mock_task]

        response = await run_agent(
            user_id=TEST_USER_ID,
            message="what are my tasks?",
            conversation_history=[],
            db=mock_db,
        )

    processing_time_ms = response.metadata.get("processing_time_ms", -1)

    # Verify processing time tracked (can be 0 or 1 ms for very fast mock tools)
    assert processing_time_ms >= 0, f"Processing time not tracked: {processing_time_ms}"

    # Verify target <500ms (mock tools are fast, real tools will have DB latency)
    # Note: Real performance test needs Spec-5 integration with database
    assert processing_time_ms < 500, f"Agent processing too slow: {processing_time_ms}ms"


@pytest.mark.asyncio
async def test_edge_case_unrelated_conversational_message():
    """
    T098: Edge case - unrelated conversational messages get helpful fallback response.
    """
    mock_db = AsyncMock(spec=AsyncSession)

    response = await run_agent(
        user_id=TEST_USER_ID,
        message="hello how are you?",
        conversation_history=[],
        db=mock_db,
    )

    # Verify helpful guidance provided
    assert ("help" in response.response_text.lower() or
            "can" in response.response_text.lower() or
            "task" in response.response_text.lower())
    assert response.metadata["intent"] == "unknown"


@pytest.mark.asyncio
async def test_edge_case_large_conversation_history():
    """
    T098: Edge case - agent handles large conversation history (50+ messages).
    """
    mock_db = AsyncMock(spec=AsyncSession)
    mock_task = create_mock_task(TEST_USER_ID, "test task")

    # Create large conversation history
    conversation_history = []
    for i in range(60):
        conversation_history.append({
            "role": "user" if i % 2 == 0 else "assistant",
            "content": f"Message {i}",
        })

    with patch("src.agent.tool_mapper.add_task", new_callable=AsyncMock) as mock_add:
        mock_add.return_value = mock_task

        response = await run_agent(
            user_id=TEST_USER_ID,
            message="add task: test task",
            conversation_history=conversation_history,
            db=mock_db,
        )

    # Agent should handle gracefully (truncation handled in agent if needed)
    assert response.response_text is not None
    assert len(response.response_text) > 0


@pytest.mark.asyncio
async def test_edge_case_very_long_task_title():
    """
    T098: Edge case - agent accepts very long task titles and passes to tool.
    """
    mock_db = AsyncMock(spec=AsyncSession)
    long_title = "A" * 600  # Exceeds typical limits

    with patch("src.agent.tool_mapper.add_task", new_callable=AsyncMock) as mock_add:
        # Simulate tool handling the validation
        mock_add.return_value = create_mock_task(TEST_USER_ID, long_title[:500])

        response = await run_agent(
            user_id=TEST_USER_ID,
            message=f"add task: {long_title}",
            conversation_history=[],
            db=mock_db,
        )

    # Agent accepts and passes to tool; tool may validate
    tool = response.tool_invocations[0]
    assert tool.tool_name == "add_task"
    # Tool validation happens at tool layer, not agent layer
