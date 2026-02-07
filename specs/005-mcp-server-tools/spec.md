# Feature Specification: MCP Server, Tools & Persistence Layer

**Feature Branch**: `005-mcp-server-tools`
**Created**: 2026-02-07
**Status**: Draft
**Input**: User description: "Spec-5: MCP Server, Tools & Persistence Layer - Stateless MCP server exposing task-management tools with database persistence"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - AI Agent Creates Task via MCP Tool (Priority: P1)

As an AI agent (or developer), I want to invoke an MCP tool to create a task for a user so that task data is persisted in the database with proper user ownership and the agent receives confirmation of creation.

**Why this priority**: This is the foundational capability that enables the AI chat agent (Spec-4) to create tasks. Without this, the entire Phase III AI chatbot feature is non-functional. This represents the minimum viable MCP tool.

**Independent Test**: Can be fully tested by calling the add_task MCP tool with a user_id and title, verifying the task is persisted in the database with correct user ownership, and confirming the tool returns the complete task object including generated ID and timestamps.

**Acceptance Scenarios**:

1. **Given** a valid user_id and task title, **When** add_task tool is invoked, **Then** a new task is persisted to the database and the complete task object is returned
2. **Given** a user_id and empty title, **When** add_task tool is invoked, **Then** a ValidationError is returned with message "Title cannot be empty"
3. **Given** an invalid user_id format, **When** add_task tool is invoked, **Then** a ValidationError is returned with message "Invalid user_id format"
4. **Given** a user_id and title exceeding 500 characters, **When** add_task tool is invoked, **Then** a ValidationError is returned with message "Title exceeds maximum length"
5. **Given** the database is unavailable, **When** add_task tool is invoked, **Then** a DatabaseError is returned with message "Unable to persist task"

---

### User Story 2 - AI Agent Retrieves Task List via MCP Tool (Priority: P1)

As an AI agent, I want to invoke an MCP tool to retrieve all tasks for a user (with optional filtering by completion status) so that I can display the task list to the user or find tasks for further operations.

**Why this priority**: This is equally critical to task creation. The AI agent needs to retrieve tasks to display them to users and to match task references for complete/delete/update operations. Without this, the agent cannot provide any task visibility.

**Independent Test**: Can be fully tested by creating 5 tasks for a user (3 pending, 2 completed), then calling list_tasks MCP tool with user_id and filter="pending", verifying exactly 3 pending tasks are returned with correct titles and completion status.

**Acceptance Scenarios**:

1. **Given** a user has 5 tasks (3 pending, 2 completed), **When** list_tasks tool is invoked with filter="all", **Then** all 5 tasks are returned sorted by creation date (newest first)
2. **Given** a user has 5 tasks (3 pending, 2 completed), **When** list_tasks tool is invoked with filter="pending", **Then** only the 3 pending tasks are returned
3. **Given** a user has 5 tasks (3 pending, 2 completed), **When** list_tasks tool is invoked with filter="completed", **Then** only the 2 completed tasks are returned
4. **Given** a user has no tasks, **When** list_tasks tool is invoked, **Then** an empty list is returned (not an error)
5. **Given** an invalid user_id format, **When** list_tasks tool is invoked, **Then** a ValidationError is returned

---

### User Story 3 - AI Agent Marks Task Complete via MCP Tool (Priority: P2)

As an AI agent, I want to invoke an MCP tool to mark a specific task as completed so that the task's completion status and timestamp are updated in the database and the agent can confirm the action to the user.

**Why this priority**: Completing tasks is a core part of task lifecycle management. Users need this to mark tasks as done via the AI agent. Less critical than creation and listing because users can complete tasks via the existing REST API as a workaround.

**Independent Test**: Can be fully tested by creating a pending task, calling complete_task MCP tool with user_id and task_id, verifying the task's is_completed flag is set to true and completed_at timestamp is populated, and confirming the updated task object is returned.

**Acceptance Scenarios**:

1. **Given** a user owns a pending task, **When** complete_task tool is invoked with user_id and task_id, **Then** the task is marked completed with timestamp and the updated task is returned
2. **Given** a task_id that doesn't exist, **When** complete_task tool is invoked, **Then** a TaskNotFoundError is returned
3. **Given** user A tries to complete user B's task, **When** complete_task tool is invoked, **Then** an UnauthorizedError is returned
4. **Given** a task that is already completed, **When** complete_task tool is invoked again, **Then** the tool succeeds (idempotent) and returns the already-completed task
5. **Given** an invalid task_id format, **When** complete_task tool is invoked, **Then** a ValidationError is returned

---

### User Story 4 - AI Agent Deletes Task via MCP Tool (Priority: P2)

As an AI agent, I want to invoke an MCP tool to permanently delete a specific task so that unwanted tasks are removed from the database and the agent can confirm deletion to the user.

**Why this priority**: Deleting tasks is useful for managing the task list but not critical for MVP. Users can work around this by ignoring unwanted tasks or using the REST API. This is less urgent than creation, listing, and completion.

