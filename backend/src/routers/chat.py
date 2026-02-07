"""
Chat API router.
Exposes the AI agent functionality to the frontend.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import List

from ..database import get_db
from ..auth.dependencies import get_current_user_id
from ..agent.chat_agent import run_agent
from ..agent.schemas import AgentRequest, AgentResponse

router = APIRouter(prefix="/api", tags=["chat"])

@router.post("/chat", response_model=AgentResponse)
async def chat_with_agent(
    request: AgentRequest,
    db: AsyncSession = Depends(get_db),
    authenticated_user_id: str = Depends(get_current_user_id)
):
    """
    Send a message to the AI chat agent.
    
    Args:
        request: AgentRequest containing message and conversation history
        db: Database session
        authenticated_user_id: Authenticated user ID from JWT
        
    Returns:
        AgentResponse with formatted answer and tool results
    """
    # Ensure user_id in request matches authenticated user
    if str(request.user_id) != authenticated_user_id:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User ID mismatch"
        )
    
    # Run the agent
    response = await run_agent(
        user_id=request.user_id,
        message=request.message,
        conversation_history=[msg.model_dump() for msg in request.conversation_history],
        db=db
    )
    return response
