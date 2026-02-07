# Data Model: AI Chat Agent & Conversation Logic

**Date**: 2026-02-07
**Feature**: 004-ai-chat-agent
**Phase**: Phase 1 - Design & Architecture

## Overview

This document defines the data structures used by the AI Chat Agent. **Important**: The agent does not persist data directly; it only receives input, processes it, and returns output. All persistence is handled by Spec-5 (MCP Server & Chat Infrastructure).

## Core Entities

### AgentRequest

Input to the agent's `run_agent()` function.

**Purpose**: Encapsulates all information needed for the agent to process a user message.

**Schema**:
```python
from uuid import UUID
from typing import List, Optional
from pydantic import BaseModel, Field

class ConversationMessage(BaseModel):
    """Single message in conversation history."""
    role: str = Field(..., pattern="^(user|assistant|system)$")
    content: str = Field(..., min_length=1)
    timestamp: Optional[str] = None  # ISO 8601 format

class AgentRequest(BaseModel):
    """Input schema for agent invocation."""
    user_id: UUID = Field(..., description="Authenticated user ID from JWT")
    message: str = Field(..., min_length=1, max_length=2000, description="Current user message")
    conversation_history: List[ConversationMessage] = Field(
        default_factory=list,
        description="Previous messages in this conversation (max 50)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "message": "remind me to buy milk",
                "conversation_history": [
                    {"role": "user", "content": "what are my tasks?"},
                    {"role": "assistant", "content": "You don't have any tasks yet."}
                ]
            }
        }
```

**Validation Rules**:
- `user_id`: Must be valid UUID (authenticated from JWT)
- `message`: Non-empty, max 2000 characters
- `conversation_history`: Max 50 messages (truncated by agent if exceeded)

**Source**: Provided by Spec-5 chat infrastructure on each request

---

### AgentResponse

Output from the agent's `run_agent()` function.

**Purpose**: Contains the agent's response to the user and metadata about tool invocations.

**Schema**:
```python
from typing import List, Optional, Dict, Any

class ToolInvocation(BaseModel):
    """Record of a single MCP tool call."""
    tool_name: str = Field(..., description="MCP tool that was called")
    parameters: Dict[str, Any] = Field(..., description="Parameters passed to tool")
    result: Optional[Dict[str, Any]] = Field(None, description="Tool response (success)")
    error: Optional[str] = Field(None, description="Error message (if tool failed)")
    duration_ms: Optional[int] = Field(None, description="Tool execution time in milliseconds")

class AgentResponse(BaseModel):
    """Output schema for agent invocation."""
    response_text: str = Field(..., min_length=1, description="User-facing response message")
    tool_invocations: List[ToolInvocation] = Field(
        default_factory=list,
        description="MCP tools called during this request"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional context (intent recognized, processing time, etc.)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "response_text": "I've added 'buy milk' to your tasks",
                "tool_invocations": [
                    {
                        "tool_name": "add_task",
                        "parameters": {"user_id": "123e4567-e89b-12d3-a456-426614174000", "title": "buy milk"},
                        "result": {"id": "550e8400-e29b-41d4-a716-446655440000", "title": "buy milk", "is_completed": False},
                        "error": None,
                        "duration_ms": 45
                    }
                ],
                "metadata": {
                    "intent": "CREATE_TASK",
                    "processing_time_ms": 312
                }
            }
        }
```

**Fields**:
- `response_text`: Conversational message returned to user
- `tool_invocations`: Audit trail of MCP tools called (for logging, debugging)
- `metadata`: Intent recognized, processing time, any warnings

**Destination**: Returned to Spec-5 chat infrastructure; response_text displayed to user

---

### Intent

Enumeration of recognized user intents.

**Purpose**: Classify user messages into actionable categories for tool mapping.

**Schema**:
```python
from enum import Enum

class Intent(str, Enum):
    """User intent classifications."""
    CREATE_TASK = "create_task"
    LIST_TASKS = "list_tasks"
    COMPLETE_TASK = "complete_task"
    DELETE_TASK = "delete_task"
    UPDATE_TASK = "update_task"
    CLARIFICATION_NEEDED = "clarification_needed"
    UNKNOWN = "unknown"
```

**Intent Descriptions**:
- `CREATE_TASK`: User wants to add a new task (keywords: add, create, remind, remember)
- `LIST_TASKS`: User wants to view tasks (keywords: show, list, what, pending, completed)
- `COMPLETE_TASK`: User wants to mark task as done (keywords: done, complete, finished, mark)
- `DELETE_TASK`: User wants to remove a task (keywords: delete, remove, cancel)
- `UPDATE_TASK`: User wants to modify task details (keywords: change, update, rename, modify)
- `CLARIFICATION_NEEDED`: Ambiguous input requiring follow-up question
- `UNKNOWN`: Unrecognized intent (fallback response)

**Usage**: Internal to agent; mapped to MCP tool selection

---

### ToolInvocation

Record of a single MCP tool call (embedded in AgentResponse).

**Purpose**: Audit trail and debugging information for tool usage.

**Schema**: See `ToolInvocation` under `AgentResponse` above.

**Fields**:
- `tool_name`: MCP tool identifier (e.g., "add_task", "list_tasks")
- `parameters`: Arguments passed to tool (includes user_id and extracted params)
- `result`: Tool response on success (task object, list of tasks, etc.)
- `error`: Error message if tool failed (e.g., "Task not found")
- `duration_ms`: Tool execution latency (for performance monitoring)

**Source**: Populated by `tool_mapper.py` after MCP tool execution

---

### ConversationMessage

Single message in conversation history (embedded in AgentRequest).

**Purpose**: Represent a user or assistant message for context-aware intent recognition.

