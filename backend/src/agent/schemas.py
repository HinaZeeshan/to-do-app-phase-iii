"""
Pydantic schemas for AI Chat Agent.

Defines data models for agent request/response and internal data structures.
All schemas follow Phase III constitutional requirements for stateless,
deterministic agent behavior.
"""

from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class Intent(str, Enum):
    """User intent classifications for task management operations."""

    CREATE_TASK = "create_task"
    LIST_TASKS = "list_tasks"
    COMPLETE_TASK = "complete_task"
    DELETE_TASK = "delete_task"
    UPDATE_TASK = "update_task"
    CLARIFICATION_NEEDED = "clarification_needed"
    UNKNOWN = "unknown"


class ConversationMessage(BaseModel):
    """Single message in conversation history."""

    role: str = Field(..., pattern="^(user|assistant|system)$")
    content: str = Field(..., min_length=1)
    timestamp: Optional[str] = None  # ISO 8601 format

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "role": "user",
                "content": "remind me to buy milk",
                "timestamp": "2026-02-07T10:00:00Z",
            }
        }
    )


class AgentRequest(BaseModel):
    """Input schema for agent invocation."""

    user_id: UUID = Field(..., description="Authenticated user ID from JWT")
    message: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="Current user message",
    )
    conversation_history: List[ConversationMessage] = Field(
        default_factory=list,
        description="Previous messages in this conversation (max 50)",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "message": "remind me to buy milk",
                "conversation_history": [
                    {"role": "user", "content": "what are my tasks?"},
                    {"role": "assistant", "content": "You don't have any tasks yet."},
                ],
            }
        }
    )


class ToolInvocation(BaseModel):
    """Record of a single MCP tool call."""

    tool_name: str = Field(..., description="MCP tool that was called")
    parameters: Dict[str, Any] = Field(..., description="Parameters passed to tool")
    result: Optional[Any] = Field(None, description="Tool response (success) - can be dict, list, or None")
    error: Optional[str] = Field(None, description="Error message (if tool failed)")
    duration_ms: Optional[int] = Field(
        None, description="Tool execution time in milliseconds"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "tool_name": "add_task",
                "parameters": {
                    "user_id": "123e4567-e89b-12d3-a456-426614174000",
                    "title": "buy milk",
                },
                "result": {
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                    "title": "buy milk",
                    "is_completed": False,
                },
                "error": None,
                "duration_ms": 45,
            }
        }
    )


class AgentResponse(BaseModel):
    """Output schema for agent invocation."""

    response_text: str = Field(..., min_length=1, description="User-facing response message")
    tool_invocations: List[ToolInvocation] = Field(
        default_factory=list,
        description="MCP tools called during this request",
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional context (intent recognized, processing time, etc.)",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "response_text": "I've added 'buy milk' to your tasks",
                "tool_invocations": [
                    {
                        "tool_name": "add_task",
                        "parameters": {
                            "user_id": "123e4567-e89b-12d3-a456-426614174000",
                            "title": "buy milk",
                        },
                        "result": {
                            "id": "550e8400-e29b-41d4-a716-446655440000",
                            "title": "buy milk",
                            "is_completed": False,
                        },
                        "error": None,
                        "duration_ms": 45,
                    }
                ],
                "metadata": {"intent": "CREATE_TASK", "processing_time_ms": 312},
            }
        }
    )


class IntentClassificationResult(BaseModel):
    """Internal result from intent classification."""

    intent: Intent = Field(..., description="Recognized intent")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score (0.0-1.0)")
    extracted_params: Dict[str, Any] = Field(
        default_factory=dict,
        description="Parameters extracted from user message (e.g., task_title, task_id)",
    )
    clarification_question: Optional[str] = Field(
        None,
        description="Question to ask user if intent is ambiguous",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "intent": "CREATE_TASK",
                "confidence": 0.95,
                "extracted_params": {"task_title": "buy milk"},
                "clarification_question": None,
            }
        }
    )
