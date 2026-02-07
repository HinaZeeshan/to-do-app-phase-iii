# Research: AI Chat Agent & Conversation Logic

**Date**: 2026-02-07
**Feature**: 004-ai-chat-agent
**Phase**: Phase 0 - Research & Technology Selection

## R1: OpenAI Agents SDK Integration

### Research Question
How to integrate OpenAI Agents SDK with FastAPI backend and MCP tools?

### Findings

**OpenAI Agents SDK Overview**:
- The OpenAI Agents SDK provides a Python library for building AI agents with function calling capabilities
- Supports stateless agent execution via the `openai` library's chat completions API
- Compatible with Python 3.11+ and async/await patterns

**Integration Pattern**:
```python
from openai import AsyncOpenAI

client = AsyncOpenAI(api_key=settings.openai_api_key)

async def run_agent(user_id: UUID, message: str, conversation_history: List[dict]):
    # Build messages array from conversation history
    messages = [
        {"role": "system", "content": AGENT_SYSTEM_PROMPT},
        *conversation_history,  # Previous user/assistant messages
        {"role": "user", "content": message}
    ]

    # Define MCP tools as function schemas
    tools = [add_task_schema, list_tasks_schema, ...]

    # Call agent with temperature=0 for determinism
    response = await client.chat.completions.create(
        model="gpt-4",
        messages=messages,
        tools=tools,
        temperature=0,  # Maximum determinism
        tool_choice="auto"
    )

    # Extract tool calls and execute MCP tools
    # Return AgentResponse
```

**Stateless Execution**:
- No long-lived agent instances needed
- Each request creates a fresh API call with full conversation history
- Agent state is conversation history (provided by Spec-5)

**Function Calling / Tool Use**:
- Define tools as JSON schemas following OpenAI function calling format
- Agent decides which tool to call based on user intent
- Extract tool call parameters from response
- Execute actual MCP tool with extracted parameters
- Return tool result to user

###Decision

**Chosen Approach**: Use OpenAI Python SDK (`openai` library) with chat completions API and function calling.

**Rationale**:
1. Supports stateless execution (constitutional requirement)
2. Built-in function calling mechanism maps directly to MCP tool invocation
3. Compatible with Python 3.11 and async FastAPI patterns
4. Temperature=0 provides maximum determinism
5. Well-documented and actively maintained

**Alternatives Considered**:
- **Custom LLM fine-tuning**: Rejected due to complexity, non-determinism, and constitutional requirement for OpenAI Agents SDK
- **LangChain agents**: Rejected because constitution explicitly requires OpenAI Agents SDK
- **Prompt-only approach (no function calling)**: Rejected because parsing responses is non-deterministic and error-prone

### Implementation Notes
- Install `openai` Python library (latest version compatible with function calling)
- Configure API key in `.env` as `OPENAI_API_KEY`
- Set `temperature=0` for all agent calls to maximize determinism
- System prompt must explicitly prohibit hallucination and require tool use

---

## R2: MCP Tool Protocol

### Research Question
What is the MCP (Model Context Protocol) tool interface for this project?

### Findings

**MCP Context**:
- MCP (Model Context Protocol) is mentioned in Phase III constitution and Spec-4
- Spec-5 (MCP Server, Tools & Chat Infrastructure) defines the actual MCP tool implementations
- MCP tools are the exclusive interface for task operations (no direct database access)

**Expected Tool Interface** (to be confirmed with Spec-5):
```python
# Tool signatures for task operations
async def add_task(user_id: UUID, title: str) -> Task
async def list_tasks(user_id: UUID, filter: Optional[str] = None) -> List[Task]
async def complete_task(user_id: UUID, task_id: UUID) -> Task
async def delete_task(user_id: UUID, task_id: UUID) -> None
async def update_task(user_id: UUID, task_id: UUID, new_title: str) -> Task
```

**Tool Invocation Pattern**:
- Agent receives user message and conversation history
- Agent uses OpenAI function calling to select tool and extract parameters
- Agent invokes MCP tool with user_id and extracted parameters
- MCP tool handles authorization (verifies user_id matches authenticated user)
- MCP tool executes task operation via existing TaskService
- Tool returns success response or raises error
- Agent formats tool response for user

