"""
Response formatting for user-facing messages.

Generates conversational confirmations and translates errors to user-friendly messages.
Prevents hallucination by only using data from MCP tool responses.
"""

from typing import Any, Dict, List, Optional

from .config import CONFIRMATION_TEMPLATES, ERROR_MESSAGES
from .schemas import ToolInvocation


def format_response(tool_invocation: ToolInvocation, context: Optional[Dict[str, Any]] = None) -> str:
    """
    Format MCP tool result into user-facing response.

    Args:
        tool_invocation: Tool invocation record with result or error
        context: Optional context (e.g., task count, filter type)

    Returns:
        User-friendly response string
    """
    if tool_invocation.error:
        return format_error(tool_invocation.error, context)

    return format_success(tool_invocation, context)


def format_success(tool_invocation: ToolInvocation, context: Optional[Dict[str, Any]] = None) -> str:
    """
    Format successful tool invocation result.

    Args:
        tool_invocation: Tool invocation with result
        context: Optional context

    Returns:
        User-friendly confirmation message
    """
    tool_name = tool_invocation.tool_name
    result = tool_invocation.result

    if tool_name == "add_task":
        title = result.get("title", "task") if result else "task"
        return CONFIRMATION_TEMPLATES["task_created"].format(title=title)

    elif tool_name == "list_tasks":
        if not result or len(result) == 0:
            return CONFIRMATION_TEMPLATES["no_tasks"]

        # Format task list conversationally
        count = len(result)
        task_summaries = []
        for task in result[:5]:  # Show first 5 tasks
            status = "✓" if task.get("is_completed") else "○"
            task_summaries.append(f"{status} {task.get('title', 'untitled')}")

        summary = "\n".join(task_summaries)
        if count > 5:
            summary += f"\n... and {count - 5} more"

        return f"You have {count} task(s):\n{summary}"

    elif tool_name == "complete_task":
        title = result.get("title", "task") if result else "task"
        return CONFIRMATION_TEMPLATES["task_completed"].format(title=title)

    elif tool_name == "delete_task":
        # Task is already deleted, extract title from context if available
        title = context.get("task_title", "task") if context else "task"
        return CONFIRMATION_TEMPLATES["task_deleted"].format(title=title)

    elif tool_name == "update_task":
        title = result.get("title", "task") if result else "task"
        return CONFIRMATION_TEMPLATES["task_updated"].format(title=title)

    else:
        return "Done!"


def format_error(error: str, context: Optional[Dict[str, Any]] = None) -> str:
    """
    Translate technical error to user-friendly message.

    Args:
        error: Error string from MCP tool (e.g., "TaskNotFoundError: Task not found")
        context: Optional context (e.g., task reference)

    Returns:
        User-friendly error message
    """
    # Extract error type
    error_type = error.split(":")[0] if ":" in error else "GenericError"

    # Get template
    template = ERROR_MESSAGES.get(error_type, ERROR_MESSAGES["GenericError"])

    # Format with context
    reference = context.get("task_reference", "") if context else ""
    
    # Special case: Missing or empty reference
    if not reference or reference.strip() in ("''", ""):
        if error_type == "TaskNotFoundError":
            return "I couldn't figure out which task you were referring to. Could you tell me the task name?"
    
    details = error.split(":", 1)[1].strip() if ":" in error else error

    try:
        return template.format(reference=reference or "that task", details=details)
    except KeyError:
        # Fallback if template formatting fails
        return template


def format_clarification_question(ambiguous_tasks: List[Dict[str, Any]]) -> str:
    """
    Format clarification question for ambiguous task references.

    Args:
        ambiguous_tasks: List of tasks that match the reference

    Returns:
        Clarification question
    """
    if len(ambiguous_tasks) == 0:
        return "I couldn't find that task. Could you be more specific?"

    if len(ambiguous_tasks) == 1:
        # Shouldn't happen, but handle gracefully
        return f"Did you mean '{ambiguous_tasks[0].get('title', 'this task')}'?"

    # Multiple matches - ask for clarification
    task_titles = [f"'{task.get('title', 'untitled')}'" for task in ambiguous_tasks[:3]]

    if len(ambiguous_tasks) == 2:
        options = f"{task_titles[0]} or {task_titles[1]}"
    else:
        options = ", ".join(task_titles[:-1]) + f", or {task_titles[-1]}"

    return f"Which task did you mean: {options}?"
