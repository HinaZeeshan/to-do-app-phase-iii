"""
Agent configuration settings and system prompts.

This module provides configuration for the AI chat agent including:
- OpenAI API settings
- Intent keyword mappings
- System prompts for deterministic behavior
- Error message templates
"""

from typing import Dict, List
from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class AgentSettings(BaseSettings):
    """Agent configuration settings loaded from environment variables."""

    openai_api_key: str
    openai_model: str = "gpt-4"
    openai_temperature: float = 0.0  # Maximum determinism
    agent_max_conversation_messages: int = 50
    agent_max_message_length: int = 2000
    agent_processing_timeout_ms: int = 500

    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=False
    )


# System prompt for the agent (deterministic behavior)
AGENT_SYSTEM_PROMPT = """You are a task management assistant. Your role is to help users manage their todo tasks through natural language commands.

CRITICAL RULES:
1. You MUST use the provided tools (add_task, list_tasks, complete_task, delete_task, update_task) for ALL task operations
2. NEVER invent or fabricate task data - only use data returned by tools
3. Be concise and friendly in your responses
4. If you're unsure about a task reference, ask for clarification
5. Always confirm actions taken

Your responses should be conversational but brief. Focus on helping users accomplish their task management goals."""

# Intent keyword mappings for deterministic classification
# Priority is determined by insertion order (checked first to last)
INTENT_KEYWORDS: Dict[str, List[str]] = {
    "DELETE_TASK": ["delete", "remove", "cancel", "discard", "bin"],
    "COMPLETE_TASK": ["done", "complete", "finished", "mark", "finish", "check off"],
    "UPDATE_TASK": ["change", "update", "rename", "modify", "edit"],
    "LIST_TASKS": ["show", "list", "what", "pending", "completed", "what are", "display", "see", "tasks"],
    "CREATE_TASK": [
        "add", "create", "remind", "remember", "new task", "make a task", 
        "buy", "need to", "must", "order", "get"
    ],
}

# Error message templates
ERROR_MESSAGES: Dict[str, str] = {
    "TaskNotFoundError": "I couldn't find a task matching '{reference}'",
    "UnauthorizedError": "You need to be authenticated to perform this action",
    "ValidationError": "That input isn't valid: {details}",
    "DatabaseError": "I'm having trouble accessing your tasks right now. Please try again in a moment.",
    "NetworkError": "I'm having trouble connecting right now. Please try again in a moment.",
    "GenericError": "Something went wrong. Please try again.",
}

# Success confirmation templates
CONFIRMATION_TEMPLATES: Dict[str, str] = {
    "task_created": "I've added '{title}' to your tasks",
    "task_completed": "Great! I've marked '{title}' as done",
    "task_deleted": "I've deleted '{title}'",
    "task_updated": "I've updated the task to '{title}'",
    "tasks_listed": "You have {count} task(s)",
    "no_tasks": "You don't have any tasks yet",
}
