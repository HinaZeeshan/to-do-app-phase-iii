# Research: MCP Server, Tools & Persistence Layer

**Date**: 2026-02-07
**Feature**: 005-mcp-server-tools
**Phase**: Phase 0 - Research & Technology Selection

## R1: Official MCP SDK Integration

### Research Question
How to integrate Official MCP SDK with Python 3.11 FastAPI backend?

### Findings

**MCP SDK Approach**:
For this project, we implement MCP tools as simple Python async functions that can be imported directly by the Spec-4 agent. The "MCP Server" refers to the module structure and tool organization, not a separate server process.

**Integration Pattern**:
```python
# MCP Tool Implementation
async def add_task(user_id: UUID, title: str, db: AsyncSession) -> dict:
    service = TaskService(db)
    task_data = TaskCreate(title=title)
    task = await service.create_task(user_id, task_data, str(user_id))
    return task.model_dump()
```

**Rationale**:
- Same-process invocation (no network overhead)
- Async/await compatible with FastAPI
- Direct imports from Spec-4 agent
- Stateless by design (no server state)

### Decision

**Chosen Approach**: Implement MCP tools as async Python functions; no separate server process.

**Rationale**:
1. Minimal latency (<50ms overhead achievable)
2. Simple integration with Spec-4 agent
3. Stateless architecture guaranteed
4. Reuses existing database session management

**Alternatives Considered**:
- **Separate MCP server process**: Rejected due to network overhead and complexity
- **HTTP-based tools**: Rejected due to serialization overhead

### Implementation Notes
- Tools in `backend/src/mcp/tools/` as async functions
- Spec-4 agent imports tools directly
- Database session passed as parameter

---

## R2: MCP Tool Schema Definition

### Research Question
What is the MCP tool schema format and how to define tool input/output contracts?

### Findings

**Schema Format**:
```python
# Input validation with Pydantic
class AddTaskInput(BaseModel):
    user_id: UUID
    title: str = Field(min_length=1, max_length=500)

# Tool implementation
async def add_task(user_id: UUID, title: str, db: AsyncSession) -> dict:
    # Validate inputs
    input_data = AddTaskInput(user_id=user_id, title=title)
    # Execute operation
    ...
```

### Decision

**Chosen Approach**: Python type hints + Pydantic validation for input schemas; return dict for output.

**Rationale**:
1. Matches existing backend patterns
2. Type safety with runtime validation
3. Clear contracts via type hints
4. Compatible with Spec-4 agent expectations

**Alternatives Considered**:
- **JSON Schema**: Rejected, less Pythonic
- **dataclasses**: Rejected, no validation

### Implementation Notes
- Define schemas in `backend/src/mcp/schemas.py`
- Reuse Task model from Spec-1
- Return task.model_dump() for serialization

---

## R3: TaskService Integration Pattern

### Research Question
How should MCP tools invoke existing TaskService methods?

### Findings

**TaskService Interface** (from Spec-1):
- `create_task(user_id, task_data, authenticated_user_id)`
- `list_tasks(user_id, authenticated_user_id)`
- `complete_task(user_id, task_id, authenticated_user_id)`
- `delete_task(user_id, task_id, authenticated_user_id)`
- `update_task(user_id, task_id, task_data, authenticated_user_id)`

**Authorization**: TaskService validates user_id == authenticated_user_id

**Wrapper Pattern**:
```python
async def add_task(user_id: UUID, title: str, db: AsyncSession) -> dict:
    # Create service
    service = TaskService(db)

    # Call service (pass user_id as both param and auth)
    task_data = TaskCreate(title=title)
    task = await service.create_task(user_id, task_data, str(user_id))

    # Return serialized
    return task.model_dump()
```

### Decision

**Chosen Approach**: Thin wrapper - validate inputs, call TaskService, return result.

**Rationale**:
1. No business logic duplication (constitutional requirement)
2. TaskService has all CRUD logic
3. Authorization already implemented in TaskService
4. MCP tools add only: input validation, result serialization

**Alternatives Considered**:
- **Direct database access**: Rejected, violates "no duplication" principle

### Implementation Notes
- MCP tools trust user_id from agent (agent is authenticated upstream)
- Pass user_id as both parameter and authenticated_user_id to TaskService
- Catch TaskService HTTPExceptions → convert to MCP errors

---

## R4: Spec-4 Agent Integration

### Research Question
How will Spec-4 AI agent invoke MCP tools?

### Findings

**Current Spec-4 Implementation**:
- Mock tools in `backend/src/agent/mocks/mock_mcp_tools.py`
- Tool invocation in `backend/src/agent/tool_mapper.py`
- Agent expects: `await mock_add_task(user_id, title)`

**Integration Changes**:
```python
# tool_mapper.py - Before
from .mocks.mock_mcp_tools import mock_add_task, mock_list_tasks, ...

# tool_mapper.py - After
from src.mcp.tools import add_task, list_tasks, complete_task, delete_task, update_task

# Pass database session
result = await add_task(user_id, title, db)
```

### Decision

**Chosen Approach**: Replace mock imports with real tool imports in Spec-4 tool_mapper.py.

**Rationale**:
1. Minimal changes to Spec-4 code
2. Function signatures match mock interface
3. Database session passed from agent
4. Error handling already implemented in agent

**Alternatives Considered**:
- **New integration layer**: Rejected, unnecessary complexity

### Implementation Notes
- Update tool_mapper.py imports
- Agent gets database session from FastAPI dependency injection
- Pass db session to all tool calls

---

## R5: Error Handling Strategy

### Research Question
How should MCP tools structure error responses for agent consumption?

### Findings

**Error Classes**:
```python
class TaskNotFoundError(Exception): pass
class ValidationError(Exception): pass
class UnauthorizedError(Exception): pass
class DatabaseError(Exception): pass
```

**Agent Error Handling** (from Spec-4):
Agent already catches these error types and translates to user-friendly messages.

### Decision

**Chosen Approach**: Define 4 error classes matching Spec-4 expectations; raise from tools.

**Rationale**:
1. Spec-4 agent already handles these errors
2. No changes needed to agent error handling
3. Consistent with mock tool errors

**Alternatives Considered**:
- **Different error structure**: Rejected, requires Spec-4 changes

### Implementation Notes
- Define in `backend/src/mcp/errors.py`
- Import in all tool modules
- Match exact names from Spec-4 mocks

---

## Summary

### Key Decisions

1. **MCP Tools as Functions**: Async Python functions, not separate server process
2. **Direct Integration**: Spec-4 agent imports tools directly (replaces mocks)
3. **TaskService Wrapper**: Thin wrappers, no business logic duplication
4. **Error Classes**: 4 structured errors matching Spec-4 expectations
5. **Stateless Architecture**: Tools persist to database, no in-memory state

### Dependencies
- No new external dependencies
- Reuse TaskService, database, SQLModel from Spec-1
- Match Spec-4 agent error handling

### Risks Mitigated
- No separate process → minimal latency
- Thin wrappers → no duplication
- Direct imports → simple integration
- Database-backed → stateless guaranteed

### Next Phase
Proceed to Phase 1: Design & Architecture (data-model.md, contracts/, quickstart.md)