**Error Handling**:
- Tools return structured errors (e.g., `TaskNotFoundError`, `UnauthorizedError`)
- Agent catches errors and translates to user-friendly messages
- No technical details exposed to users

### Decision

**Chosen Approach**: Define expected MCP tool contracts in `contracts/mcp_tools.yaml` and implement mock tools for agent development.

**Rationale**:
1. Agent development can proceed independently of Spec-5 implementation
2. Mock tools allow testing agent logic (intent recognition, parameter extraction, response formatting)
3. Contracts document expected interface for Spec-5 coordination
4. Real MCP tools can be swapped in during integration phase

**Alternatives Considered**:
- **Wait for Spec-5 completion**: Rejected due to blocking agent development
- **Agent directly calls TaskService**: Rejected because violates constitutional separation of concerns (agent must use MCP tools only)
- **REST API calls**: Rejected because MCP tools are the defined protocol, not REST APIs

### Implementation Notes
- Create `contracts/mcp_tools.yaml` with tool schemas
- Implement mock MCP tools in `backend/src/agent/mocks/` for testing
- Mock tools simulate success and error responses
- Integration testing requires real MCP tools from Spec-5

---

## R3: Intent Classification Strategy

### Research Question
Should intent recognition use prompt engineering, fine-tuned models, or keyword matching?

### Findings

**Approach 1: Pure Keyword Matching**
- Pros: Deterministic, fast, no API costs
- Cons: Limited flexibility, may miss variations

**Approach 2: Pure LLM Intent Classification**
- Pros: Flexible, handles variations
- Cons: Non-deterministic (violates constitution), adds latency

**Approach 3: Hybrid (Keyword + LLM)**
- Pros: Combines determinism with flexibility
- Cons: Moderate complexity

**Constitutional Requirement**: Agent behavior must be deterministic (Principle VI, VII)

**Hybrid Approach Design**:
```python
def classify_intent(message: str) -> Intent:
    # Step 1: Keyword matching (deterministic, fast)
    keywords = {
        Intent.CREATE_TASK: ["add", "create", "remind", "remember", "new task"],
        Intent.LIST_TASKS: ["show", "list", "what", "pending", "completed"],
        Intent.COMPLETE_TASK: ["done", "complete", "finished", "mark"],
        Intent.DELETE_TASK: ["delete", "remove", "cancel"],
        Intent.UPDATE_TASK: ["change", "update", "rename", "modify"],
    }

    message_lower = message.lower()
    for intent, keywords_list in keywords.items():
        if any(kw in message_lower for kw in keywords_list):
            return intent

    # Step 2: LLM classification for edge cases (temperature=0)
    # Only if keyword matching fails
    return classify_with_llm(message)
```

### Decision

**Chosen Approach**: Hybrid keyword matching + LLM fallback with temperature=0.

**Rationale**:
1. Primary keyword matching provides determinism for common cases
2. LLM fallback (temperature=0) handles edge cases while maximizing determinism
3. Keyword matching is fast and free
4. Meets constitutional requirement for deterministic behavior
5. Balances flexibility with predictability

**Alternatives Considered**:
- **Pure keywords**: Rejected because too rigid, misses variations
- **Pure LLM**: Rejected because non-deterministic (violates constitution)
- **Fine-tuned model**: Rejected due to complexity and maintenance burden

### Implementation Notes
- Implement keyword matching first (deterministic path)
- Use LLM fallback only for unrecognized inputs
- Set temperature=0 for LLM calls
- Log all intent classifications for monitoring determinism
- If non-determinism observed, expand keyword rules

---

## R4: Conversation History Management

### Research Question
How is conversation history formatted and passed to the agent?

### Findings

**OpenAI Agents SDK Format**:
```python
conversation_history = [
    {"role": "user", "content": "remind me to buy milk"},
    {"role": "assistant", "content": "I've added 'buy milk' to your tasks"},
    {"role": "user", "content": "what are my tasks?"},
    {"role": "assistant", "content": "You have 1 task: buy milk"},
]
```

**Message Structure**:
- `role`: "user" | "assistant" | "system"
- `content`: Message text
- Optional: `timestamp`, `metadata`

