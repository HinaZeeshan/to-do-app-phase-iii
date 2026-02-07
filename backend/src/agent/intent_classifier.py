"""
Intent classification and parameter extraction for natural language task management.

This module implements deterministic intent recognition using keyword matching
as the primary strategy, with LLM fallback for edge cases (temperature=0).
"""

import re
from typing import Dict, List, Optional
from uuid import UUID

from .config import INTENT_KEYWORDS
from .schemas import Intent, IntentClassificationResult

# Common greetings to avoid accidental task creation
GREETINGS = {
    "hi", "hello", "hey", "hello there", "good morning", "good afternoon", 
    "good evening", "howdy", "yo", "greetings", "hi there"
}


def classify_intent(
    message: str, conversation_history: Optional[List[Dict[str, str]]] = None
) -> IntentClassificationResult:
    """
    Classify user intent from natural language message.
    """
    # Ensure message is string (defensive)
    message = str(message)
    message_lower = message.lower().strip()

    # Keyword-based intent classification (deterministic, primary strategy)
    for intent_name, keywords in INTENT_KEYWORDS.items():
        if any(keyword in message_lower for keyword in keywords):
            intent = Intent[intent_name]

            # Extract parameters based on intent
            extracted_params = extract_parameters(intent, message, conversation_history)

            return IntentClassificationResult(
                intent=intent,
                confidence=1.0,  # Keyword match is 100% confident
                extracted_params=extracted_params,
                clarification_question=None,
            )

    # Step 2: Fallback for dynamic task creation
    # If it's a greeting, don't create a task - let it fall through to UNKNOWN
    if message_lower in GREETINGS or any(g in message_lower for g in GREETINGS if len(message_lower) < len(g) + 2):
        return IntentClassificationResult(
            intent=Intent.UNKNOWN,
            confidence=0.0,
            extracted_params={},
            clarification_question=None,
        )

    # If message is long enough and not a greeting, assume it's a new task (Literal Input)
    if len(message_lower) > 2:
        return IntentClassificationResult(
            intent=Intent.CREATE_TASK,
            confidence=0.5,  # Moderate confidence for fallback
            extracted_params={"task_title": message.strip()},
            clarification_question=None,
        )

    # No keyword match found - return UNKNOWN intent
    return IntentClassificationResult(
        intent=Intent.UNKNOWN,
        confidence=0.0,
        extracted_params={},
        clarification_question=None,
    )


def extract_parameters(
    intent: Intent, message: str, conversation_history: Optional[List[Dict[str, str]]] = None
) -> Dict[str, any]:
    """
    Extract parameters from user message based on intent.

    Args:
        intent: Classified intent
        message: User's message
        conversation_history: Previous messages for context

    Returns:
        Dict of extracted parameters (task_title, task_id, filter, etc.)
    """
    params = {}

    if intent == Intent.CREATE_TASK:
        # Extract task title from phrases like:
        # "remind me to buy milk" -> "buy milk"
        # "add a task to call dentist" -> "call dentist"
        # "remember to finish report" -> "finish report"
        params["task_title"] = extract_task_title_for_creation(message)

    elif intent == Intent.LIST_TASKS:
        # Extract optional filter (pending, completed, all)
        params["filter"] = extract_filter(message)

    elif intent in (Intent.COMPLETE_TASK, Intent.DELETE_TASK, Intent.UPDATE_TASK):
        # Extract task reference (partial title or full title)
        params["task_reference"] = extract_task_reference(message)

        # For UPDATE_TASK, also extract new title
        if intent == Intent.UPDATE_TASK:
            params["new_title"] = extract_new_title(message)

    return params


