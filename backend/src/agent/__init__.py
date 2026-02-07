"""
AI Chat Agent Module for Todo Task Management.

This module provides natural language processing capabilities for task management
through an AI-powered chat agent that interprets user intent and executes
task operations via MCP (Model Context Protocol) tools.

The agent is stateless, deterministic, and follows Phase III constitutional
requirements: no direct database access, protocol-driven tool execution,
and conversation history persistence handled externally.
"""

from .chat_agent import run_agent
from .schemas import AgentRequest, AgentResponse, Intent

__all__ = ["run_agent", "AgentRequest", "AgentResponse", "Intent"]
