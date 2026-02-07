"""
Repository for handling RefreshToken database operations.
"""

from uuid import UUID
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete

from ..models.refresh_token import RefreshToken


class RefreshTokenRepository:
    """Repository for authentication refresh tokens."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_token(self, user_id: UUID, token_hash: str, expires_at: datetime) -> RefreshToken:
        """Create a new refresh token."""
        token = RefreshToken(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at
        )
        self.db.add(token)
        await self.db.commit()
        await self.db.refresh(token)
        return token

    async def get_by_token_hash(self, token_hash: str) -> RefreshToken | None:
        """Retrieve a token by its hash."""
        query = select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def delete_token(self, token_hash: str) -> None:
        """Delete a specific token."""
        query = delete(RefreshToken).where(RefreshToken.token_hash == token_hash)
        await self.db.execute(query)
        await self.db.commit()

    async def delete_all_for_user(self, user_id: UUID) -> None:
        """Delete all tokens for a user (e.g. on password reset or logout all)."""
        query = delete(RefreshToken).where(RefreshToken.user_id == user_id)
        await self.db.execute(query)
        await self.db.commit()
