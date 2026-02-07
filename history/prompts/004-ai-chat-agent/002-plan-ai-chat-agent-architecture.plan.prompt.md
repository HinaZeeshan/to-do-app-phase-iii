---
id: 002
title: Plan AI Chat Agent Architecture
stage: plan
date: 2026-02-07
surface: agent
model: claude-sonnet-4-5-20250929
feature: 004-ai-chat-agent
branch: 004-ai-chat-agent
user: user
command: /sp.plan
labels: ["plan", "ai-chat-agent", "phase-iii", "openai-agents-sdk", "mcp-tools", "architecture"]
links:
  spec: specs/004-ai-chat-agent/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/004-ai-chat-agent/plan.md
  - specs/004-ai-chat-agent/research.md
  - specs/004-ai-chat-agent/data-model.md
  - specs/004-ai-chat-agent/contracts/agent_interface.yaml
  - specs/004-ai-chat-agent/contracts/mcp_tools.yaml
  - specs/004-ai-chat-agent/quickstart.md
tests:
  - N/A (planning phase)
---

## Prompt

```text
before planning first review the frontend and backend folder then generate plan here is detail about /sp.plan

Spec: Spec-4 – AI Chat Agent & Conversation Logic

Goal:
Design and validate an AI-powered chat agent that interprets natural language todo commands and reliably converts them into MCP tool calls without direct data access or UI responsibility.

Planning principles:
- Spec-driven development (no implementation leakage)
- Deterministic agent behavior
- Clear separation of concerns
- Tool-first execution model

Plan:

Phase 1: Agent Role Definition
- Define the agent's single responsibility: intent interpretation and orchestration
- Explicitly prohibit database, API, or UI logic
- Establish stateless execution rules (full context per request)
- Define boundaries between agent reasoning and MCP execution

Phase 2: Intent Taxonomy
- Identify supported user intents:
  - Create task
  - List tasks
  - Update task
  - Complete task
  - Delete task
- Define required and optional parameters for each intent
- Define fallback behavior for unsupported or ambiguous intents

Phase 3: MCP Tool Mapping
- Map each intent to exactly one MCP tool
- Define strict input schema for every tool invocation
- Specify rules for parameter validation before tool calls
- Ensure agent never mutates state outside MCP tools

Phase 4: Conversation Flow Design
- Define how the agent handles:
  - Missing parameters
  - Ambiguous user input
  - Confirmation requests
- Specify when to ask follow-up questions
- Define confirmation response format after successful execution

Phase 5: Error Handling Strategy
- Define recoverable vs non-recoverable errors
- Standardize error explanations in user-friendly language
- Prevent hallucinated fixes or assumptions
- Ensure errors never trigger unintended tool calls

Phase 6: Determinism & Safety
- Enforce deterministic outputs for identical inputs
- Disable creative rewriting of user intent
- Require explicit user intent before destructive actions
- Prevent multi-tool execution per request

Phase 7: Validation Scenarios
- Define test conversations for each intent
- Include edge cases:
  - Invalid task references
  - Ambiguous intents
  - Large conversation histories
  - Error conditions
```

## Response snapshot

Successfully created comprehensive implementation plan for Spec-4: AI Chat Agent & Conversation Logic.

**Planning Artifacts Created**:

1. **plan.md** - Complete implementation plan with:
   - Summary: Stateless AI agent using OpenAI Agents SDK for NL interpretation → MCP tool invocation
   - Technical Context: Python 3.11, OpenAI Agents SDK, FastAPI infrastructure, <500ms processing target
   - Constitution Check: ✅ PASSED all Phase III principles (stateless, deterministic, protocol-driven)
   - Project Structure: New `backend/src/agent/` module (chat_agent, intent_classifier, tool_mapper, response_formatter)
   - Phase 0: 5 research tasks (OpenAI SDK integration, MCP protocol, intent classification, conversation history, error handling)
   - Phase 1: 5 implementation phases (agent core, intent classification, tool mapping, response formatting, integration testing)
   - Dependencies: Spec-5 (CRITICAL - MCP tools), Spec-2 (auth), Spec-1 (backend)
   - Risks: OpenAI SDK non-determinism, Spec-5 blocking, hallucination, ambiguous intents (all mitigated)

2. **research.md** - Phase 0 research findings with decisions:
   - R1: OpenAI Agents SDK - Use `openai` library with function calling, temperature=0 for determinism
   - R2: MCP Tool Protocol - Define contracts, use mock tools for independent development
   - R3: Intent Classification - Hybrid keyword matching (deterministic) + LLM fallback (temperature=0)
   - R4: Conversation History - OpenAI format, truncate at 50 messages or 5k tokens
   - R5: Error Handling - User-friendly error mapping with technical logging

3. **data-model.md** - Entity schemas:
   - AgentRequest: Input (user_id, message, conversation_history)
   - AgentResponse: Output (response_text, tool_invocations, metadata)
   - Intent: Enum (CREATE_TASK, LIST_TASKS, COMPLETE_TASK, DELETE_TASK, UPDATE_TASK, UNKNOWN)
   - ToolInvocation: MCP tool call record (tool_name, parameters, result, error, duration_ms)
   - ConversationMessage: History entry (role, content, timestamp)
   - IntentClassificationResult: Internal (intent, confidence, extracted_params, clarification_question)

