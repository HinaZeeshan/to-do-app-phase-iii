# Implementation Plan: MCP Server, Tools & Persistence Layer

**Branch**: `005-mcp-server-tools` | **Date**: 2026-02-07 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/005-mcp-server-tools/spec.md`

## Summary

Implement a stateless MCP (Model Context Protocol) server that exposes 5 task management tools (add, list, complete, delete, update) for the AI chat agent (Spec-4). The MCP tools wrap existing TaskService business logic with user-level authorization checks, persist all state to the PostgreSQL database, and return structured responses. The server uses the Official MCP SDK, maintains zero in-memory state, validates all inputs, and integrates seamlessly with the existing backend infrastructure without modifying Phase II REST APIs.

## Technical Context

**Language/Version**: Python 3.11 (matches existing backend stack)
**Primary Dependencies**: Official MCP SDK (Python version), existing FastAPI backend infrastructure, TaskService (Spec-1)
**Storage**: Neon PostgreSQL via SQLModel ORM (existing infrastructure from Spec-1)
**Testing**: pytest (matches existing backend test framework)
**Target Platform**: Linux server (backend component)
**Project Type**: Web application - backend MCP server module
**Performance Goals**: <50ms MCP tool overhead, <200ms list_tasks p95 latency
**Constraints**: Stateless architecture, no REST API changes, business logic reuse only, user-level authorization
**Scale/Scope**: 5 MCP tools wrapping existing TaskService; integration with Spec-4 AI agent

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Core Principles Compliance

✅ **I. Spec-Driven Development**: Plan follows spec.md with no implementation leakage
✅ **II. Security-First Architecture**: Tools enforce user-level authorization; validate user_id on all operations
✅ **III. Clear Separation of Concerns**: MCP tools handle protocol interface only; delegate to existing TaskService for business logic
✅ **IV. Performance-Conscious Design**: Performance targets defined (<50ms overhead, <200ms list_tasks); no feature additions
✅ **V. Deterministic and Reproducible Outputs**: Database-backed operations are deterministic; same inputs → same database state
✅ **VI. Stateless Server Components (Phase III)**: MCP server maintains zero in-memory state; all data persisted in database
✅ **VII. Protocol-Driven Tool Execution (Phase III)**: MCP protocol defines tool interface; tools are stateless operations

### Architecture & Technology Standards Compliance

✅ **Backend Stack**: Python 3.11, FastAPI infrastructure, SQLModel, Neon PostgreSQL (existing)
✅ **MCP Server & Chat Infrastructure (Phase III)**:
  - Official MCP SDK (required) ✓
  - Stateless, idempotent operations ✓
  - All tool actions persist state in database ✓
  - User-level authorization enforced ✓

### Security Requirements Compliance

✅ **Authorization Rules**:
  - MCP tools validate user_id on all operations ✓
  - Database queries filter by authenticated user_id ✓
  - No cross-user access (ownership validation) ✓

### Constraints Enforcement

✅ **Phase III Constraints**:
  - No changes to Phase II REST APIs (MCP tools are separate module) ✓
  - No duplication of task business logic (uses existing TaskService) ✓
  - No server-held memory across requests (stateless, database-backed) ✓
  - No manual coding; Claude Code only ✓

**Gate Status**: ✅ PASSED - All constitutional requirements satisfied

## Project Structure

### Documentation (this feature)

```text
specs/005-mcp-server-tools/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── mcp/                      # NEW: MCP server module
│   │   ├── __init__.py
│   │   ├── server.py             # MCP server setup and tool registration
│   │   ├── tools/                # MCP tool implementations
│   │   │   ├── __init__.py
│   │   │   ├── add_task.py       # add_task tool
│   │   │   ├── list_tasks.py     # list_tasks tool
│   │   │   ├── complete_task.py  # complete_task tool
│   │   │   ├── delete_task.py    # delete_task tool
│   │   │   └── update_task.py    # update_task tool
│   │   ├── schemas.py            # MCP tool input/output schemas
│   │   └── errors.py             # Structured error classes
│   ├── agent/                    # Existing: AI agent from Spec-4
│   ├── services/                 # Existing: TaskService
│   ├── models/                   # Existing: Task model
│   ├── database.py               # Existing: DB connection
│   └── main.py                   # Existing: FastAPI app
└── tests/
    ├── mcp/                      # NEW: MCP tool tests
    │   ├── test_add_task.py
    │   ├── test_list_tasks.py
    │   ├── test_complete_task.py
    │   ├── test_delete_task.py
    │   └── test_update_task.py
    ├── agent/                    # Existing: Agent tests from Spec-4
    └── integration/              # Existing: End-to-end tests
