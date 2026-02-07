"""
Authentication event repository for database operations.
"""

from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional

from ..models.auth_event import AuthenticationEvent, EventType


class AuthEventRepository:
    """Repository for authentication event database operations."""

    def __init__(self, db: AsyncSession):
        """
        Initialize repository with database session.

        Args:
            db: Async SQLAlchemy session
        """
        self.db = db

    async def log_auth_event(
        self,
        user_id: Optional[UUID],
        event_type: EventType,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        success: bool = True,
        failure_reason: Optional[str] = None
    ) -> AuthenticationEvent:
        """
        Log an authentication event to the database.

        Args:
            user_id: ID of the user associated with the event (None if not available)
            event_type: Type of authentication event (signup, login, logout, login_failed)
            ip_address: Client IP address
            user_agent: Client user agent string
            success: Whether the event was successful
            failure_reason: Reason for failure (if applicable)

        Returns:
            Created AuthenticationEvent object
        """
        event = AuthenticationEvent(
            user_id=user_id,
            event_type=event_type,
            ip_address=ip_address,
            user_agent=user_agent,
            success=success,
            failure_reason=failure_reason
        )
        self.db.add(event)
        await self.db.commit()
        await self.db.refresh(event)
        return event