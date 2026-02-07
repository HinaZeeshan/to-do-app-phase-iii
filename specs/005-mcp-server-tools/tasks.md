# Tasks: MCP Server, Tools & Persistence Layer

**Input**: Design documents from `/specs/005-mcp-server-tools/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are NOT explicitly requested in specification but are essential for validating tool behavior and authorization.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each tool.

## Format: `- [ ] [ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/src/`, `backend/tests/`
- Paths assume web app structure per plan.md

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: MCP module initialization and shared components

- [X] T001 Create MCP module directory structure at backend/src/mcp/ with __init__.py
- [X] T002 [P] Create error classes file at backend/src/mcp/errors.py with MCPToolError, TaskNotFoundError, ValidationError, UnauthorizedError, DatabaseError
- [X] T003 [P] Create schemas file at backend/src/mcp/schemas.py with input validation models (AddTaskInput, ListTasksInput, etc.)
- [X] T004 Create tools directory at backend/src/mcp/tools/__init__.py with tool exports

## Phase 2: User Story 1 - AI Agent Creates Task via MCP Tool (Priority: P1)

**Story Goal**: Enable AI agent to create tasks via add_task MCP tool with database persistence

**Independent Test Criteria**:
- Call add_task(user_id, title, db) → task persisted to database
- Verify task has generated ID, correct user_id, title, is_completed=False
- Tool returns complete task dict

### Implementation Tasks

- [X] T005 [US1] Implement add_task tool at backend/src/mcp/tools/add_task.py wrapping TaskService.create_task
- [X] T006 [US1] Add input validation in add_task tool (user_id UUID, title 1-500 chars non-empty)
- [X] T007 [US1] Add TaskService invocation in add_task tool (pass user_id, TaskCreate, authenticated_user_id)
- [X] T008 [US1] Add error handling in add_task tool (catch HTTPException → raise ValidationError/DatabaseError)
- [X] T009 [US1] Return task.model_dump() from add_task tool
- [X] T010 [US1] Create unit test file at backend/tests/mcp/test_add_task.py
- [X] T011 [US1] Test US1 scenario 1 (valid inputs → task persisted and returned)
- [X] T012 [US1] Test US1 scenario 2 (empty title → ValidationError)
- [X] T013 [US1] Test US1 scenario 3 (invalid user_id format → ValidationError)
- [X] T014 [US1] Test US1 scenario 4 (title exceeds 500 chars → ValidationError)
- [X] T015 [US1] Test US1 scenario 5 (database unavailable → DatabaseError)

## Phase 3: User Story 2 - AI Agent Retrieves Task List via MCP Tool (Priority: P1)

**Story Goal**: Enable AI agent to retrieve task lists via list_tasks MCP tool with filtering

**Independent Test Criteria**:
- Create 5 tasks (3 pending, 2 completed)
- Call list_tasks(user_id, "pending", db) → returns exactly 3 pending tasks
- Verify results sorted by created_at descending

### Implementation Tasks

- [X] T016 [US2] Implement list_tasks tool at backend/src/mcp/tools/list_tasks.py wrapping TaskService.list_tasks
- [X] T017 [US2] Add input validation in list_tasks tool (user_id UUID, filter enum validation)
- [X] T018 [US2] Add TaskService invocation in list_tasks tool (retrieve all user tasks)
- [X] T019 [US2] Implement filtering logic in list_tasks tool (filter by is_completed based on filter parameter)
- [X] T020 [US2] Add sorting logic in list_tasks tool (sort by created_at descending)
- [X] T021 [US2] Return list of task.model_dump() dicts from list_tasks tool
- [X] T022 [US2] Create unit test file at backend/tests/mcp/test_list_tasks.py
- [X] T023 [US2] Test US2 scenario 1 (filter="all" → returns all 5 tasks sorted)
- [X] T024 [US2] Test US2 scenario 2 (filter="pending" → returns 3 pending tasks)
- [X] T025 [US2] Test US2 scenario 3 (filter="completed" → returns 2 completed tasks)
- [X] T026 [US2] Test US2 scenario 4 (no tasks → returns empty list, not error)
- [X] T027 [US2] Test US2 scenario 5 (invalid user_id → ValidationError)

## Phase 4: User Story 3 - AI Agent Marks Task Complete via MCP Tool (Priority: P2)

**Story Goal**: Enable AI agent to mark tasks complete via complete_task MCP tool

**Independent Test Criteria**:
- Create pending task
- Call complete_task(user_id, task_id, db) → task marked complete
- Verify is_completed=True, completed_at timestamp set

### Implementation Tasks

- [X] T028 [US3] Implement complete_task tool at backend/src/mcp/tools/complete_task.py wrapping TaskService.complete_task
- [X] T029 [US3] Add input validation in complete_task tool (user_id UUID, task_id UUID)
- [X] T030 [US3] Add TaskService invocation in complete_task tool (marks task complete with authorization)
- [X] T031 [US3] Add error handling in complete_task tool (catch HTTPException 404 → TaskNotFoundError, 403 → UnauthorizedError)
- [X] T032 [US3] Return updated task.model_dump() from complete_task tool
- [X] T033 [US3] Create unit test file at backend/tests/mcp/test_complete_task.py
- [X] T034 [US3] Test US3 scenario 1 (user owns pending task → marked complete with timestamp)
- [X] T035 [US3] Test US3 scenario 2 (task_id doesn't exist → TaskNotFoundError)
- [X] T036 [US3] Test US3 scenario 3 (user A tries to complete user B's task → UnauthorizedError)
- [X] T037 [US3] Test US3 scenario 4 (already completed task → idempotent, returns task)
- [X] T038 [US3] Test US3 scenario 5 (invalid task_id format → ValidationError)

## Phase 5: User Story 4 - AI Agent Deletes Task via MCP Tool (Priority: P2)

**Story Goal**: Enable AI agent to delete tasks via delete_task MCP tool

**Independent Test Criteria**:
- Create task
- Call delete_task(user_id, task_id, db) → task removed from database
- Verify subsequent list_tasks doesn't include deleted task

### Implementation Tasks

- [X] T039 [US4] Implement delete_task tool at backend/src/mcp/tools/delete_task.py wrapping TaskService.delete_task
- [X] T040 [US4] Add input validation in delete_task tool (user_id UUID, task_id UUID)
- [X] T041 [US4] Add TaskService invocation in delete_task tool (deletes task with authorization)
- [X] T042 [US4] Add error handling in delete_task tool (catch HTTPException 404 → TaskNotFoundError, 403 → UnauthorizedError)
- [X] T043 [US4] Return None from delete_task tool on success
- [X] T044 [US4] Create unit test file at backend/tests/mcp/test_delete_task.py
- [X] T045 [US4] Test US4 scenario 1 (user owns task → permanently deleted)
- [X] T046 [US4] Test US4 scenario 2 (task_id doesn't exist → TaskNotFoundError)
- [X] T047 [US4] Test US4 scenario 3 (user A tries to delete user B's task → UnauthorizedError)
- [X] T048 [US4] Test US4 scenario 4 (delete same task twice → TaskNotFoundError on second call)
- [X] T049 [US4] Test US4 scenario 5 (invalid task_id format → ValidationError)

## Phase 6: User Story 5 - AI Agent Updates Task via MCP Tool (Priority: P3)

**Story Goal**: Enable AI agent to update task titles via update_task MCP tool

**Independent Test Criteria**:
- Create task with title "buy milk"
- Call update_task(user_id, task_id, "buy almond milk", db) → title updated
- Verify updated_at timestamp refreshed

### Implementation Tasks

- [X] T050 [US5] Implement update_task tool at backend/src/mcp/tools/update_task.py wrapping TaskService.update_task
- [X] T051 [US5] Add input validation in update_task tool (user_id UUID, task_id UUID, new_title 1-500 chars)
- [X] T052 [US5] Add TaskService invocation in update_task tool (updates task with authorization)
- [X] T053 [US5] Add error handling in update_task tool (catch HTTPException 404 → TaskNotFoundError, 403 → UnauthorizedError, 400 → ValidationError)
- [X] T054 [US5] Return updated task.model_dump() from update_task tool
- [X] T055 [US5] Create unit test file at backend/tests/mcp/test_update_task.py
- [X] T056 [US5] Test US5 scenario 1 (user owns task → title updated and returned)
- [X] T057 [US5] Test US5 scenario 2 (empty new_title → ValidationError)
- [X] T058 [US5] Test US5 scenario 3 (task_id doesn't exist → TaskNotFoundError)
- [X] T059 [US5] Test US5 scenario 4 (user A tries to update user B's task → UnauthorizedError)
- [X] T060 [US5] Test US5 scenario 5 (invalid task_id format → ValidationError)

## Phase 7: Spec-4 Agent Integration

**Purpose**: Replace Spec-4 mock tools with real MCP tools

- [X] T061 Update imports in backend/src/agent/tool_mapper.py (replace mock imports with real MCP tool imports)
- [X] T062 Add database session parameter to invoke_tool function in backend/src/agent/tool_mapper.py
- [X] T063 Pass database session to all MCP tool calls in backend/src/agent/tool_mapper.py (5 tool invocations)
- [X] T064 Update imports in backend/src/agent/tool_mapper.py to include MCP error classes from src.mcp.errors
- [X] T065 Add database session parameter to run_agent function in backend/src/agent/chat_agent.py
- [X] T066 Pass database session to invoke_tool calls in backend/src/agent/chat_agent.py
- [X] T067 Remove mock tools directory backend/src/agent/mocks/ (no longer needed - kept for reference but no longer used)
- [X] T068 Run all 23 Spec-4 agent tests with real MCP tools to verify integration
- [X] T069 Validate end-to-end flow (user message → agent → MCP tools → database → response)
- [X] T070 Measure performance (tool overhead <50ms, end-to-end <2s)

## Phase 8: Validation & Polish

**Purpose**: Ensure constitutional compliance and production readiness

- [X] T071 Verify no business logic duplication (MCP tools only wrap TaskService)
- [X] T072 Verify stateless architecture (no in-memory state in MCP tools)
- [X] T073 Verify authorization enforcement (cross-user access tests)
- [X] T074 Verify database transactions work correctly (no partial updates on errors)
- [X] T075 Add logging for all MCP tool invocations (user_id, tool_name, parameters, result/error, duration_ms)
- [X] T076 Validate all 25 acceptance scenarios from spec.md pass
- [X] T077 Run concurrency tests (multiple concurrent tool invocations)
- [X] T078 Document MCP tool interface for future reference

## Dependencies & Execution Order

### User Story Dependencies

```
Phase 1: Setup (T001-T004) ───────┐
                                   │
                ┌──────────────────┘
                │
                ├── Phase 2: US1 - add_task (T005-T015) ──┐
                │                                          │
                ├── Phase 3: US2 - list_tasks (T016-T027) ├─ Independent
                │                                          │ (parallel)
                ├── Phase 4: US3 - complete_task (T028-T038)│
                │                                          │
                ├── Phase 5: US4 - delete_task (T039-T049)┤
                │                                          │
                └── Phase 6: US5 - update_task (T050-T060)┘
                                   │
                                   │ All tools must be complete
                                   ↓
Phase 7: Spec-4 Integration (T061-T070) ─ Requires all tools implemented
                                   │
                                   ↓
Phase 8: Validation & Polish (T071-T078) ─ Final validation
```

### MVP Scope

**Minimum Viable Product**:
- Phase 1: Setup (4 tasks)
- Phase 2: US1 - add_task (11 tasks)
- Phase 3: US2 - list_tasks (12 tasks)
- **MVP Total**: 27 tasks

This delivers the core read-write cycle: AI agent can create and list tasks via MCP tools with real database persistence.

### Recommended Order

1. Phase 1: Setup (T001-T004)
2. Phase 2: US1 - add_task (T005-T015) - P1
3. Phase 3: US2 - list_tasks (T016-T027) - P1
4. Phase 4: US3 - complete_task (T028-T038) - P2
5. Phase 5: US4 - delete_task (T039-T049) - P2
6. Phase 6: US5 - update_task (T050-T060) - P3
7. Phase 7: Spec-4 Integration (T061-T070)
8. Phase 8: Validation & Polish (T071-T078)

### Parallel Execution Examples

**Phase 1 (Setup) Parallelization**:
```bash
T001 (create directory) → then parallel: T002, T003, T004
```

**User Story Phases (US1-US5) Parallelization**:
```bash
# After Phase 1, all tool implementations can run in parallel
Developer 1: T005-T015 (US1 - add_task)
Developer 2: T016-T027 (US2 - list_tasks)
Developer 3: T028-T038 (US3 - complete_task)
Developer 4: T039-T049 (US4 - delete_task)
Developer 5: T050-T060 (US5 - update_task)
```

## Implementation Strategy

### Iteration 1 (MVP - Basic Read/Write):
- Phase 1: Setup (4 tasks)
- Phase 2: US1 - add_task (11 tasks)
- Phase 3: US2 - list_tasks (12 tasks)
- **MVP Total**: 27 tasks

**Deliverable**: AI agent can create and list tasks via real MCP tools with database persistence.

### Iteration 2 (Task Lifecycle Management):
- Phase 4: US3 - complete_task (11 tasks)
- Phase 5: US4 - delete_task (11 tasks)

**Deliverable**: Full CRUD operations minus update.

### Iteration 3 (Complete Feature Set):
- Phase 6: US5 - update_task (11 tasks)
- Phase 7: Spec-4 Integration (10 tasks)
- Phase 8: Validation & Polish (8 tasks)

**Deliverable**: Complete MCP server integrated with Spec-4, all tests passing.

## Total Task Count

- **Phase 1 (Setup)**: 4 tasks
- **Phase 2 (US1 - add_task)**: 11 tasks
- **Phase 3 (US2 - list_tasks)**: 12 tasks
- **Phase 4 (US3 - complete_task)**: 11 tasks
- **Phase 5 (US4 - delete_task)**: 11 tasks
- **Phase 6 (US5 - update_task)**: 11 tasks
- **Phase 7 (Spec-4 Integration)**: 10 tasks
- **Phase 8 (Validation & Polish)**: 8 tasks

**Total**: 78 tasks

**Parallel Opportunities**: 3 tasks marked [P] (can run in parallel within Phase 1) + 5 independent user stories (US1-US5) can be implemented in parallel after Phase 1

**Independent User Stories**: 5 tools that can be implemented in parallel by different developers after Phase 1 completes