**Schema**: See `ConversationMessage` under `AgentRequest` above.

**Fields**:
- `role`: "user" | "assistant" | "system" (OpenAI format)
- `content`: Message text
- `timestamp`: Optional ISO 8601 timestamp (for display, not used by agent logic)

**Source**: Provided by Spec-5 from conversation storage

---

## Internal Data Structures

### IntentClassificationResult

Internal result from intent classifier.

**Purpose**: Capture intent, confidence, and extracted parameters from user message.

**Schema**:
```python
from typing import Optional, Dict, Any

class IntentClassificationResult(BaseModel):
    """Internal result from intent classification."""
    intent: Intent = Field(..., description="Recognized intent")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score (0.0-1.0)")
    extracted_params: Dict[str, Any] = Field(
        default_factory=dict,
        description="Parameters extracted from user message (e.g., task_title, task_id)"
    )
    clarification_question: Optional[str] = Field(
        None,
        description="Question to ask user if intent is ambiguous"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "intent": "CREATE_TASK",
                "confidence": 0.95,
                "extracted_params": {"task_title": "buy milk"},
                "clarification_question": None
            }
        }
```

**Usage**: Passed from `IntentClassifier` to `ToolMapper` for tool selection

---

### MCPToolSchema

Schema definition for MCP tool function calling.

**Purpose**: Define tool signatures for OpenAI function calling.

**Schema**:
```python
# Example: add_task tool schema
add_task_schema = {
    "type": "function",
    "function": {
        "name": "add_task",
        "description": "Create a new task for the authenticated user",
        "parameters": {
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "string",
                    "format": "uuid",
                    "description": "Authenticated user ID"
                },
                "title": {
                    "type": "string",
                    "minLength": 1,
                    "maxLength": 500,
                    "description": "Task title or description"
                }
            },
            "required": ["user_id", "title"]
        }
    }
}
```

**Usage**: Passed to OpenAI API for function calling; defines tool interface

---

## Data Flow

### Request Flow
1. **Spec-5 Chat Infrastructure** receives user message
2. Spec-5 retrieves conversation history from database
3. Spec-5 constructs `AgentRequest` (user_id, message, conversation_history)
4. Spec-5 invokes agent's `run_agent()` function
5. **Agent** processes request:
   - Classifies intent → `IntentClassificationResult`
   - Maps intent to MCP tool → `ToolInvocation`
   - Executes MCP tool → tool result or error
   - Formats response → `AgentResponse`
6. Agent returns `AgentResponse` to Spec-5
7. Spec-5 persists assistant message to database
8. Spec-5 returns `response_text` to user

### Data Persistence
- **Agent**: No persistence (stateless)
- **Spec-5**: Persists conversation messages (ConversationMessage) to database
- **MCP Tools**: Persist task data via TaskService and database

---

## Validation Rules

### Input Validation (AgentRequest)
- `user_id`: Must be valid UUID from authenticated JWT
- `message`: Non-empty, max 2000 characters (protects against prompt injection)
- `conversation_history`: Max 50 messages (agent truncates if exceeded)

### Output Validation (AgentResponse)
- `response_text`: Must be non-empty
- `tool_invocations`: May be empty (for unknown intents)
- `metadata`: Optional debugging information

### Parameter Extraction Validation
- `task_title`: Non-empty string (extracted from user message)
- `task_id`: Valid UUID (extracted from user message or conversation context)
- `filter`: Optional string for list_tasks (e.g., "completed", "pending")

---

## Error Handling

### Error Types
- **ValidationError**: Invalid input (empty message, malformed UUID)
- **IntentClassificationError**: Unable to classify intent
- **ToolInvocationError**: MCP tool execution failed
- **UnauthorizedError**: User_id mismatch or permission denied

### Error Response Format
```python
{
    "response_text": "I'm having trouble with that request. Please try again.",
    "tool_invocations": [
        {
            "tool_name": "add_task",
            "parameters": {"user_id": "...", "title": "..."},
            "result": None,
            "error": "ValidationError: Title cannot be empty",
            "duration_ms": 10
        }
    ],
    "metadata": {
        "intent": "CREATE_TASK",
        "error_type": "ValidationError"
    }
}
```

---

## Relationships

```
AgentRequest
  ├── user_id (UUID) ──────────────────────┐
  ├── message (str)                        │
  └── conversation_history                 │
        └── ConversationMessage[]          │
              ├── role                     │
              ├── content                  │
              └── timestamp                │
                                           │
Agent Processing (stateless)              │
  ├── Intent Classification               │
  │     └── IntentClassificationResult    │
  │           ├── intent (Intent enum)    │
  │           ├── confidence               │
  │           ├── extracted_params         │
  │           └── clarification_question   │
  │                                        │
  ├── Tool Mapping                        │
  │     └── MCPToolSchema                 │
  │                                        │
  ├── MCP Tool Invocation ────────────────┤ (user_id passed to all tools)
  │     └── ToolInvocation                │
  │           ├── tool_name                │
  │           ├── parameters ──────────────┘
  │           ├── result (from Spec-5)
  │           ├── error
  │           └── duration_ms
  │
  └── Response Formatting
        └── AgentResponse
              ├── response_text (to user)
              ├── tool_invocations[]
              └── metadata
```

---

## Dependencies

- **Spec-5**: Provides conversation persistence and MCP tool implementations
- **Spec-2**: Provides authenticated user_id (via JWT)
- **Spec-1**: Provides Task model structure (for tool results)

---

## Notes

- All schemas use Pydantic for validation and serialization
- Agent is stateless: no data persisted by agent itself
- Conversation history format matches OpenAI API requirements
- Tool invocations logged for audit and debugging
- Error messages user-friendly (no technical details exposed)
