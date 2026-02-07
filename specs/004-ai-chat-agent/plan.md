# Implementation Plan: AI Chat Agent & Conversation Logic

**Branch**: `004-ai-chat-agent` | **Date**: 2026-02-07 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/004-ai-chat-agent/spec.md`

## Summary

Implement an AI-powered chat agent that interprets natural language todo commands (add, list, complete, delete, update tasks) and converts them into MCP tool invocations. The agent uses the OpenAI Agents SDK for natural language processing, maintains stateless architecture with full conversation history per request, and ensures deterministic behavior by exclusively using MCP tools for all task operations. No direct database access, no UI responsibility, and no hallucination—all task data comes from MCP tool responses.

## Technical Context

**Language/Version**: Python 3.11 (matches existing backend stack)
**Primary Dependencies**: OpenAI Agents SDK (required), existing FastAPI backend infrastructure
**Storage**: N/A (agent is stateless; conversation storage handled by Spec-5)
**Testing**: pytest (matches existing backend test framework)
**Target Platform**: Linux server (backend component)
**Project Type**: Web application - backend AI agent module
**Performance Goals**: <500ms agent processing time (excluding MCP tool latency), handle conversations up to 50 messages
**Constraints**: Stateless architecture, no direct database access, deterministic outputs, single-turn interactions
**Scale/Scope**: Single AI agent module; integrates with existing task management system (5 CRUD operations)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Core Principles Compliance

✅ **I. Spec-Driven Development**: Plan follows spec.md with no implementation leakage
✅ **II. Security-First Architecture**: Agent receives authenticated user_id from chat infrastructure; passes to all MCP tools for user-level authorization
✅ **III. Clear Separation of Concerns**: Agent handles only NL interpretation and tool orchestration; no database, API routes, or UI logic
✅ **IV. Performance-Conscious Design**: Performance targets defined (<500ms processing); no feature additions
✅ **V. Deterministic and Reproducible Outputs**: Explicit requirement for identical inputs → identical tool invocations
✅ **VI. Stateless Server Components (Phase III)**: Agent maintains no in-memory state; receives full conversation history per request
✅ **VII. Protocol-Driven Tool Execution (Phase III)**: Agent maps intents to MCP tools; all state changes persist via tools

### Architecture & Technology Standards Compliance

✅ **Backend Stack**: Python 3.11, FastAPI infrastructure (existing)
✅ **AI Chat Agent (Phase III)**:
  - OpenAI Agents SDK (required) ✓
  - Deterministic, spec-defined interpretation rules ✓
  - No in-memory state; load conversation history per request ✓
  - Graceful error handling with user-friendly explanations ✓

### Security Requirements Compliance

✅ **Authorization Rules**:
  - AI Agent MUST NOT directly access database ✓
  - Uses MCP tools with user-level authorization ✓
  - User identity (user_id) passed to all tool invocations ✓

### Constraints Enforcement

✅ **Phase III Constraints**:
  - No changes to Phase II REST APIs (agent is separate module) ✓
  - No duplication of task business logic (uses MCP tools) ✓
  - No server-held memory across requests (stateless) ✓
  - No manual coding; Claude Code only ✓

**Gate Status**: ✅ PASSED - All constitutional requirements satisfied

## Project Structure

### Documentation (this feature)

```text
specs/004-ai-chat-agent/
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
│   ├── agent/                    # NEW: AI chat agent module
│   │   ├── __init__.py
│   │   ├── chat_agent.py         # Agent runner and orchestration
│   │   ├── intent_classifier.py  # Intent recognition logic
│   │   ├── tool_mapper.py        # MCP tool selection and invocation
│   │   └── response_formatter.py # User-facing response generation
│   ├── models/                   # Existing: Task, User models
│   ├── routers/                  # Existing: REST API routes
│   ├── services/                 # Existing: TaskService
│   ├── auth/                     # Existing: JWT dependencies
│   ├── middleware/               # Existing: logging, rate limiting
│   ├── config.py                 # Existing: settings
│   ├── database.py               # Existing: DB connection
│   └── main.py                   # Existing: FastAPI app
└── tests/
    ├── agent/                    # NEW: Agent tests
    │   ├── test_chat_agent.py
    │   ├── test_intent_classifier.py
    │   └── test_tool_mapper.py
    ├── contract/                 # Existing: API contract tests
    └── integration/              # Existing: End-to-end tests

