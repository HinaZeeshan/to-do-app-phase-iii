# Quickstart Guide: AI Chat Agent & Conversation Logic

**Date**: 2026-02-07
**Feature**: 004-ai-chat-agent
**Audience**: Developers implementing the AI chat agent

## Overview

The AI Chat Agent interprets natural language todo commands and converts them into MCP tool invocations. The agent is stateless, deterministic, and exclusively uses MCP tools for all task operations.

**Key Characteristics**:
- Stateless: No in-memory state between requests
- Deterministic: Identical inputs → identical outputs
- Protocol-driven: Uses MCP tools exclusively (no direct database access)
- Secure: Passes authenticated user_id to all tools

## Architecture

### Component Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    Spec-5: Chat Infrastructure                  │
│  - Conversation persistence (database)                          │
│  - Conversation retrieval                                       │
│  - Chat API endpoint                                            │
│  - MCP tool implementations                                     │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     │ run_agent(user_id, message, history)
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                    AI Chat Agent (Spec-4)                       │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  1. Intent Classifier                                      │ │
│  │     - Keyword matching (deterministic)                     │ │
│  │     - LLM fallback (temperature=0)                         │ │
│  │     - Parameter extraction                                 │ │
│  └──────────────────┬─────────────────────────────────────────┘ │
│                     │ Intent + extracted params                  │
│                     ▼                                            │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  2. Tool Mapper                                            │ │
│  │     - Map intent to MCP tool                               │ │
│  │     - Build tool invocation (tool_name, params)            │ │
│  │     - Validate parameters                                  │ │
│  └──────────────────┬─────────────────────────────────────────┘ │
│                     │ MCP tool call                              │
│                     ▼                                            │
└─────────────────────┼────────────────────────────────────────────┘
                      │
                      │ add_task / list_tasks / complete_task /
                      │ delete_task / update_task
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│              MCP Tools (Spec-5) + TaskService (Spec-1)          │
│  - add_task(user_id, title) → Task                             │
│  - list_tasks(user_id, filter) → List[Task]                    │
│  - complete_task(user_id, task_id) → Task                      │
│  - delete_task(user_id, task_id) → None                        │
│  - update_task(user_id, task_id, new_title) → Task             │
│                                                                 │
│  Authorization: Validate user_id matches authenticated user    │
│  Execution: Call TaskService business logic                    │
│  Persistence: Database operations via SQLModel                 │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     │ Tool result or error
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                    AI Chat Agent (Spec-4)                       │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  3. Response Formatter                                     │ │
│  │     - Format tool result conversationally                  │ │
│  │     - Translate errors to user-friendly messages           │ │
│  │     - Prevent hallucination (data from tools only)         │ │
│  └──────────────────┬─────────────────────────────────────────┘ │
│                     │ AgentResponse                              │
│                     ▼                                            │
└─────────────────────┼────────────────────────────────────────────┘
                      │
                      │ response_text, tool_invocations, metadata
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Spec-5: Chat Infrastructure                  │
│  - Persist assistant message to database                       │
│  - Return response_text to user                                │
└─────────────────────────────────────────────────────────────────┘
```

### Intent Classification Flow

```
User Message: "remind me to buy milk"
     │
     ▼
┌─────────────────────────────────────────┐
│  Keyword Matching (Primary Strategy)   │
│  - Check for: add, create, remind, ... │
│  - Match found: CREATE_TASK             │
└─────────────┬───────────────────────────┘
              │
              ▼ (if no match)
┌─────────────────────────────────────────┐
│  LLM Classification (Fallback)          │
│  - temperature=0 for determinism        │
│  - Classify intent via OpenAI API       │
└─────────────┬───────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────┐
│  Parameter Extraction                   │
│  - Extract task_title: "buy milk"       │
│  - Extract task_id: (if mentioned)      │
│  - Extract filter: (if mentioned)       │
└─────────────┬───────────────────────────┘
              │
              ▼
    IntentClassificationResult
    {
      intent: CREATE_TASK,
      confidence: 0.95,
      extracted_params: {
        task_title: "buy milk"
      }
    }
```

### Error Handling Flow

```
MCP Tool Error: TaskNotFoundError
     │
     ▼
┌─────────────────────────────────────────┐
│  Error Handler in Tool Mapper           │
│  - Catch exception from MCP tool        │
│  - Extract error type and details       │
└─────────────┬───────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────┐
│  Error Translation (Response Formatter) │
│  - Map TaskNotFoundError to message     │
│  - User-friendly: "I couldn't find..."  │
│  - No technical details exposed         │
└─────────────┬───────────────────────────┘
              │
              ▼
    AgentResponse
    {
      response_text: "I couldn't find a task matching 'buy milk'",
      tool_invocations: [
        {
          tool_name: "complete_task",
          error: "TaskNotFoundError",
          ...
        }
      ]
    }
