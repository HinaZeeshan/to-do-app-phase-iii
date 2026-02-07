# Tasks: AI Chat Agent & Conversation Logic

**Input**: Design documents from `/specs/004-ai-chat-agent/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are NOT included in this implementation plan (not requested in specification).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `- [ ] [ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/src/`, `backend/tests/`
- Paths assume web app structure per plan.md

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and agent module structure

- [x] T001 Create agent module directory structure at backend/src/agent/ with __init__.py
- [x] T002 [P] Add openai>=1.0.0 dependency to backend/pyproject.toml
- [x] T003 [P] Create agent configuration file at backend/src/agent/config.py with OpenAI settings
- [x] T004 [P] Add OPENAI_API_KEY, OPENAI_MODEL, OPENAI_TEMPERATURE to backend/.env.example
- [x] T005 [P] Create Pydantic schemas file at backend/src/agent/schemas.py with AgentRequest, AgentResponse, Intent, ToolInvocation, ConversationMessage models

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure needed by all user stories

- [x] T006 Create mock MCP tools directory at backend/src/agent/mocks/__init__.py
- [x] T007 Implement mock add_task tool in backend/src/agent/mocks/mock_mcp_tools.py simulating success and error responses
- [x] T008 [P] Implement mock list_tasks tool in backend/src/agent/mocks/mock_mcp_tools.py with filter support
- [x] T009 [P] Implement mock complete_task tool in backend/src/agent/mocks/mock_mcp_tools.py
- [x] T010 [P] Implement mock delete_task tool in backend/src/agent/mocks/mock_mcp_tools.py
- [x] T011 [P] Implement mock update_task tool in backend/src/agent/mocks/mock_mcp_tools.py
- [x] T012 Create intent classifier module at backend/src/agent/intent_classifier.py with Intent enum and keyword mappings
- [x] T013 Implement keyword-based intent classification function in backend/src/agent/intent_classifier.py (primary strategy, deterministic)
- [x] T014 Implement parameter extraction logic in backend/src/agent/intent_classifier.py (extract task_title, task_id, filter from user message)
- [x] T015 Create tool mapper module at backend/src/agent/tool_mapper.py with intent-to-tool mapping
- [x] T016 Implement tool invocation function in backend/src/agent/tool_mapper.py (accepts Intent, calls appropriate mock tool, handles errors)
- [x] T017 Create response formatter module at backend/src/agent/response_formatter.py with success confirmation templates
- [x] T018 Implement error translation logic in backend/src/agent/response_formatter.py (map error types to user-friendly messages)
- [x] T019 Create main agent runner at backend/src/agent/chat_agent.py with run_agent async function skeleton
- [x] T020 Implement agent orchestration in backend/src/agent/chat_agent.py (integrate intent_classifier, tool_mapper, response_formatter)

## Phase 3: User Story 1 - Create Task via Natural Language (Priority: P1)

**Story Goal**: Users can create tasks by typing natural language commands like "remind me to buy milk"

**Independent Test Criteria**:
- Send "add a task to buy groceries" → agent invokes add_task MCP tool
- Verify task created with correct title and user ownership
- Receive confirmation message "I've added 'buy groceries' to your tasks"

### Implementation Tasks

- [x] T021 [US1] Add CREATE_TASK intent keywords to backend/src/agent/intent_classifier.py ("add", "create", "remind", "remember", "new task")
- [x] T022 [US1] Implement task title extraction in backend/src/agent/intent_classifier.py (parse title from "remind me to [title]" patterns)
- [x] T023 [US1] Map CREATE_TASK intent to add_task tool in backend/src/agent/tool_mapper.py
- [x] T024 [US1] Implement add_task tool invocation in backend/src/agent/tool_mapper.py (pass user_id and extracted title)
- [x] T025 [US1] Add success confirmation template for task creation in backend/src/agent/response_formatter.py ("I've added '[title]' to your tasks")
- [x] T026 [US1] Handle authentication errors in backend/src/agent/response_formatter.py (unauthenticated user scenario)
- [x] T027 [US1] Integrate CREATE_TASK flow in backend/src/agent/chat_agent.py run_agent function
- [x] T028 [US1] Test US1 acceptance scenario 1 (remind me to buy milk → task created with confirmation)
- [x] T029 [US1] Test US1 acceptance scenario 2 (add a task to call the dentist tomorrow → task created)
- [x] T030 [US1] Test US1 acceptance scenario 3 (remember to finish the report → task created)
- [x] T031 [US1] Test US1 acceptance scenario 4 (ambiguous command "do the thing" → accepts literal input)
- [x] T032 [US1] Test US1 acceptance scenario 5 (unauthenticated user → authentication error)

## Phase 4: User Story 2 - List Tasks via Natural Language (Priority: P1)

**Story Goal**: Users can view tasks by asking natural language questions like "what are my tasks?"

**Independent Test Criteria**:
- Create 3 tasks for user
- Send "show me my tasks" → agent invokes list_tasks MCP tool
- Verify response includes all 3 tasks with titles and completion status

### Implementation Tasks

- [x] T033 [US2] Add LIST_TASKS intent keywords to backend/src/agent/intent_classifier.py ("show", "list", "what", "pending", "completed", "what are")
- [x] T034 [US2] Implement filter extraction in backend/src/agent/intent_classifier.py (detect "pending", "completed", "all")
- [x] T035 [US2] Map LIST_TASKS intent to list_tasks tool in backend/src/agent/tool_mapper.py
- [x] T036 [US2] Implement list_tasks tool invocation in backend/src/agent/tool_mapper.py (pass user_id and optional filter)
- [x] T037 [US2] Add task list formatting in backend/src/agent/response_formatter.py (conversational summary: "You have 3 tasks: ...")
- [x] T038 [US2] Handle empty task list in backend/src/agent/response_formatter.py ("You don't have any tasks yet")
- [x] T039 [US2] Integrate LIST_TASKS flow in backend/src/agent/chat_agent.py run_agent function
- [x] T040 [US2] Test US2 acceptance scenario 1 (3 pending tasks → agent lists all 3 with status)
- [x] T041 [US2] Test US2 acceptance scenario 2 (no tasks → "You don't have any tasks yet")
- [x] T042 [US2] Test US2 acceptance scenario 3 (show me my pending tasks → filters correctly)
- [x] T043 [US2] Test US2 acceptance scenario 4 (what do I need to do → conversational summary)
- [x] T044 [US2] Test US2 acceptance scenario 5 (unauthenticated user → authentication error)

## Phase 5: User Story 3 - Complete Task via Natural Language (Priority: P2)

**Story Goal**: Users can mark tasks as complete by saying "I finished buying milk"

**Independent Test Criteria**:
- Create task "buy milk"
- Send "I finished buying milk" → agent invokes complete_task MCP tool
- Verify task status updated to completed

### Implementation Tasks

- [x] T045 [US3] Add COMPLETE_TASK intent keywords to backend/src/agent/intent_classifier.py ("done", "complete", "finished", "mark")
- [x] T046 [US3] Implement task reference extraction in backend/src/agent/intent_classifier.py (partial title matching from conversation context)
- [x] T047 [US3] Add task matching logic in backend/src/agent/intent_classifier.py (find task_id by partial title match)
- [x] T048 [US3] Map COMPLETE_TASK intent to complete_task tool in backend/src/agent/tool_mapper.py
- [x] T049 [US3] Implement complete_task tool invocation in backend/src/agent/tool_mapper.py (pass user_id and matched task_id)
- [x] T050 [US3] Add completion confirmation template in backend/src/agent/response_formatter.py ("Great! I've marked '[title]' as done")
- [x] T051 [US3] Handle task not found error in backend/src/agent/response_formatter.py ("I couldn't find a task matching '[reference]'")
- [x] T052 [US3] Handle ambiguous task references in backend/src/agent/response_formatter.py (ask "Which task did you mean: ...")
- [x] T053 [US3] Integrate COMPLETE_TASK flow in backend/src/agent/chat_agent.py run_agent function
- [x] T054 [US3] Test US3 acceptance scenario 1 (I finished buying milk → task marked complete)
- [x] T055 [US3] Test US3 acceptance scenario 2 (mark the dentist task as done → partial match works)
- [x] T056 [US3] Test US3 acceptance scenario 3 (done with milk → abbreviated reference works)
- [x] T057 [US3] Test US3 acceptance scenario 4 (mark 'walk the dog' as done → task not found error)
- [x] T058 [US3] Test US3 acceptance scenario 5 (ambiguous reference → clarification question)

## Phase 6: User Story 4 - Delete Task via Natural Language (Priority: P2)

**Story Goal**: Users can delete tasks by saying "remove 'buy milk'"

**Independent Test Criteria**:
- Create task "buy milk"
- Send "delete the milk task" → agent invokes delete_task MCP tool
- Verify task removed from database

### Implementation Tasks

- [x] T059 [US4] Add DELETE_TASK intent keywords to backend/src/agent/intent_classifier.py ("delete", "remove", "cancel")
- [x] T060 [US4] Reuse task reference extraction logic for DELETE_TASK in backend/src/agent/intent_classifier.py
- [x] T061 [US4] Map DELETE_TASK intent to delete_task tool in backend/src/agent/tool_mapper.py
- [x] T062 [US4] Implement delete_task tool invocation in backend/src/agent/tool_mapper.py (pass user_id and matched task_id)
- [x] T063 [US4] Add deletion confirmation template in backend/src/agent/response_formatter.py ("I've deleted '[title]'")
- [x] T064 [US4] Reuse task not found error handling for DELETE_TASK in backend/src/agent/response_formatter.py
- [x] T065 [US4] Reuse ambiguous task reference handling for DELETE_TASK in backend/src/agent/response_formatter.py
- [x] T066 [US4] Integrate DELETE_TASK flow in backend/src/agent/chat_agent.py run_agent function
- [x] T067 [US4] Test US4 acceptance scenario 1 (delete the milk task → task deleted with confirmation)
- [x] T068 [US4] Test US4 acceptance scenario 2 (remove 'buy milk' → task deleted)
- [x] T069 [US4] Test US4 acceptance scenario 3 (delete 'walk the dog' → task not found)
- [x] T070 [US4] Test US4 acceptance scenario 4 (ambiguous reference → clarification before deletion)
- [x] T071 [US4] Test US4 acceptance scenario 5 (unauthenticated user → authentication error)

## Phase 7: User Story 5 - Update Task via Natural Language (Priority: P3)

**Story Goal**: Users can update task details by saying "change 'buy milk' to 'buy almond milk'"

**Independent Test Criteria**:
- Create task "buy milk"
- Send "change it to 'buy almond milk'" → agent invokes update_task MCP tool
- Verify task title updated in database

### Implementation Tasks

- [x] T072 [US5] Add UPDATE_TASK intent keywords to backend/src/agent/intent_classifier.py ("change", "update", "rename", "modify")
- [x] T073 [US5] Implement new title extraction in backend/src/agent/intent_classifier.py (parse "change [old] to [new]" patterns)
- [x] T074 [US5] Handle context-aware references in backend/src/agent/intent_classifier.py ("change it to ..." uses most recent task)
- [x] T075 [US5] Map UPDATE_TASK intent to update_task tool in backend/src/agent/tool_mapper.py
- [x] T076 [US5] Implement update_task tool invocation in backend/src/agent/tool_mapper.py (pass user_id, task_id, new_title)
- [x] T077 [US5] Add update confirmation template in backend/src/agent/response_formatter.py ("I've updated the task to '[new_title]'")
- [x] T078 [US5] Handle validation error for empty title in backend/src/agent/response_formatter.py ("Titles cannot be empty")
- [x] T079 [US5] Reuse task not found and ambiguous reference handling for UPDATE_TASK
- [x] T080 [US5] Integrate UPDATE_TASK flow in backend/src/agent/chat_agent.py run_agent function
- [x] T081 [US5] Test US5 acceptance scenario 1 (change 'buy milk' to 'buy almond milk' → task updated)
- [x] T082 [US5] Test US5 acceptance scenario 2 (change it to 'buy oat milk' → context-aware update)
- [x] T083 [US5] Test US5 acceptance scenario 3 (update 'walk the dog' → task not found)
- [x] T084 [US5] Test US5 acceptance scenario 4 (ambiguous reference → clarification before update)
- [x] T085 [US5] Test US5 acceptance scenario 5 (empty new title → validation error)

## Phase 8: Edge Cases & Polish

**Purpose**: Handle edge cases and improve agent robustness

- [x] T086 Handle unrelated conversational messages in backend/src/agent/response_formatter.py (friendly fallback: "I'm here to help manage your tasks. What would you like to do?")
- [x] T087 Implement conversation history truncation in backend/src/agent/chat_agent.py (max 50 messages or 5k tokens)
- [x] T088 Add LLM fallback for unrecognized intents in backend/src/agent/intent_classifier.py (temperature=0, only if keyword matching fails)
- [x] T089 Implement malformed input handling in backend/src/agent/intent_classifier.py (friendly error: "I'm not sure what you'd like me to do...")
- [x] T090 Handle MCP tool database errors in backend/src/agent/response_formatter.py ("I'm having trouble accessing your tasks right now. Please try again in a moment.")
- [x] T091 Add logging for all tool invocations in backend/src/agent/tool_mapper.py (audit trail: intent, tool_name, parameters, result/error, duration_ms)
- [x] T092 Add processing time tracking in backend/src/agent/chat_agent.py (target <500ms, log slow requests)
- [x] T093 Implement determinism validation in backend/src/agent/chat_agent.py (verify identical inputs → identical outputs)
- [x] T094 Add performance monitoring to backend/src/agent/chat_agent.py (track agent processing time, log metrics)

## Phase 9: Integration & Validation

**Purpose**: End-to-end validation and integration with Spec-5

- [x] T095 Create integration test suite at backend/tests/agent/test_chat_agent.py for all 25 acceptance scenarios
- [x] T096 Run determinism tests (identical request 10 times → verify identical responses)
- [x] T097 Run performance tests (measure agent processing time, target <500ms)
- [x] T098 Validate edge case handling (unrelated messages, large conversation history, malformed input, tool errors)
- [x] T099 Document agent interface for Spec-5 integration in specs/004-ai-chat-agent/contracts/agent_interface.yaml (already created)
- [x] T100 Coordinate MCP tool contracts with Spec-5 team using specs/004-ai-chat-agent/contracts/mcp_tools.yaml
- [x] T101 Create mock-to-real MCP tools migration guide in specs/004-ai-chat-agent/quickstart.md (integration instructions)
- [x] T102 Validate all constitutional requirements (stateless, deterministic, no direct DB access, protocol-driven)

## Dependencies & Execution Order

### User Story Dependencies

```
Phase 1: Setup (T001-T005) ───────┐
                                   │
Phase 2: Foundational (T006-T020) ├─── BLOCKING: Must complete before user stories
                                   │
                ┌──────────────────┘
                │
                ├── Phase 3: US1 - Create Task (T021-T032) ──┐
                │                                             │
                ├── Phase 4: US2 - List Tasks (T033-T044) ───┤── Independent (can implement in any order)
                │                                             │
                ├── Phase 5: US3 - Complete Task (T045-T058) │
                │                                             │
                ├── Phase 6: US4 - Delete Task (T059-T071) ──┤
                │                                             │
                └── Phase 7: US5 - Update Task (T072-T085) ──┘
                                   │
                                   │
Phase 8: Edge Cases & Polish (T086-T094) ─── Can run after any user story completes
                                   │
                                   │
Phase 9: Integration & Validation (T095-T102) ─── Final validation, requires all phases

```

### Story Completion Order

**MVP Scope** (minimum viable product):
- Phase 1: Setup (T001-T005)
- Phase 2: Foundational (T006-T020)
- Phase 3: US1 - Create Task (T021-T032)
- Phase 4: US2 - List Tasks (T033-T044)

This delivers the core read-write cycle needed for basic task management via natural language.

**Recommended Order** (priority-based):
1. Phase 1 & 2: Setup + Foundational (BLOCKING)
2. Phase 3: US1 - Create Task (P1)
3. Phase 4: US2 - List Tasks (P1)
4. Phase 5: US3 - Complete Task (P2)
5. Phase 6: US4 - Delete Task (P2)
6. Phase 7: US5 - Update Task (P3)
7. Phase 8: Edge Cases & Polish
8. Phase 9: Integration & Validation

### Parallel Execution Examples

**Phase 1 (Setup) Parallelization**:
```bash
# All setup tasks can run in parallel after T001 completes
T001 (create directory) → then parallel: T002, T003, T004, T005
```

**Phase 2 (Foundational) Parallelization**:
```bash
# Mock tools can be implemented in parallel after T006-T007
T006-T007 (mock infrastructure) → then parallel: T008, T009, T010, T011

# Core modules are sequential (dependencies)
T012 → T013 → T014 (intent_classifier)
T015 → T016 (tool_mapper, depends on intent_classifier)
T017 → T018 (response_formatter, independent)
T019 → T020 (chat_agent, depends on all above)
```

**User Story Phases (US1-US5) Parallelization**:
```bash
# Within each user story, tasks are mostly sequential
# But DIFFERENT user stories can be implemented in parallel by different developers

Example: 3 developers working in parallel
Developer 1: T021-T032 (US1 - Create Task)
Developer 2: T033-T044 (US2 - List Tasks)
Developer 3: T045-T058 (US3 - Complete Task)
```

## Implementation Strategy

### MVP-First Approach

**Iteration 1** (MVP - Basic Read/Write):
- Phase 1: Setup (T001-T005)
- Phase 2: Foundational (T006-T020)
- Phase 3: US1 - Create Task (T021-T032)
- Phase 4: US2 - List Tasks (T033-T044)

**Deliverable**: Agent can create and list tasks via natural language. Users can test basic functionality.

**Iteration 2** (Task Lifecycle Management):
- Phase 5: US3 - Complete Task (T045-T058)
- Phase 6: US4 - Delete Task (T059-T071)

**Deliverable**: Agent supports full CRUD operations minus update. Users can manage task lifecycle.

**Iteration 3** (Full Feature Set):
- Phase 7: US5 - Update Task (T072-T085)
- Phase 8: Edge Cases & Polish (T086-T094)

**Deliverable**: Complete agent with all 5 operations and robust error handling.

**Iteration 4** (Production Ready):
- Phase 9: Integration & Validation (T095-T102)

**Deliverable**: Production-ready agent integrated with Spec-5, all tests passing, performance validated.

### Independent Testing Per Story

Each user story phase includes its own acceptance tests, enabling:
- **Incremental delivery**: Ship US1+US2 as MVP without waiting for US3-US5
- **Parallel development**: Different developers implement different stories simultaneously
- **Independent validation**: Each story can be tested and validated separately
- **Risk mitigation**: Issues in one story don't block others

### Success Criteria

- ✅ All 5 user stories implemented and tested
- ✅ 25 acceptance scenarios passing (5 per user story)
- ✅ Edge cases handled (unrelated messages, errors, large conversations)
- ✅ Determinism validated (identical inputs → identical outputs 100%)
- ✅ Performance targets met (<500ms agent processing time)
- ✅ Constitutional compliance (stateless, no direct DB access, protocol-driven)
- ✅ Integration with Spec-5 documented and validated

## Total Task Count

- **Phase 1 (Setup)**: 5 tasks
- **Phase 2 (Foundational)**: 15 tasks
- **Phase 3 (US1)**: 12 tasks
- **Phase 4 (US2)**: 12 tasks
- **Phase 5 (US3)**: 14 tasks
- **Phase 6 (US4)**: 13 tasks
- **Phase 7 (US5)**: 14 tasks
- **Phase 8 (Edge Cases)**: 9 tasks
- **Phase 9 (Integration)**: 8 tasks

**Total**: 102 tasks

**Parallel Opportunities**: 15 tasks marked [P] (can run in parallel within their phase)

**Independent User Stories**: 5 stories (US1-US5) that can be implemented in parallel by different developers after Phase 2 completes