frontend/                         # Existing: Next.js UI (no changes for this spec)
```

**Structure Decision**: Web application structure (Option 2). Agent is a new backend module under `backend/src/agent/`. Integrates with existing FastAPI backend infrastructure, models, and services. Frontend remains unchanged (chat UI is out of scope for Spec-4; covered in Spec-3 or future work).

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

N/A - No constitutional violations. All principles and constraints satisfied.

## Phase 0: Research & Technology Selection

**Objective**: Resolve all technical unknowns and validate technology choices before design.

### Research Tasks

#### R1: OpenAI Agents SDK Integration
**Question**: How to integrate OpenAI Agents SDK with FastAPI backend and MCP tools?

**Research Areas**:
- OpenAI Agents SDK installation and configuration in Python 3.11
- Agent runner setup for stateless execution (no long-lived agent instances)
- Function calling / tool use patterns in OpenAI Agents SDK
- How to pass conversation history to agent per request
- Best practices for deterministic agent behavior

**Decision Criteria**:
- SDK supports stateless agent execution
- Clear documentation for function calling with custom tools
- Compatible with Python 3.11 and async FastAPI patterns

#### R2: MCP Tool Protocol
**Question**: What is the MCP (Model Context Protocol) tool interface for this project?

**Research Areas**:
- Review Spec-5 (MCP Server, Tools & Chat Infrastructure) if available
- Understand MCP tool definition format (input schema, output schema, error handling)
- Clarify how MCP tools are invoked from the agent
- Determine if MCP tools are local functions or remote API calls

**Decision Criteria**:
- Clear interface contract for tool invocations
- Tools handle authorization (user_id validation)
- Tools return structured responses for success and errors

#### R3: Intent Classification Strategy
**Question**: Should intent recognition use prompt engineering, fine-tuned models, or keyword matching?

**Research Areas**:
- Prompt engineering patterns for intent classification with OpenAI models
- Keyword-based intent mapping (simpler, more deterministic)
- Hybrid approaches (keywords + LLM confirmation)

**Decision Criteria**:
- Deterministic behavior (constitutional requirement)
- Minimal latency (<500ms target)
- No external API calls for intent classification (use SDK model)

#### R4: Conversation History Management
**Question**: How is conversation history formatted and passed to the agent?

**Research Areas**:
- OpenAI Agents SDK conversation history format (messages array)
- Maximum conversation length handling (spec requires 50 messages)
- Message structure (role: user/assistant, content, timestamp)

**Decision Criteria**:
- Conversation format compatible with OpenAI Agents SDK
- Clear truncation strategy if conversation exceeds limits
- Spec-5 provides conversation history retrieval

#### R5: Error Handling Patterns
**Question**: How should the agent translate MCP tool errors into user-friendly messages?

**Research Areas**:
- Common error types from task operations (not found, unauthorized, validation, database)
- Mapping error codes to plain language explanations
- Preventing error details leakage (no technical stack traces to users)

**Decision Criteria**:
- Consistent error message format
- User-actionable error explanations
- No hallucination of fixes or assumptions

### Research Output

See `research.md` for detailed findings, decisions, rationale, and alternatives considered.

## Phase 1: Design & Architecture

**Prerequisites**: `research.md` complete

### Data Model

**Objective**: Define entities and schemas used by the agent (note: agent does not persist data; it only passes data to/from MCP tools).

See `data-model.md` for:
- **AgentRequest**: Input schema (user_id, message, conversation_history)
- **AgentResponse**: Output schema (response_text, tool_invocations, metadata)
- **Intent**: Enumeration of supported intents (CREATE_TASK, LIST_TASKS, COMPLETE_TASK, DELETE_TASK, UPDATE_TASK, UNKNOWN)
- **ToolInvocation**: Schema for MCP tool calls (tool_name, parameters, result)
- **ConversationMessage**: Schema for conversation history entries (role, content, timestamp)

### API Contracts

**Objective**: Define the agent's interface (invocation contract) and MCP tool contracts.

See `contracts/` for:
- **agent_interface.yaml**: How the chat infrastructure (Spec-5) invokes the agent
  - Input: `run_agent(user_id: UUID, message: str, conversation_history: List[ConversationMessage])`
  - Output: `AgentResponse(response_text: str, tool_invocations: List[ToolInvocation], metadata: dict)`

- **mcp_tools.yaml**: Expected MCP tool signatures (defined by Spec-5, documented here for reference)
  - `add_task(user_id: UUID, title: str) -> Task`
  - `list_tasks(user_id: UUID, filter: Optional[str]) -> List[Task]`
  - `complete_task(user_id: UUID, task_id: UUID) -> Task`
  - `delete_task(user_id: UUID, task_id: UUID) -> None`
  - `update_task(user_id: UUID, task_id: UUID, new_title: str) -> Task`

### Architecture Diagram

See `quickstart.md` for:
- Component interaction diagram (Chat Infrastructure → Agent → MCP Tools)
- Intent classification flow (User Message → Intent Classifier → Tool Mapper → MCP Tool → Response Formatter → User Response)
- Error handling flow (MCP Tool Error → Agent Error Handler → User-Friendly Message)
- Conversation context flow (Conversation History → Agent → Context-Aware Intent Recognition)

### Implementation Phases

**Phase 1A: Agent Core**
- Implement `ChatAgent` class with stateless runner pattern
- Integrate OpenAI Agents SDK for NL processing
- Pass conversation history to agent on each invocation
- Return structured `AgentResponse`

**Phase 1B: Intent Classification**
- Implement `IntentClassifier` with keyword-based + LLM hybrid approach
- Map user messages to Intent enum
- Extract parameters from natural language (e.g., task title from "remind me to buy milk")
- Handle ambiguous input (ask for clarification)

**Phase 1C: Tool Mapping**
- Implement `ToolMapper` to select MCP tool based on intent
- Build tool invocation payload (tool_name, user_id, extracted parameters)
- Validate parameters before tool call
- Handle tool errors gracefully

**Phase 1D: Response Formatting**
- Implement `ResponseFormatter` to generate user-friendly confirmations
- Summarize tool results conversationally (e.g., "You have 3 tasks: ...")
- Translate errors to plain language
- Prevent hallucination (all task data from tool responses only)

**Phase 1E: Integration Testing**
- Test agent with mock MCP tools
- Validate deterministic behavior (identical inputs → identical outputs)
- Test all 5 user stories from spec (create, list, complete, delete, update)
- Test edge cases (ambiguous input, errors, large conversation history)

## Phase 2: Testing & Validation

**Objective**: Validate agent behavior against spec acceptance criteria.

### Contract Tests
- Agent interface matches `agent_interface.yaml`
- Agent correctly invokes MCP tools with expected schemas
- Agent handles tool errors without crashing

### Integration Tests
- Test all 25 acceptance scenarios from spec.md
- User Story 1: Create task via NL (5 scenarios)
- User Story 2: List tasks via NL (5 scenarios)
- User Story 3: Complete task via NL (5 scenarios)
- User Story 4: Delete task via NL (5 scenarios)
- User Story 5: Update task via NL (5 scenarios)

### Edge Case Tests
- Unrelated conversational messages → friendly fallback
- Ambiguous task references → clarification request
- MCP tool errors → user-friendly error messages
- Very long task titles → passed to tool (validation at tool layer)
- Large conversation history (50+ messages) → handled gracefully

### Determinism Tests
- Identical conversation history + user message → identical tool invocation 100% of time
- No randomness in intent classification or parameter extraction
- Reproducible responses for same inputs

### Success Criteria Validation
- SC-001: 95% accuracy for task title extraction (measure via test scenarios)
- SC-002: <2 second response time for listing (measure with timer)
- SC-003: 90% success rate for unambiguous references (measure via test scenarios)
- SC-006: 100% deterministic behavior (verified via repeated tests)
- SC-007: 0% hallucination rate (verify all task data from tools only)

## Dependencies

### External Dependencies
- **OpenAI Agents SDK**: Required for agent implementation (constitutional requirement)
- **Existing Backend Infrastructure**: FastAPI, SQLModel, asyncpg (already installed)

### Internal Dependencies
- **Spec-5 (MCP Server, Tools & Chat Infrastructure)**: CRITICAL - Provides:
  - MCP tool implementations (add_task, list_tasks, complete_task, delete_task, update_task)
  - Chat API endpoint that invokes this agent
  - Conversation persistence and retrieval
  - **Dependency Type**: Blocking - Agent cannot be implemented without MCP tool contracts

- **Spec-2 (Auth & JWT Security)**: Provides authenticated user_id to chat infrastructure
- **Spec-1 (Backend API & Database)**: Provides underlying task business logic accessed by MCP tools

### Dependency Resolution Strategy
1. **Review Spec-5** (if exists) to understand MCP tool contracts before implementation
2. If Spec-5 not yet created, **define expected MCP tool interface** in `contracts/mcp_tools.yaml` and coordinate with Spec-5 planning
3. Use **mock MCP tools** for agent development and testing until real tools available
4. **Integration testing** requires Spec-5 implementation complete

## Risks & Mitigations

### Risk 1: OpenAI Agents SDK Non-Determinism
**Description**: LLM-based agents may produce non-deterministic outputs even with identical inputs.

**Likelihood**: Medium
**Impact**: High (violates constitutional requirement)

**Mitigation**:
- Use temperature=0 in OpenAI API calls for maximum determinism
- Implement keyword-based intent classification as primary strategy (deterministic)
- Use LLM only for parameter extraction and edge case handling
- Log all tool invocations for audit and reproducibility verification

### Risk 2: Spec-5 Dependency Blocking
**Description**: Agent implementation blocked if Spec-5 (MCP tools) not ready.

**Likelihood**: Medium
**Impact**: High (cannot test or integrate agent)

**Mitigation**:
- Define expected MCP tool contracts early in `contracts/mcp_tools.yaml`
- Implement mock MCP tools for agent development
- Coordinate with Spec-5 planning to align on tool interface
- Agent can be fully developed and tested with mocks before Spec-5 integration

### Risk 3: Hallucination / Data Fabrication
**Description**: Agent might generate task data instead of using tool responses.

**Likelihood**: Low
**Impact**: Critical (data integrity violation)

**Mitigation**:
- Explicit system prompt: "Never invent task data; only use tool responses"
- Implement strict response formatter that only echoes tool results
- Contract tests verify agent never returns task data without tool call
- Determinism tests catch any non-reproducible outputs

### Risk 4: Ambiguous Intent Handling
**Description**: User input may be unclear or map to multiple intents.

**Likelihood**: High
**Impact**: Medium (user frustration)

**Mitigation**:
- Implement explicit clarification requests (spec allows single follow-up)
- Provide examples in agent prompt for common phrasings
- Log ambiguous cases for continuous improvement
- Fallback to helpful error message directing user to supported operations

## Next Steps

1. ✅ **Phase 0 Complete**: Generate `research.md` with OpenAI Agents SDK integration patterns, MCP tool contracts, intent classification strategy
2. ✅ **Phase 1 Complete**: Generate `data-model.md`, `contracts/`, `quickstart.md`
3. **Ready for Tasks**: Run `/sp.tasks` to generate actionable implementation tasks
4. **Coordinate with Spec-5**: Ensure MCP tool contracts align with Spec-5 planning
5. **Implementation**: Follow tasks.md task order (agent core → intent → tools → formatting → testing)

---

**Plan Status**: ✅ COMPLETE - Ready for `/sp.tasks`
**Constitutional Compliance**: ✅ PASSED - All Phase III principles enforced
**Critical Path**: Spec-5 (MCP tools) must define tool contracts before agent integration testing