```

### Conversation Context Flow

```
Conversation History: [
  {role: "user", content: "remind me to buy milk"},
  {role: "assistant", content: "I've added 'buy milk' to your tasks"},
  {role: "user", content: "actually, change it to almond milk"}
]
     │
     ▼
┌─────────────────────────────────────────┐
│  Intent Classifier with Context         │
│  - Recognize "change it" refers to      │
│    most recent task ("buy milk")        │
│  - Extract task_id from conversation    │
│  - Intent: UPDATE_TASK                  │
└─────────────┬───────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────┐
│  Tool Mapper                             │
│  - Tool: update_task                     │
│  - Parameters:                           │
│    user_id: (from auth)                  │
│    task_id: (from conversation)          │
│    new_title: "almond milk"              │
└─────────────┬───────────────────────────┘
              │
              ▼
    MCP Tool Invocation
```

## Module Structure

### Directory Layout

```
backend/src/agent/
├── __init__.py                    # Module exports
├── chat_agent.py                  # Main agent runner (run_agent function)
├── intent_classifier.py           # Intent recognition logic
├── tool_mapper.py                 # MCP tool selection and invocation
├── response_formatter.py          # User-facing response generation
├── schemas.py                     # Pydantic models (AgentRequest, AgentResponse, etc.)
├── config.py                      # Agent configuration (OpenAI API key, system prompts)
└── mocks/
    └── mock_mcp_tools.py          # Mock MCP tools for testing

backend/tests/agent/
├── test_chat_agent.py             # Integration tests for run_agent
├── test_intent_classifier.py      # Unit tests for intent classification
├── test_tool_mapper.py            # Unit tests for tool mapping
└── test_response_formatter.py     # Unit tests for response formatting
```

### Module Responsibilities

**chat_agent.py**:
- Exports `run_agent(user_id, message, conversation_history) -> AgentResponse`
- Orchestrates intent classifier, tool mapper, response formatter
- Handles top-level errors and logging
- Stateless: creates fresh components on each invocation

**intent_classifier.py**:
- Exports `classify_intent(message, conversation_history) -> IntentClassificationResult`
- Implements keyword matching (primary strategy)
- Falls back to LLM classification (temperature=0)
- Extracts parameters from user message

**tool_mapper.py**:
- Exports `invoke_tool(intent, params, user_id) -> ToolInvocation`
- Maps Intent enum to MCP tool name
- Builds tool invocation payload
- Executes MCP tool and captures result or error

**response_formatter.py**:
- Exports `format_response(tool_invocation) -> str`
- Generates conversational confirmations for success
- Translates errors to user-friendly messages
- Prevents hallucination (data from tool responses only)

**schemas.py**:
- Defines Pydantic models: `AgentRequest`, `AgentResponse`, `Intent`, `ToolInvocation`, etc.
- Provides validation and serialization

**config.py**:
- Agent configuration: OpenAI API key, model name, system prompts
- Intent keyword mappings
- Error message templates

## Implementation Phases

### Phase 1A: Agent Core
1. Create `backend/src/agent/` directory
2. Implement `schemas.py` with Pydantic models
3. Implement `chat_agent.py` with `run_agent()` function skeleton
4. Implement `config.py` with configuration settings
5. Test: Agent accepts AgentRequest and returns AgentResponse (mock internals)

### Phase 1B: Intent Classification
1. Implement `intent_classifier.py` with keyword matching
2. Implement LLM fallback (OpenAI API, temperature=0)
3. Implement parameter extraction logic
4. Test: Verify deterministic intent classification for all 5 intents

### Phase 1C: Tool Mapping
1. Create `mocks/mock_mcp_tools.py` with mock tool implementations
2. Implement `tool_mapper.py` with intent-to-tool mapping
3. Implement tool invocation with mock tools
4. Test: Verify correct tool selection and parameter passing

### Phase 1D: Response Formatting
1. Implement `response_formatter.py` with confirmation templates
2. Implement error translation logic
3. Test: Verify user-friendly messages for all success/error scenarios

### Phase 1E: Integration Testing
1. Test all 25 acceptance scenarios from spec.md
2. Test edge cases (ambiguous input, errors, large conversation history)
3. Test determinism (identical inputs → identical outputs, 10 iterations)
4. Test performance (<500ms agent processing time)

## Configuration

### Environment Variables

Add to `.env`:
```bash
# OpenAI API Configuration
OPENAI_API_KEY=sk-...your-api-key...
OPENAI_MODEL=gpt-4
OPENAI_TEMPERATURE=0.0  # Maximum determinism