**Independent Test**: Can be fully tested by creating a task, calling delete_task MCP tool with user_id and task_id, verifying the task is removed from the database (subsequent list_tasks doesn't include it), and confirming the tool returns success.

**Acceptance Scenarios**:

1. **Given** a user owns a task, **When** delete_task tool is invoked with user_id and task_id, **Then** the task is permanently deleted from the database
2. **Given** a task_id that doesn't exist, **When** delete_task tool is invoked, **Then** a TaskNotFoundError is returned
3. **Given** user A tries to delete user B's task, **When** delete_task tool is invoked, **Then** an UnauthorizedError is returned
4. **Given** a task is deleted, **When** delete_task tool is invoked again with the same task_id, **Then** a TaskNotFoundError is returned (not idempotent by design)
5. **Given** an invalid task_id format, **When** delete_task tool is invoked, **Then** a ValidationError is returned

---

### User Story 5 - AI Agent Updates Task via MCP Tool (Priority: P3)

As an AI agent, I want to invoke an MCP tool to update a task's title or description so that task details can be modified via natural language and changes are persisted to the database.

**Why this priority**: Updating tasks is a convenience feature but not essential for MVP. Users can delete and recreate tasks or use the REST API as a workaround. This is the lowest priority core operation.

**Independent Test**: Can be fully tested by creating a task with title "buy milk", calling update_task MCP tool with user_id, task_id, and new_title="buy almond milk", verifying the task title is updated in the database and the updated_at timestamp is refreshed, and confirming the updated task object is returned.

**Acceptance Scenarios**:

1. **Given** a user owns a task, **When** update_task tool is invoked with user_id, task_id, and new_title, **Then** the task title is updated and the modified task is returned
2. **Given** a user owns a task, **When** update_task tool is invoked with new_title as empty string, **Then** a ValidationError is returned with message "Title cannot be empty"
3. **Given** a task_id that doesn't exist, **When** update_task tool is invoked, **Then** a TaskNotFoundError is returned
4. **Given** user A tries to update user B's task, **When** update_task tool is invoked, **Then** an UnauthorizedError is returned
5. **Given** an invalid task_id format, **When** update_task tool is invoked, **Then** a ValidationError is returned

---

### Edge Cases

- **What happens when multiple concurrent requests modify the same task?** Database transactions ensure consistency; last write wins; updated_at timestamp reflects most recent change
- **How does the system handle database connection failures?** MCP tools return DatabaseError; agent translates to user-friendly message; no data loss (transaction rollback)
- **What happens when tool parameters are malformed (wrong types)?** MCP server validates input schemas before tool execution; returns ValidationError with specific field and issue
- **How does the system handle very large result sets (thousands of tasks)?** list_tasks returns all tasks (no pagination in MVP); performance concerns addressed in future optimization
- **What happens when a task is deleted while another operation is in progress?** Database-level locking prevents race conditions; second operation receives TaskNotFoundError
- **How does the MCP server handle authentication?** MCP tools receive authenticated user_id from chat infrastructure (Spec-4 or caller); tools validate ownership at data access layer
- **What happens if the MCP server crashes or restarts?** All state is in database (stateless server); no data loss; operations resume after restart

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: MCP server MUST be implemented using the Official MCP SDK (Python or TypeScript version)
- **FR-002**: MCP server MUST expose 5 task management tools: add_task, list_tasks, complete_task, delete_task, update_task
- **FR-003**: MCP server MUST maintain zero server-side state; all operations are stateless
- **FR-004**: add_task tool MUST accept user_id and title; persist task to database; return complete task object with generated ID
- **FR-005**: list_tasks tool MUST accept user_id and optional filter (all, pending, completed); return list of tasks filtered and sorted by creation date
- **FR-006**: complete_task tool MUST accept user_id and task_id; mark task as completed; set completed_at timestamp; return updated task
- **FR-007**: delete_task tool MUST accept user_id and task_id; permanently remove task from database; return success confirmation
- **FR-008**: update_task tool MUST accept user_id, task_id, and new_title; update task title; refresh updated_at timestamp; return updated task
- **FR-009**: All MCP tools MUST validate user_id format (valid UUID) before database operations
- **FR-010**: All MCP tools (except add_task and list_tasks) MUST verify the user owns the referenced task; return UnauthorizedError if user_id mismatch
- **FR-011**: All MCP tools MUST use existing TaskService business logic from Spec-1; no duplication of business logic
- **FR-012**: All MCP tools MUST use database transactions to ensure atomicity and consistency
- **FR-013**: MCP server MUST validate tool input schemas before execution; return ValidationError for malformed inputs
- **FR-014**: MCP server MUST return structured error responses: error_type, error_message, details (optional)
- **FR-015**: MCP tools MUST log all invocations with: user_id, tool_name, parameters, result/error, duration_ms
- **FR-016**: MCP server MUST NOT maintain conversation history; conversation persistence is handled separately (chat infrastructure)

### Key Entities

- **MCP Server**: Stateless server process exposing task management tools via MCP protocol
- **MCP Tool**: Individual operation (add_task, list_tasks, etc.) with defined input/output schema and database persistence logic
- **Task**: Existing entity from Spec-1 (id, user_id, title, description, is_completed, completed_at, created_at, updated_at)
- **TaskService**: Existing business logic from Spec-1; MCP tools wrap TaskService methods with authorization checks
- **Tool Result**: Structured response from MCP tool containing either success data (task object, task list) or error information

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: AI agents can create tasks via add_task tool with 100% success rate for valid inputs
- **SC-002**: AI agents can retrieve task lists via list_tasks tool with results returned in under 200ms (p95 latency)
- **SC-003**: AI agents can modify tasks (complete, delete, update) with 100% success rate for owned tasks and 100% authorization enforcement for non-owned tasks
- **SC-004**: MCP tools enforce user-level data isolation: 0% cross-user data leakage across all operations
- **SC-005**: MCP server handles concurrent requests without data corruption (database transactions ensure consistency)
- **SC-006**: MCP server restarts result in zero data loss (all state persisted in database)
- **SC-007**: Tool input validation catches 100% of malformed requests before database operations
- **SC-008**: Error responses provide clear, actionable information for debugging (error_type, message, details)

## Assumptions *(mandatory)*

- **TaskService and Task model already exist** from Spec-1; MCP tools reuse this business logic
- **Database connection and session management already configured** in Spec-1; MCP tools use existing infrastructure
- **User authentication handled upstream**; MCP tools receive authenticated user_id from caller (AI agent or chat infrastructure)
- **MCP tools are invoked locally** (same process as AI agent); not exposed as external API endpoints
- **Conversation history persistence is separate** from task persistence; MCP server handles only task operations
- **No pagination in MVP**; list_tasks returns all user tasks (performance optimization deferred to future)
- **Task schema matches Spec-1 contracts**; MCP tools return task objects in same format as REST API

## Scope Boundaries *(mandatory)*

### In Scope
- MCP server implementation using Official MCP SDK
- 5 MCP tools for task management (add, list, complete, delete, update)
- Database persistence via existing SQLModel + PostgreSQL infrastructure
- Input validation and error handling for all tools
- User-level authorization enforcement
- Tool invocation logging for audit trail
- Integration with existing TaskService business logic

### Out of Scope
- AI agent implementation (covered in Spec-4)
- Conversation persistence and retrieval (separate concern, not part of task tools)
- Chat API endpoint (may be added separately or integrated with existing FastAPI app)
- REST API modifications (Phase II APIs remain unchanged per constitution)
- Frontend UI changes (covered in Spec-3)
- User authentication and JWT validation (covered in Spec-2)
- Task scheduling, reminders, or notifications
- Task priority, tags, categories, or relationships
- Pagination, sorting, or advanced filtering (deferred to future optimization)

## Dependencies *(mandatory)*

- **Spec-1 (Backend API & Database)**: Provides TaskService, Task model, database connection, SQLModel ORM
- **Spec-2 (Auth & JWT Security)**: Provides user_id from JWT validation (upstream of MCP tools)
- **Spec-4 (AI Chat Agent)**: Primary consumer of MCP tools; invokes tools based on user intent
- **Official MCP SDK**: Required framework for implementing the MCP server (Python or TypeScript version)
- **Existing Database Infrastructure**: Neon PostgreSQL connection, SQLModel ORM, database session management

## Constraints *(mandatory)*

- **Stateless architecture**: MCP server maintains no in-memory state; all data persisted in database
- **No REST API changes**: MCP tools are separate from Phase II REST APIs (cannot modify existing endpoints)
- **Business logic reuse**: MCP tools MUST use existing TaskService; no duplication of task business logic
- **User-level authorization**: Every tool MUST validate user owns the referenced resource
- **Database transactions**: All write operations MUST use transactions for atomicity
- **Input validation**: All tools MUST validate inputs before database access
- **Error handling**: Tools MUST return structured errors (not raise unhandled exceptions)

## Non-Functional Requirements *(optional)*

### Performance
- MCP tool invocation overhead should be under 50ms (excluding database query time)
- list_tasks should return results in under 200ms for typical user task counts (<100 tasks)
- Database queries should be optimized with proper indexes (user_id, is_completed)

### Reliability
- MCP tools must handle database errors gracefully without crashing
- Database connection pooling should support concurrent tool invocations
- Transaction rollback on errors prevents partial state updates

### Maintainability
- MCP tool definitions should be version-controlled and reviewable
- Tool schemas should be documented (input/output contracts)
- Error types should be consistent across all tools

### Security
- User_id validation prevents unauthorized data access
- Database queries use parameterized statements (SQL injection protection)
- Error messages do not leak sensitive information (other users' data, database structure)

## Open Questions *(optional - for clarifications needed before planning)*

*No open questions - all requirements are fully specified. Reasonable defaults applied:*
- MCP SDK version: Latest stable Python version (compatible with existing Python 3.11 backend)
- Tool interface: Local function calls (not remote API)
- Error handling: Structured error objects (error_type, message, details)
- Logging: Standard application logging (same format as existing backend logs)
