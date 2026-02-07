# Data Model: MCP Server, Tools & Persistence Layer

**Date**: 2026-02-07
**Feature**: 005-mcp-server-tools
**Phase**: Phase 1 - Design & Architecture

## Overview

This document defines the data structures used by MCP tools. **Important**: MCP tools reuse the existing Task model from Spec-1 and wrap existing TaskService business logic. No new database tables or models are created.

## Existing Entities (from Spec-1)

### Task

**Source**: `backend/src/models/task.py` (already exists from Spec-1)

**Purpose**: Represents a user's task item in the database.

**Schema** (reference only, no changes):
```python
class Task(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True, nullable=False)
    title: str = Field(max_length=500, nullable=False)
    description: Optional[str] = Field(default=None, max_length=1000, nullable=True)
    is_completed: bool = Field(default=False, nullable=False)
    completed_at: Optional[datetime] = Field(default=None, nullable=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
```

**Indexes**:
- Primary key: `id` (UUID)
- Foreign key: `user_id` → users.id (indexed)
- Query optimization: `is_completed` (for filtering)

**Source**: Spec-1 (Backend API & Database)

---

## MCP Tool Schemas (New)

### AddTaskInput

**Purpose**: Input validation for add_task tool.

**Schema**:
```python
from pydantic import BaseModel, Field
from uuid import UUID

class AddTaskInput(BaseModel):
    user_id: UUID = Field(..., description="Authenticated user ID")
    title: str = Field(..., min_length=1, max_length=500, description="Task title")
```

**Validation Rules**:
- `user_id`: Must be valid UUID
- `title`: Non-empty, max 500 characters

---

### ListTasksInput

**Purpose**: Input validation for list_tasks tool.

**Schema**:
```python
class ListTasksInput(BaseModel):
    user_id: UUID = Field(..., description="Authenticated user ID")
    filter: Optional[str] = Field("all", pattern="^(all|pending|completed)$", description="Task filter")
```

**Validation Rules**:
- `user_id`: Must be valid UUID
- `filter`: Must be "all", "pending", or "completed"

---

### CompleteTaskInput

**Purpose**: Input validation for complete_task tool.

**Schema**:
```python
class CompleteTaskInput(BaseModel):
    user_id: UUID = Field(..., description="Authenticated user ID (must own task)")
    task_id: UUID = Field(..., description="Task ID to complete")
```

**Validation Rules**:
- `user_id`: Must be valid UUID
- `task_id`: Must be valid UUID
- Ownership validation: Tool verifies user owns task

---

### DeleteTaskInput

**Purpose**: Input validation for delete_task tool.

**Schema**:
```python
class DeleteTaskInput(BaseModel):
    user_id: UUID = Field(..., description="Authenticated user ID (must own task)")
    task_id: UUID = Field(..., description="Task ID to delete")
```

**Validation Rules**:
- `user_id`: Must be valid UUID
- `task_id`: Must be valid UUID
- Ownership validation: Tool verifies user owns task

---

### UpdateTaskInput

**Purpose**: Input validation for update_task tool.

**Schema**:
```python
class UpdateTaskInput(BaseModel):
    user_id: UUID = Field(..., description="Authenticated user ID (must own task)")
    task_id: UUID = Field(..., description="Task ID to update")
    new_title: str = Field(..., min_length=1, max_length=500, description="New task title")
```

**Validation Rules**:
- `user_id`: Must be valid UUID
- `task_id`: Must be valid UUID
- `new_title`: Non-empty, max 500 characters
- Ownership validation: Tool verifies user owns task

---

## Error Classes (New)

### MCPToolError (Base)

**Purpose**: Base exception class for all MCP tool errors.

**Schema**:
```python
class MCPToolError(Exception):
    """Base class for MCP tool errors."""
    def __init__(self, message: str, details: Optional[dict] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)
```

---

### TaskNotFoundError

**Purpose**: Task does not exist or user doesn't own it.

**Usage**: Raised when task_id not found in user's tasks

**Schema**:
```python
class TaskNotFoundError(MCPToolError):
    """Task not found or unauthorized access."""
    pass
```

---

### ValidationError

**Purpose**: Input validation failed (empty title, invalid UUID, etc.).

**Usage**: Raised when tool inputs don't meet schema requirements

**Schema**:
```python
class ValidationError(MCPToolError):
    """Input validation failed."""
    pass
```

---

### UnauthorizedError

**Purpose**: User not authorized for operation (cross-user access attempt).

**Usage**: Raised when user_id doesn't own the referenced task

**Schema**:
```python
class UnauthorizedError(MCPToolError):
    """User not authorized for this operation."""
    pass
```

---

### DatabaseError

**Purpose**: Database operation failed (connection, transaction, constraint).

**Usage**: Raised when database persistence fails

**Schema**:
```python
class DatabaseError(MCPToolError):
    """Database operation failed."""
    pass
```

---

## Tool Result Format

### Success Response

**Format**: Python dict containing task data

```python
{
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "user_id": "123e4567-e89b-12d3-a456-426614174000",
    "title": "buy milk",
    "description": None,
    "is_completed": False,
    "completed_at": None,
    "created_at": "2026-02-07T10:00:00Z",
    "updated_at": "2026-02-07T10:00:00Z"
}
```

**For list_tasks**: List of task dicts

---

### Error Response

**Format**: Exception raised with error class and message

```python
raise TaskNotFoundError("Task not found: 550e8400-e29b-41d4-a716-446655440000")
```

**Agent Handling**: Spec-4 agent catches exception, extracts error class name and message, translates to user-friendly text.

---

## Data Flow

### Tool Invocation Flow

```
Spec-4 Agent (tool_mapper.py)
    ↓ (direct Python function call)
MCP Tool (e.g., add_task)
    ↓ (validate inputs)
TaskService (from Spec-1)
    ↓ (execute business logic)
TaskRepository (from Spec-1)
    ↓ (database query)
PostgreSQL Database
    ↓ (persist data)
TaskRepository (return Task)
    ↓
TaskService (return Task)
    ↓
MCP Tool (return task.model_dump())
    ↓
Spec-4 Agent (format response for user)
```

### Authorization Flow

```
MCP Tool receives user_id and task_id
    ↓
TaskService.complete_task(user_id, task_id, authenticated_user_id=str(user_id))
    ↓
TaskService validates: user_id == authenticated_user_id ✓
    ↓
TaskRepository queries: WHERE id = task_id AND user_id = user_id
    ↓
If no rows: raise HTTPException(404)
    ↓
MCP Tool catches HTTPException → raise TaskNotFoundError
    ↓
Spec-4 Agent catches TaskNotFoundError → user-friendly message
```

---

## Reused Components (No Changes)

- **Task Model**: `backend/src/models/task.py` (Spec-1)
- **TaskService**: `backend/src/services/task_service.py` (Spec-1)
- **TaskRepository**: `backend/src/repositories/task_repository.py` (Spec-1)
- **Database Session**: `backend/src/database.py` (Spec-1)

**Constitutional Compliance**: No duplication of business logic; MCP tools wrap only.

---

## Dependencies

- **Spec-1**: Task model, TaskService, TaskRepository, database infrastructure
- **Spec-4**: Consumer of MCP tools (replaces mocks with real tools)
- **Spec-2**: user_id from JWT validation (upstream)

---

## Notes

- All schemas use Pydantic for validation
- MCP tools are stateless (no in-memory state)
- Tools reuse existing TaskService (constitutional requirement)
- Error classes match Spec-4 agent expectations
- Database transactions handled by TaskService/TaskRepository
