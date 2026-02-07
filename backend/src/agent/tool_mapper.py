"""
Tool mapping and MCP tool invocation.

Maps intents to MCP tools and handles tool execution with error handling.
"""

import logging
import time
from typing import Any, Dict, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from ..mcp.errors import (
    TaskNotFoundError,
    UnauthorizedError,
    ValidationError,
)
from ..mcp.tools.add_task import add_task
from ..mcp.tools.complete_task import complete_task
from ..mcp.tools.delete_task import delete_task
from ..mcp.tools.list_tasks import list_tasks
from ..mcp.tools.update_task import update_task
from .schemas import Intent, IntentClassificationResult, ToolInvocation

logger = logging.getLogger(__name__)


async def invoke_tool(
    intent_result: IntentClassificationResult,
    user_id: UUID,
    db: AsyncSession,
    tasks: Optional[list] = None,
) -> ToolInvocation:
    """
    Invoke the appropriate MCP tool based on classified intent.

    Args:
        intent_result: Intent classification result with extracted parameters
        user_id: Authenticated user ID
        db: Database session for MCP tool operations
        tasks: Current user tasks (for task reference matching)

    Returns:
        ToolInvocation record with tool name, parameters, result/error, duration

    Raises:
        ValueError: If intent cannot be mapped to a tool
    """
    intent = intent_result.intent
    params = intent_result.extracted_params
    start_time = time.time()

    tool_name = ""
    tool_params = {}
    result = None
    error = None

    try:
        if intent == Intent.CREATE_TASK:
            tool_name = "add_task"
            task_title = params.get("task_title", "")
            tool_params = {"user_id": user_id, "title": task_title}
            result = await add_task(user_id, task_title, db)

        elif intent == Intent.LIST_TASKS:
            tool_name = "list_tasks"
            filter_type = params.get("filter", "all")
            tool_params = {"user_id": user_id, "filter": filter_type}
            result = await list_tasks(user_id, filter_type, db)

        elif intent == Intent.COMPLETE_TASK:
            tool_name = "complete_task"
            task_id = match_task_by_reference(params.get("task_reference", ""), tasks)
            if not task_id:
                raise TaskNotFoundError(f"Task not found: {params.get('task_reference', '')}")
            tool_params = {"user_id": user_id, "task_id": task_id}
            result = await complete_task(user_id, task_id, db)

        elif intent == Intent.DELETE_TASK:
            tool_name = "delete_task"
            task_id = match_task_by_reference(params.get("task_reference", ""), tasks)
            if not task_id:
                raise TaskNotFoundError(f"Task not found: {params.get('task_reference', '')}")
            tool_params = {"user_id": user_id, "task_id": task_id}
            await delete_task(user_id, task_id, db)
            result = {"success": True}

        elif intent == Intent.UPDATE_TASK:
            tool_name = "update_task"
            task_id = match_task_by_reference(params.get("task_reference", ""), tasks)
            if not task_id:
                raise TaskNotFoundError(f"Task not found: {params.get('task_reference', '')}")
            new_title = params.get("new_title", "")
            tool_params = {"user_id": user_id, "task_id": task_id, "new_title": new_title}
            result = await update_task(user_id, task_id, new_title, db)

        else:
            raise ValueError(f"Cannot map intent {intent} to a tool")

    except (TaskNotFoundError, UnauthorizedError, ValidationError) as e:
        error = f"{e.__class__.__name__}: {str(e)}"
        result = None
    except Exception as e:
        import traceback
        traceback.print_exc()
        error = f"UnexpectedError: {str(e)}"
        result = None

    duration_ms = int((time.time() - start_time) * 1000)

    # Log MCP tool invocation for observability
    log_params = {k: str(v) if isinstance(v, UUID) else v for k, v in tool_params.items()}
    if error:
        logger.warning(
            "MCP tool invocation failed",
            extra={
                "user_id": str(user_id),
                "tool_name": tool_name,
                "parameters": log_params,
                "error": error,
                "duration_ms": duration_ms,
            },
        )
    else:
        logger.info(
            "MCP tool invocation succeeded",
            extra={
                "user_id": str(user_id),
                "tool_name": tool_name,
                "parameters": log_params,
                "duration_ms": duration_ms,
            },
        )

    return ToolInvocation(
        tool_name=tool_name,
        parameters=tool_params,
        result=result,
        error=error,
        duration_ms=duration_ms,
    )


def match_task_by_reference(reference: str, tasks: Optional[list]) -> Optional[UUID]:
    """
    Match a task by partial title reference.

    Args:
        reference: Partial or full task title
        tasks: List of user tasks to search

    Returns:
        Task UUID if found, None otherwise
    """
    if not tasks or not reference:
        return None

    reference_lower = str(reference).lower().strip()

    # First try exact match
    for task in tasks:
        if task["title"].lower() == reference_lower:
            return UUID(str(task["id"]))

    # Then try partial match (bidirectional - reference in title OR title in reference)
    matches = []
    for task in tasks:
        task_title_lower = task["title"].lower()
        # Check both directions for flexibility
        if reference_lower in task_title_lower or task_title_lower in reference_lower:
            matches.append(task)

    # If no matches, try word-based matching (e.g., "buying milk" matches "buy milk")
    if not matches:
        reference_words = set(reference_lower.split())
        for task in tasks:
            task_words = set(task["title"].lower().split())
            # If reference words significantly overlap with task words
            overlap = reference_words & task_words
            # Need at least 1 word match and >40% overlap
            if len(overlap) >= 1 and len(overlap) >= len(reference_words) * 0.4:
                matches.append(task)

    # If exactly one match, return it
    if len(matches) == 1:
        return UUID(str(matches[0]["id"]))

    # Multiple or no matches - return None (caller will handle)
    return None