```

**Structure Decision**: Web application structure. MCP server is a new backend module under `backend/src/mcp/`. Integrates with existing TaskService, database infrastructure, and Spec-4 AI agent. No changes to existing REST API routes (Phase II unchanged).

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

N/A - No constitutional violations. All principles and constraints satisfied.

## Phase 0: Research & Technology Selection

**Objective**: Resolve all technical unknowns and validate MCP SDK integration approach.

### Research Tasks

#### R1: Official MCP SDK Integration
**Question**: How to integrate Official MCP SDK with Python 3.11 FastAPI backend?

**Research Areas**:
- Official MCP SDK Python library installation and setup
- MCP server initialization patterns
- Tool registration and schema definition
- Integration with existing async FastAPI patterns
- Stateless server architecture best practices

**Decision Criteria**:
- SDK compatible with Python 3.11
- Supports async/await patterns
- Clear documentation for tool registration
- Stateless operation support

#### R2: MCP Tool Schema Definition
**Question**: What is the MCP tool schema format and how to define tool input/output contracts?

**Research Areas**:
- MCP tool schema specification format
- Parameter validation mechanisms
- Error response formats
- Tool result serialization

**Decision Criteria**:
- Clear schema definition format
- Built-in validation support
- Compatible with Pydantic models
- Structured error responses

#### R3: TaskService Integration Pattern
**Question**: How should MCP tools invoke existing TaskService methods?

**Research Areas**:
- Review existing TaskService methods from Spec-1
- Determine wrapper pattern (thin adapter vs enhanced wrapper)
- Authorization check placement (tool layer vs service layer)
- Database session management

**Decision Criteria**:
- No duplication of business logic (constitutional requirement)
- Authorization enforced before TaskService invocation
- Database transactions properly managed
- Error handling consistent with existing patterns

#### R4: Spec-4 Agent Integration
**Question**: How will Spec-4 AI agent invoke MCP tools (local calls vs remote protocol)?

**Research Areas**:
- MCP SDK invocation patterns (local vs remote)
- Review Spec-4 agent contracts (contracts/mcp_tools.yaml)
- Determine import/invocation mechanism
- Error propagation from tools to agent

**Decision Criteria**:
- Matches Spec-4 agent expectations
- Minimal integration complexity
- Clear error propagation
- Performance acceptable (<50ms overhead)

#### R5: Error Handling Strategy
**Question**: How should MCP tools structure error responses for agent consumption?

**Research Areas**:
- MCP SDK error handling patterns
- Structured error format (error_type, message, details)
- Error classes (TaskNotFoundError, ValidationError, UnauthorizedError, DatabaseError)
- Integration with Spec-4 agent error translation

**Decision Criteria**:
- Consistent error structure across all tools
- Agent can translate errors to user-friendly messages
- No sensitive information leakage
- Actionable error details for debugging

### Research Output

See `research.md` for detailed findings, decisions, rationale, and alternatives considered.

## Phase 1: Design & Architecture

**Prerequisites**: `research.md` complete

### Data Model

**Objective**: Define MCP tool schemas and reuse existing Task model from Spec-1.

See `data-model.md` for:
- **MCP Tool Schemas**: Input/output schemas for all 5 tools
- **Error Classes**: TaskNotFoundError, ValidationError, UnauthorizedError, DatabaseError
- **Task Model**: Reference to existing Spec-1 Task entity (no changes)
- **Tool Result Format**: Structured success/error responses

### API Contracts

**Objective**: Define MCP tool contracts that match Spec-4 agent expectations.

See `contracts/` for:
- **mcp_tools_impl.yaml**: Complete MCP tool implementations spec
  - add_task: input (user_id, title), output (Task object)
  - list_tasks: input (user_id, filter), output (List[Task])
  - complete_task: input (user_id, task_id), output (Task object)
  - delete_task: input (user_id, task_id), output (success confirmation)
  - update_task: input (user_id, task_id, new_title), output (Task object)

- **integration_with_spec4.yaml**: How MCP tools integrate with Spec-4 agent
  - Import mechanism
  - Error propagation
  - Tool invocation patterns

### Architecture Diagram

See `quickstart.md` for:
- MCP server architecture diagram
- Tool execution flow (Agent → MCP Tool → TaskService → Database)
- Authorization enforcement flow (validate user_id → check ownership → execute operation)
- Error handling flow (Database error → MCP tool → Agent → User-friendly message)
- Integration with Spec-4 agent (replace mock tools with real MCP tools)

### Implementation Phases

**Phase 1A: MCP Server Setup**
- Install Official MCP SDK dependency
- Create MCP server module structure
- Initialize MCP server with tool registration
- Configure stateless operation mode

**Phase 1B: Tool Schemas & Errors**
- Define Pydantic schemas for all 5 tool inputs/outputs
- Create structured error classes (TaskNotFoundError, etc.)
- Implement input validation logic
- Define tool result serialization

**Phase 1C: MCP Tool Implementations**
- Implement add_task tool (wrap TaskService.create_task)
- Implement list_tasks tool (wrap TaskService.list_tasks)
- Implement complete_task tool (wrap TaskService.complete_task)
- Implement delete_task tool (wrap TaskService.delete_task)
- Implement update_task tool (wrap TaskService.update_task)

**Phase 1D: Authorization & Validation**
- Add user_id validation to all tools
- Implement ownership verification for complete/delete/update
- Add input schema validation
- Add database transaction management

**Phase 1E: Integration with Spec-4**
- Update Spec-4 tool_mapper.py to import real MCP tools
- Replace mock tool calls with real MCP tool invocations
- Test end-to-end flow (agent → MCP tools → database)
- Validate determinism with real database operations

## Phase 2: Testing & Validation

**Objective**: Validate MCP tools against spec acceptance criteria.

### Contract Tests
- MCP tool schemas match contracts/mcp_tools_impl.yaml
- Tool input/output formats match Spec-4 agent expectations
- Error responses structured correctly

### Integration Tests
- Test all 25 acceptance scenarios from spec.md
- User Story 1: add_task (5 scenarios)
- User Story 2: list_tasks (5 scenarios)
- User Story 3: complete_task (5 scenarios)
- User Story 4: delete_task (5 scenarios)
- User Story 5: update_task (5 scenarios)

### Authorization Tests
- Tools reject unauthorized access (user A cannot modify user B's tasks)
- Tools validate user_id format before database operations
- Tools properly filter database queries by user_id

### Concurrency Tests
- Multiple concurrent add_task operations complete successfully
- Concurrent modifications to same task handled correctly (last write wins)
- Database transactions prevent partial updates

### Success Criteria Validation
- SC-001: 100% success rate for valid inputs (measure via test scenarios)
- SC-002: <200ms p95 latency for list_tasks (measure with timer)
- SC-003: 100% authorization enforcement (test cross-user access attempts)
- SC-004: 0% data leakage (verify all queries filter by user_id)
- SC-007: 100% input validation (test malformed inputs)

## Dependencies

### External Dependencies
- **Official MCP SDK (Python)**: Required for MCP server implementation (constitutional requirement)
- **Existing Backend Infrastructure**: FastAPI, SQLModel, asyncpg, Neon PostgreSQL (already installed from Spec-1)

### Internal Dependencies
- **Spec-1 (Backend API & Database)**: CRITICAL - Provides:
  - TaskService with CRUD business logic
  - Task model (SQLModel entity)
  - Database connection and session management
  - **Dependency Type**: Blocking - MCP tools cannot be implemented without TaskService

- **Spec-4 (AI Chat Agent)**: Consumer of MCP tools; defines expected tool interface in contracts/mcp_tools.yaml
- **Spec-2 (Auth & JWT Security)**: Provides user_id validation (upstream of MCP tools)

### Dependency Resolution Strategy
1. **Reuse TaskService**: MCP tools wrap existing TaskService methods (no duplication)
2. **Coordinate with Spec-4**: Implement tools matching contracts/mcp_tools.yaml from Spec-4
3. **Integration Testing**: Replace Spec-4 mock tools with real MCP tools after implementation

## Risks & Mitigations

### Risk 1: MCP SDK Compatibility with FastAPI
**Description**: Official MCP SDK may not integrate smoothly with existing async FastAPI patterns.

**Likelihood**: Medium
**Impact**: Medium (workaround possible but adds complexity)

**Mitigation**:
- Research MCP SDK async support early (Phase 0)
- Create adapter layer if SDK is sync-only
- Test integration with existing database session management
- Document any compatibility issues for future SDK upgrades

### Risk 2: Business Logic Duplication Temptation
**Description**: Developers may duplicate TaskService logic in MCP tools instead of wrapping.

**Likelihood**: Low
**Impact**: High (violates constitutional constraint)

**Mitigation**:
- Explicit requirement: "MCP tools MUST call TaskService methods"
- Code review checklist item: "No duplicated business logic"
- Tool implementations are thin wrappers only (authorization + TaskService call)
- Contract tests verify TaskService is invoked

### Risk 3: Stateful MCP Server Implementation
**Description**: MCP server may accidentally maintain in-memory state (caching, sessions).

**Likelihood**: Low
**Impact**: High (violates constitutional requirement)

**Mitigation**:
- Explicit architecture: "Zero in-memory state"
- All data persisted in database immediately
- Server restart tests verify no data loss
- No caching, session storage, or in-memory data structures

### Risk 4: Authorization Bypass
**Description**: MCP tools may skip ownership validation, allowing cross-user access.

**Likelihood**: Low
**Impact**: Critical (security violation)

**Mitigation**:
- Authorization checks in every tool (except add_task and list_tasks which filter by user_id)
- Database queries always include user_id filter
- Integration tests verify cross-user access is rejected
- Security-focused code review

## Next Steps

1. ✅ **Phase 0 Complete**: Generate `research.md` with MCP SDK integration patterns, TaskService wrapper design, tool schema format
2. ✅ **Phase 1 Complete**: Generate `data-model.md`, `contracts/`, `quickstart.md`
3. **Ready for Tasks**: Run `/sp.tasks` to generate actionable implementation tasks
4. **Coordinate with Spec-4**: Ensure tool implementation matches Spec-4 contracts (contracts/mcp_tools.yaml)
5. **Implementation**: Follow tasks.md task order (server setup → schemas → tools → authorization → integration)

---

**Plan Status**: ✅ COMPLETE - Ready for `/sp.tasks`
**Constitutional Compliance**: ✅ PASSED - All Phase III principles enforced
**Critical Path**: TaskService (Spec-1) available; Spec-4 agent ready to integrate