# Agent Configuration
AGENT_MAX_CONVERSATION_MESSAGES=50
AGENT_MAX_MESSAGE_LENGTH=2000
AGENT_PROCESSING_TIMEOUT_MS=500
```

### Dependencies

Add to `backend/pyproject.toml`:
```toml
dependencies = [
    # ... existing dependencies ...
    "openai>=1.0.0",  # OpenAI Python SDK
]
```

## Testing Strategy

### Unit Tests
- `test_intent_classifier.py`: Test keyword matching, LLM fallback, parameter extraction
- `test_tool_mapper.py`: Test intent-to-tool mapping, mock tool invocation
- `test_response_formatter.py`: Test success messages, error translations

### Integration Tests
- `test_chat_agent.py`: Test `run_agent()` with mock MCP tools
- Test all 25 acceptance scenarios from spec.md
- Test edge cases and error scenarios

### Determinism Tests
- Run identical request 10 times
- Verify response_text is identical
- Verify tool_invocations are identical
- Fail test if any non-determinism detected

### Performance Tests
- Measure agent processing time (exclude MCP tool latency)
- Target: <500ms for typical requests
- Log slow requests for optimization

## Usage Example

### Basic Usage

```python
from backend.src.agent.chat_agent import run_agent
from uuid import UUID

# Example 1: Create task
response = await run_agent(
    user_id=UUID("123e4567-e89b-12d3-a456-426614174000"),
    message="remind me to buy milk",
    conversation_history=[]
)
print(response.response_text)
# Output: "I've added 'buy milk' to your tasks"

# Example 2: List tasks
response = await run_agent(
    user_id=UUID("123e4567-e89b-12d3-a456-426614174000"),
    message="what are my tasks?",
    conversation_history=[
        {"role": "user", "content": "remind me to buy milk"},
        {"role": "assistant", "content": "I've added 'buy milk' to your tasks"}
    ]
)
print(response.response_text)
# Output: "You have 1 task: buy milk"

# Example 3: Complete task with context
response = await run_agent(
    user_id=UUID("123e4567-e89b-12d3-a456-426614174000"),
    message="mark it as done",
    conversation_history=[
        {"role": "user", "content": "remind me to buy milk"},
        {"role": "assistant", "content": "I've added 'buy milk' to your tasks"}
    ]
)
print(response.response_text)
# Output: "Great! I've marked 'buy milk' as done"
```

### Error Handling

```python
# Task not found error
response = await run_agent(
    user_id=UUID("123e4567-e89b-12d3-a456-426614174000"),
    message="mark 'walk the dog' as done",
    conversation_history=[]
)
print(response.response_text)
# Output: "I couldn't find a task matching 'walk the dog'"

# Check tool invocation for debugging
print(response.tool_invocations[0].error)
# Output: "TaskNotFoundError"
```

## Coordination with Spec-5

### Critical Dependencies
- **MCP Tool Implementations**: Spec-5 must implement actual MCP tools (add_task, list_tasks, etc.)
- **Chat API Endpoint**: Spec-5 must provide endpoint that invokes `run_agent()`
- **Conversation Persistence**: Spec-5 must persist and retrieve conversation history

### Development Strategy
1. **Agent Development** (Spec-4): Use mock MCP tools for independent development
2. **MCP Tool Contracts**: Define expected tool interface in `contracts/mcp_tools.yaml`
3. **Coordination**: Share contracts with Spec-5 team for alignment
4. **Integration**: Replace mock tools with real MCP tools during integration phase
5. **Testing**: End-to-end testing requires Spec-5 implementation complete

## Performance Targets

- **Agent Processing Time**: <500ms (excluding MCP tool latency)
- **End-to-End Response Time**: <2 seconds (including tool execution and database)
- **Intent Classification Accuracy**: 95%+ for common phrasings
- **Determinism**: 100% (identical inputs → identical outputs)

## Security Considerations

- **User ID Validation**: Agent passes authenticated user_id to all MCP tools
- **No Direct Database Access**: Agent only uses MCP tools (constitutional requirement)
- **Error Message Safety**: No technical details, stack traces, or other users' data exposed
- **Input Validation**: Message length limited to 2000 characters (prevents prompt injection)

## Next Steps

1. ✅ Phase 0 Complete: Research complete (see research.md)
2. ✅ Phase 1 Complete: Design complete (see data-model.md, contracts/)
3. **Ready for Implementation**: Run `/sp.tasks` to generate actionable tasks
4. **Coordinate with Spec-5**: Ensure MCP tool contracts align before integration
5. **Development**: Follow task order (agent core → intent → tools → formatting → testing)

---

**Status**: Design complete, ready for task generation and implementation
**Critical Path**: Spec-5 (MCP tools) required for integration testing
**Constitutional Compliance**: All Phase III principles enforced (stateless, deterministic, protocol-driven)
