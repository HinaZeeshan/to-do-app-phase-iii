"""
Main AI chat agent runner.

Orchestrates intent classification, tool invocation, and response formatting
for natural language task management.
"""

import time
from typing import List
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from .intent_classifier import classify_intent
from .response_formatter import format_response
from .schemas import AgentRequest, AgentResponse, Intent
from .tool_mapper import invoke_tool


async def run_agent(
    user_id: UUID,
    message: str,
    conversation_history: List[dict],
    db: AsyncSession,
) -> AgentResponse:
    """
    Execute the AI chat agent with a user message.

    This is the main entry point for the agent. It:
    1. Classifies user intent from natural language
    2. Invokes appropriate MCP tool
    3. Formats response for user

    The agent is stateless - all context is provided via conversation_history.

    Args:
        user_id: Authenticated user ID from JWT
        message: Current user message
        conversation_history: Previous messages in conversation
        db: Database session for MCP tool operations

    Returns:
        AgentResponse with response_text, tool_invocations, and metadata
    """
    start_time = time.time()

    # Step 1: Classify intent and extract parameters
    intent_result = classify_intent(message, conversation_history)

    # Step 2: If unknown intent, return helpful fallback
    if intent_result.intent == Intent.UNKNOWN:
        response_text = (
            "I'm not sure what you'd like me to do. I can help you with:\n"
            "- Adding tasks (e.g., 'remind me to buy milk')\n"
            "- Listing tasks (e.g., 'what are my tasks?')\n"
            "- Completing tasks (e.g., 'mark buy milk as done')\n"
            "- Deleting tasks (e.g., 'delete the milk task')\n"
            "- Updating tasks (e.g., 'change buy milk to buy almond milk')"
        )
        return AgentResponse(
            response_text=response_text,
            tool_invocations=[],
            metadata={
                "intent": intent_result.intent.value,
                "confidence": intent_result.confidence,
                "processing_time_ms": int((time.time() - start_time) * 1000),
            },
        )

    # Step 3: Get current tasks (if needed for reference matching)
    tasks = None
    if intent_result.intent in (Intent.COMPLETE_TASK, Intent.DELETE_TASK, Intent.UPDATE_TASK):
        # Need to fetch tasks to match references - use real list_tasks MCP tool
        from ..mcp.tools.list_tasks import list_tasks

        tasks = await list_tasks(user_id, "all", db)

    # Step 4: Invoke MCP tool
    tool_invocation = await invoke_tool(intent_result, user_id, db, tasks)

    # Step 5: Format response
    task_title = (
        tool_invocation.result.get("title")
        if tool_invocation.result and isinstance(tool_invocation.result, dict)
        else ""
    )
    context = {
        "task_reference": intent_result.extracted_params.get("task_reference", ""),
        "task_title": task_title or intent_result.extracted_params.get("task_reference", ""),
    }
    response_text = format_response(tool_invocation, context)

    # Step 6: Return AgentResponse
    processing_time_ms = int((time.time() - start_time) * 1000)

    return AgentResponse(
        response_text=response_text,
        tool_invocations=[tool_invocation],
        metadata={
            "intent": intent_result.intent.value,
            "confidence": intent_result.confidence,
            "processing_time_ms": processing_time_ms,
        },
    )