**Conversation Length Handling**:
- Spec requires handling up to 50 messages
- OpenAI API has token limits (~8k-32k depending on model)
- Average message ~100 tokens → 50 messages ~5k tokens (safe)
- If exceeding limits, truncate oldest messages (keep most recent context)

**Integration with Spec-5**:
- Spec-5 persists conversation history in database
- Spec-5 retrieves conversation history on each request
- Spec-5 passes conversation history to agent
- Agent appends new user message and assistant response
- Spec-5 persists updated conversation after agent response

### Decision

**Chosen Approach**: Accept conversation history as `List[ConversationMessage]` in OpenAI format; implement truncation if > 50 messages or > 5k tokens.

**Rationale**:
1. OpenAI SDK native format (no conversion needed)
2. Truncation strategy handles edge cases gracefully
3. 50-message limit is reasonable for task management conversations
4. Spec-5 handles persistence (agent is stateless)

**Alternatives Considered**:
- **Custom format**: Rejected because requires conversion to/from OpenAI format
- **No truncation**: Rejected because may hit token limits
- **Summarization**: Rejected due to complexity and potential information loss

### Implementation Notes
- Define `ConversationMessage` schema matching OpenAI format
- Implement truncation logic (keep most recent 50 messages or ~5k tokens)
- Log when truncation occurs for monitoring
- Coordinate with Spec-5 on conversation persistence format

---

## R5: Error Handling Patterns

### Research Question
How should the agent translate MCP tool errors into user-friendly messages?

### Findings

**Common Error Types**:
1. **TaskNotFoundError**: User references non-existent task
2. **UnauthorizedError**: User attempts to access another user's task
3. **ValidationError**: Invalid input (empty title, invalid UUID)
4. **DatabaseError**: Persistence layer failure
5. **NetworkError**: External service unavailable

**Error Translation Pattern**:
```python
ERROR_MESSAGES = {
    "TaskNotFoundError": "I couldn't find a task matching '{reference}'",
    "UnauthorizedError": "You don't have permission to access that task",
    "ValidationError": "That input isn't valid: {details}",
    "DatabaseError": "I'm having trouble accessing your tasks right now. Please try again in a moment.",
    "NetworkError": "I'm having trouble connecting right now. Please try again in a moment.",
}

def format_error(error: Exception) -> str:
    error_type = type(error).__name__
    template = ERROR_MESSAGES.get(error_type, "Something went wrong. Please try again.")
    return template.format(reference=..., details=...)
```

**Security Considerations**:
- Never expose database connection strings, file paths, or stack traces
- Don't reveal existence of other users' data
- Don't provide technical details that aid attackers

### Decision

**Chosen Approach**: Implement error mapping dictionary with user-friendly templates; log technical details for debugging.

**Rationale**:
1. Consistent user experience across error types
2. No technical details leaked to users
3. Actionable guidance where possible
4. Logging preserves debugging information

**Alternatives Considered**:
- **Generic errors**: Rejected because not helpful to users
- **Detailed technical errors**: Rejected due to security concerns
- **LLM-generated error messages**: Rejected due to non-determinism and potential hallucination

### Implementation Notes
- Define error mapping dictionary in `response_formatter.py`
- Log full error details (stack trace, context) for debugging
- Test all error scenarios in integration tests
- Coordinate with Spec-5 on error response format from MCP tools

---

## Summary

### Key Decisions

1. **OpenAI Agents SDK**: Use `openai` Python library with function calling (temperature=0)
2. **MCP Tools**: Define contracts in `contracts/mcp_tools.yaml`, use mocks for development
3. **Intent Classification**: Hybrid keyword matching + LLM fallback (deterministic priority)
4. **Conversation History**: OpenAI format, truncate at 50 messages or 5k tokens
5. **Error Handling**: User-friendly error mapping with technical logging

### Dependencies
- `openai` Python library (add to pyproject.toml)
- Spec-5 for MCP tool implementations and conversation persistence
- OpenAI API key configured in `.env`

### Risks Mitigated
- Non-determinism: Temperature=0, keyword-first classification
- Spec-5 blocking: Mock MCP tools for independent development
- Hallucination: Explicit system prompt, strict response formatting
- Security: User-friendly error messages, no technical details exposed

### Next Phase
Proceed to Phase 1: Design & Architecture (data-model.md, contracts/, quickstart.md)