def extract_task_title_for_creation(message: str) -> str:
    """
    Extract task title from creation messages.

    Examples:
        "remind me to buy milk" -> "buy milk"
        "add a task to call dentist" -> "call dentist"
        "create task: finish report" -> "finish report"
    """
    message_lower = message.lower().strip()

    # Pattern 1: "remind me to [title]"
    match = re.search(r"remind me to (.+)", message_lower, re.IGNORECASE)
    if match:
        return match.group(1).strip()

    # Pattern 2: "add (a task)? to [title]"
    match = re.search(r"add(?: a task)? to (.+)", message_lower, re.IGNORECASE)
    if match:
        return match.group(1).strip()

    # Pattern 3: "create (task)? [title]"
    match = re.search(r"create(?: task)?:? (.+)", message_lower, re.IGNORECASE)
    if match:
        return match.group(1).strip()

    # Pattern 4: "remember to [title]"
    match = re.search(r"remember to (.+)", message_lower, re.IGNORECASE)
    if match:
        return match.group(1).strip()

    # Pattern 5: "new task: [title]"
    match = re.search(r"new task:? (.+)", message_lower, re.IGNORECASE)
    if match:
        return match.group(1).strip()

    # Fallback: Use entire message as title (accept literal input)
    return message.strip()


def extract_filter(message: str) -> str:
    """
    Extract task filter from list messages.

    Examples:
        "show me my pending tasks" -> "pending"
        "list completed tasks" -> "completed"
        "what are my tasks" -> "all"
    """
    message_lower = message.lower().strip()

    if "pending" in message_lower or "incomplete" in message_lower or "todo" in message_lower:
        return "pending"
    elif "completed" in message_lower or "done" in message_lower or "finished" in message_lower:
        return "completed"
    else:
        return "all"


def extract_task_reference(message: str) -> str:
    """
    Extract task reference (partial title) from completion/deletion/update messages.

    Examples:
        "mark 'buy milk' as done" -> "buy milk"
        "delete the dentist task" -> "dentist"
        "I finished buying milk" -> "buying milk"
    """
    message_lower = message.lower().strip()

    # Pattern 1: Quoted text (e.g., "mark 'buy milk' as done")
    match = re.search(r"['\"]([^'\"]+)['\"]", message)
    if match:
        return match.group(1).strip()

    # Pattern 2: "the [reference] task"
    match = re.search(r"the (.+?) task", message_lower, re.IGNORECASE)
    if match:
        return match.group(1).strip()

    # Pattern 3: "finished/done with [reference]"
    match = re.search(r"(?:finished|done with) (.+)", message_lower, re.IGNORECASE)
    if match:
        return match.group(1).strip()

    # Pattern 4: "mark [reference] (as)? (done/done/complete)"
    match = re.search(r"mark (.+?)(?: as)? (?:done|complete|finished)", message_lower, re.IGNORECASE)
    if match:
        return match.group(1).strip()

    # Pattern 5: "delete/remove [reference]"
    match = re.search(r"(?:delete|remove) (.+)", message_lower, re.IGNORECASE)
    if match:
        # Check if the extracted reference itself contains intent keywords (e.g. "delete the milk task")
        # and clean them up if it's literally repeating the command
        ref = match.group(1).strip()
        ref = re.sub(r"^the\s+", "", ref)
        ref = re.sub(r"\s+task$", "", ref)
        return ref

    # Pattern 6: If message is JUST an intent keyword like "done" or "finish"
    # We return empty string which will trigger clarification, but we can look at history later
    
    # Fallback: If it's a multi-word message containing a keyword but not matching patterns,
    # try to guess the reference by stripping the keyword
    from .config import INTENT_KEYWORDS
    for keywords in INTENT_KEYWORDS.values():
        for kw in keywords:
            if kw in message_lower and len(message_lower) > len(kw) + 2:
                # Basic attempt to strip the keyword and return the rest
                # e.g. "complete buy milk" -> "buy milk"
                possible_ref = message_lower.replace(kw, "").strip()
                if possible_ref:
                    return possible_ref

    return ""


def extract_new_title(message: str) -> str:
    """
    Extract new title from update messages.

    Examples:
        "change 'buy milk' to 'buy almond milk'" -> "buy almond milk"
        "rename dentist task to call dentist at 3pm" -> "call dentist at 3pm"
    """
    message_lower = message.lower().strip()

    # Pattern 1: "change X to Y" or "rename X to Y"
    match = re.search(r"(?:change|rename).+to ['\"]?([^'\"]+)['\"]?", message_lower, re.IGNORECASE)
    if match:
        return match.group(1).strip()

    # Pattern 2: "update X to Y"
    match = re.search(r"update.+to (.+)", message_lower, re.IGNORECASE)
    if match:
        return match.group(1).strip()

    # Fallback: Return empty string
    return ""
