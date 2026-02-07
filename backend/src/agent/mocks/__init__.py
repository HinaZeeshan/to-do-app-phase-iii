"""Mock MCP tools for agent development and testing."""

from .mock_mcp_tools import (
    mock_add_task,
    mock_complete_task,
    mock_delete_task,
    mock_list_tasks,
    mock_update_task,
)

__all__ = [
    "mock_add_task",
    "mock_list_tasks",
    "mock_complete_task",
    "mock_delete_task",
    "mock_update_task",
]
