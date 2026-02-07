
# Quickstart Guide: MCP Server, Tools & Persistence Layer

**Date**: 2026-02-07
**Feature**: 005-mcp-server-tools
**Audience**: Developers implementing MCP tools and integrating with Spec-4

## Overview

MCP tools are async Python functions that wrap existing TaskService business logic from Spec-1. They provide a stateless interface for the AI agent (Spec-4) to perform task operations with database persistence.

**Key Characteristics**:
- **Stateless**: No in-memory state; all data persisted to database
- **Thin Wrappers**: Call TaskService methods only (no business logic duplication)
- **Direct Integration**: Imported as Python functions by Spec-4 agent
- **Authorization**: Validate user ownership at TaskService layer

## Architecture

### Component Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    Spec-4: AI Chat Agent                        │
│  - Intent classification                                        │
│  - Tool selection (tool_mapper.py)                              │
│  - Response formatting                                          │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     │ Direct Python import
                     │ await add_task(user_id, title, db)
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Spec-5: MCP Tools (NEW)                      │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  MCP Tool (e.g., add_task)                                 │ │
│  │  1. Validate inputs (user_id UUID, title 1-500 chars)     │ │
│  │  2. Create TaskService instance                            │ │
│  │  3. Call service.create_task(user_id, TaskCreate, auth)   │ │
│  │  4. Return task.model_dump()                               │ │
│  └──────────────────┬─────────────────────────────────────────┘ │
└─────────────────────┼───────────────────────────────────────────┘
                      │
                      │ Reuse existing business logic
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│              Spec-1: TaskService & Database                     │
│  - Business logic (CRUD operations)                             │
│  - Authorization (user_id validation)                           │
│  - TaskRepository (database queries)                            │
│  - Database transactions                                        │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     │ SQLModel ORM queries
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                    PostgreSQL Database                          │
│  - tasks table (id, user_id, title, is_completed, timestamps)  │
│  - Indexed by user_id and id                                    │
│  - Transaction-based consistency                                │
└─────────────────────────────────────────────────────────────────┘
```

## Module Structure & Implementation

```
backend/src/mcp/
├── __init__.py                    # Module exports
├── tools/
│   ├── add_task.py                # Create task
│   ├── list_tasks.py              # Retrieve tasks
│   ├── complete_task.py           # Mark complete
│   ├── delete_task.py             # Delete task
│   └── update_task.py             # Update task
├── errors.py                      # Error classes
└── schemas.py                     # Input validation (optional)
```

## Integration with Spec-4

### Steps
1. Implement all 5 MCP tools in `backend/src/mcp/tools/`
2. Update `backend/src/agent/tool_mapper.py` imports (replace mocks)
3. Add db parameter to agent functions
4. Run Spec-4 agent tests with real tools
5. Remove mock tools directory

## Next Steps

1. ✅ Phase 0 & 1 Complete: Design artifacts ready
2. **Generate Tasks**: Run `/sp.tasks`
3. **Implement**: Follow tasks.md
4. **Integrate**: Connect with Spec-4
5. **Validate**: End-to-end testing

---

**Status**: Design complete, ready for `/sp.tasks`