4. **contracts/agent_interface.yaml** - Agent invocation contract:
   - Input: run_agent(user_id, message, conversation_history)
   - Output: AgentResponse with response_text, tool_invocations, metadata
   - Performance targets: <500ms processing, <2s end-to-end
   - Determinism guarantee: identical inputs → identical outputs 100%

5. **contracts/mcp_tools.yaml** - Expected MCP tool contracts (for Spec-5 coordination):
   - add_task(user_id, title) → Task
   - list_tasks(user_id, filter?) → List[Task]
   - complete_task(user_id, task_id) → Task
   - delete_task(user_id, task_id) → None
   - update_task(user_id, task_id, new_title) → Task
   - Authorization: All tools validate user_id matches authenticated user

6. **quickstart.md** - Architecture overview:
   - Component diagram: Chat Infrastructure → Agent (Intent Classifier → Tool Mapper → Response Formatter) → MCP Tools
   - Intent classification flow: User message → Keyword matching → LLM fallback → Parameter extraction
   - Error handling flow: MCP tool error → Error handler → User-friendly translation
   - Conversation context flow: History → Context-aware intent recognition → Tool invocation
   - Module structure: backend/src/agent/ with 4 core modules + schemas + config + mocks
   - Implementation phases: 1A (core) → 1B (intent) → 1C (tools) → 1D (formatting) → 1E (testing)

**Key Architecture Decisions**:

1. **OpenAI Agents SDK Integration**:
   - Use `openai` Python library with chat completions API
   - Function calling mechanism for MCP tool invocation
   - Temperature=0 for maximum determinism
   - Stateless execution (no long-lived agent instances)

2. **Intent Classification Strategy**:
   - Primary: Keyword matching (deterministic, fast)
   - Fallback: LLM classification (temperature=0, non-determinism minimized)
   - Hybrid approach balances flexibility with constitutional determinism requirement

3. **MCP Tool Abstraction**:
   - Agent never directly accesses database (constitutional requirement)
   - All task operations via MCP tools (add, list, complete, delete, update)
   - Mock tools enable independent agent development before Spec-5 integration

4. **Stateless Architecture**:
   - Agent maintains no in-memory state between requests
   - Conversation history passed per request (from Spec-5)
   - Fresh agent runner created for each invocation

5. **Error Handling**:
   - User-friendly error mapping (no technical details exposed)
   - Structured logging for debugging (full error context preserved)
   - No hallucination of fixes or assumptions

**Constitutional Compliance Verification**:

✅ **I. Spec-Driven Development**: Plan follows spec.md with no implementation leakage
✅ **II. Security-First Architecture**: Agent receives authenticated user_id; passes to all MCP tools
✅ **III. Clear Separation of Concerns**: Agent handles only NL interpretation and tool orchestration
✅ **IV. Performance-Conscious Design**: <500ms processing target; no feature additions
✅ **V. Deterministic and Reproducible Outputs**: Temperature=0, keyword-first classification, determinism tests
✅ **VI. Stateless Server Components**: No in-memory state; full conversation history per request
✅ **VII. Protocol-Driven Tool Execution**: Intent → MCP tool mapping; all state changes persist via tools

**Backend Review Summary**:
- Existing backend: FastAPI (Python 3.11), SQLModel, asyncpg, Neon PostgreSQL
- Task API: TaskService with CRUD operations (list, create, complete, delete, update)
- Auth: JWT-based with get_current_user_id dependency
- Middleware: Logging, rate limiting, request ID, error handling
- Agent will integrate as new `backend/src/agent/` module (no changes to existing routes)

**Frontend Review Summary**:
- Next.js 16 with App Router, TypeScript
- Tasks page: useTasks hook for CRUD operations
- Auth: useAuth hook for JWT management
- UI: TaskList, TaskForm, LoadingSpinner, Button components
- Chat UI out of scope for Spec-4 (covered in Spec-3 or future work)

**Critical Dependency**:
- **Spec-5 (MCP Server, Tools & Chat Infrastructure)** is BLOCKING for integration testing
- Mitigation: Define MCP tool contracts now, use mock tools for agent development
- Agent can be fully developed and tested with mocks before Spec-5 integration

## Outcome

- ✅ Impact: Complete implementation plan with 6 design artifacts (plan, research, data-model, 2 contracts, quickstart)
- 🧪 Tests: 25 acceptance scenarios defined, determinism tests specified, performance targets set
- 📁 Files: 6 files created (plan.md, research.md, data-model.md, agent_interface.yaml, mcp_tools.yaml, quickstart.md)
- 🔁 Next prompts: Run /sp.tasks to generate actionable implementation tasks, coordinate MCP tool contracts with Spec-5
- 🧠 Reflection: Plan successfully balances determinism (constitutional requirement) with flexibility (NL understanding). Hybrid intent classification (keyword + LLM) and mock tools enable independent development while maintaining architectural alignment with Spec-5.

## Evaluation notes (flywheel)

- Failure modes observed: None - planning followed constitutional guidelines and spec requirements
- Graders run and results (PASS/FAIL): Constitution Check validation - PASS (all Phase III principles satisfied)
- Prompt variant (if applicable): Standard /sp.plan command with architecture guidance
- Next experiment (smallest change to try): Monitor Spec-5 planning for MCP tool contract alignment; adjust contracts if needed before implementation
