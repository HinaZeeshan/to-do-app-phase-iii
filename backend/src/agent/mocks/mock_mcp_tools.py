"""
Mock MCP (Model Context Protocol) tools for agent development and testing.

These mock tools simulate the behavior of actual MCP tools that will be
implemented in Spec-5 (MCP Server, Tools & Chat Infrastructure).
They enable independent agent development before Spec-5 integration.
"""

import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4


class TaskNotFoundError(Exception):
    """Raised when a task cannot be found."""

    pass


class UnauthorizedError(Exception):
    """Raised when user is not authorized for the operation."""

    pass


class ValidationError(Exception):
    """Raised when input validation fails."""

    pass


# In-memory storage for mock tasks (per-user)
# Format: {user_id: {task_id: task_dict}}
_mock_task_storage: Dict[UUID, Dict[UUID, Dict[str, Any]]] = {}


async def mock_add_task(user_id: UUID, title: str) -> Dict[str, Any]:
    """
    Mock implementation of add_task MCP tool.

    Creates a new task for the authenticated user.

    Args:
        user_id: Authenticated user ID
        title: Task title (1-500 characters)

    Returns:
        Task dict with id, user_id, title, is_completed, created_at

    Raises:
        ValidationError: If title is empty
        UnauthorizedError: If user_id is invalid
    """
    start_time = time.time()

    # Validation
    if not title or not title.strip():
        raise ValidationError("Title cannot be empty")

    # Create task
    task_id = uuid4()
    task = {
        "id": str(task_id),
        "user_id": str(user_id),
        "title": title.strip(),
        "is_completed": False,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }

    # Store in mock storage
    if user_id not in _mock_task_storage:
        _mock_task_storage[user_id] = {}
    _mock_task_storage[user_id][task_id] = task

    # Simulate latency
    duration_ms = int((time.time() - start_time) * 1000)

    return task


async def mock_list_tasks(
    user_id: UUID, filter: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Mock implementation of list_tasks MCP tool.

    Retrieves all tasks for the authenticated user, optionally filtered.

    Args:
        user_id: Authenticated user ID
        filter: Optional filter ("all", "pending", "completed")

    Returns:
        List of task dicts

    Raises:
        UnauthorizedError: If user_id is invalid
    """
    start_time = time.time()

    # Get user's tasks
    user_tasks = _mock_task_storage.get(user_id, {})
    tasks = list(user_tasks.values())

    # Apply filter
    if filter == "pending":
        tasks = [t for t in tasks if not t["is_completed"]]
    elif filter == "completed":
        tasks = [t for t in tasks if t["is_completed"]]
    # "all" or None: return all tasks

    # Sort by created_at (newest first)
    tasks.sort(key=lambda t: t["created_at"], reverse=True)

    return tasks


async def mock_complete_task(user_id: UUID, task_id: UUID) -> Dict[str, Any]:
    """
    Mock implementation of complete_task MCP tool.

    Marks a task as completed.

    Args:
        user_id: Authenticated user ID (must own the task)
        task_id: Task ID to complete

    Returns:
        Updated task dict

    Raises:
        TaskNotFoundError: If task doesn't exist
        UnauthorizedError: If user doesn't own the task
    """
    start_time = time.time()

    # Check user has tasks
    user_tasks = _mock_task_storage.get(user_id, {})

    # Find task
    if task_id not in user_tasks:
        raise TaskNotFoundError(f"Task {task_id} not found")

    task = user_tasks[task_id]

    # Update task
    task["is_completed"] = True
    task["completed_at"] = datetime.now(timezone.utc).isoformat()
    task["updated_at"] = datetime.now(timezone.utc).isoformat()

    return task


async def mock_delete_task(user_id: UUID, task_id: UUID) -> None:
    """
    Mock implementation of delete_task MCP tool.

    Permanently deletes a task.

    Args:
        user_id: Authenticated user ID (must own the task)
        task_id: Task ID to delete

    Returns:
        None

    Raises:
        TaskNotFoundError: If task doesn't exist
        UnauthorizedError: If user doesn't own the task
    """
    start_time = time.time()

    # Check user has tasks
    user_tasks = _mock_task_storage.get(user_id, {})

    # Find task
    if task_id not in user_tasks:
        raise TaskNotFoundError(f"Task {task_id} not found")

    # Delete task
    del user_tasks[task_id]


async def mock_update_task(user_id: UUID, task_id: UUID, new_title: str) -> Dict[str, Any]:
    """
    Mock implementation of update_task MCP tool.

    Updates a task's title.

    Args:
        user_id: Authenticated user ID (must own the task)
        task_id: Task ID to update
        new_title: New task title

    Returns:
        Updated task dict

    Raises:
        TaskNotFoundError: If task doesn't exist
        UnauthorizedError: If user doesn't own the task
        ValidationError: If new_title is empty
    """
    start_time = time.time()

    # Validation
    if not new_title or not new_title.strip():
        raise ValidationError("Title cannot be empty")

    # Check user has tasks
    user_tasks = _mock_task_storage.get(user_id, {})

    # Find task
    if task_id not in user_tasks:
        raise TaskNotFoundError(f"Task {task_id} not found")

    task = user_tasks[task_id]

    # Update task
    task["title"] = new_title.strip()
    task["updated_at"] = datetime.now(timezone.utc).isoformat()

    return task


# Utility function to clear mock storage (for testing)
def clear_mock_storage():
    """Clear all mock task storage. Useful for testing."""
    _mock_task_storage.clear()
