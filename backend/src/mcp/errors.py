"""
MCP Tool Error Classes

Structured error types for MCP tool operations.
Designed for consumption by Spec-4 AI agent.
"""

from typing import Optional


class MCPToolError(Exception):
    """Base class for MCP tool errors."""

    def __init__(self, message: str, details: Optional[dict] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class TaskNotFoundError(MCPToolError):
    """Task not found or unauthorized access."""

    pass


class ValidationError(MCPToolError):
    """Input validation failed."""

    pass


class UnauthorizedError(MCPToolError):
    """User not authorized for this operation."""

    pass


class DatabaseError(MCPToolError):
    """Database operation failed."""

    pass
