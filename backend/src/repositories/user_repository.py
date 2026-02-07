"""
User repository for database operations.
"""

from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from passlib.context import CryptContext
from typing import Optional

from ..models.user import User


class UserRepository:
    """Repository for user database operations."""

    def __init__(self, db: AsyncSession):
        """
        Initialize repository with database session.

        Args:
            db: Async SQLAlchemy session
        """
        self.db = db
        self.pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

    def hash_password(self, password: str) -> str:
        """
        Hash a password using bcrypt.

        Args:
            password: Plain text password

        Returns:
            Hashed password string
        """
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify a password against its hash.

        Args:
            plain_password: Plain text password to verify
            hashed_password: Hashed password to compare against

        Returns:
            True if password matches the hash, False otherwise
        """
        return self.pwd_context.verify(plain_password, hashed_password)

    async def create_user(self, email: str, password: str) -> User:
        """
        Create a new user with hashed password.

        Args:
            email: User's email address
            password: Plain text password (will be hashed)

        Returns:
            Created User object
        """
        hashed_password = self.hash_password(password)
        user = User(
            email=email,
            password_hash=hashed_password
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Retrieve a user by email address.

        Args:
            email: Email address to search for

        Returns:
            User object if found, None otherwise
        """
        statement = select(User).where(User.email == email)
        result = await self.db.execute(statement)
        user = result.scalar_one_or_none()
        return user

    async def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        """
        Retrieve a user by ID.

        Args:
            user_id: UUID of the user to retrieve

        Returns:
            User object if found, None otherwise
        """
        statement = select(User).where(User.id == user_id)
        result = await self.db.execute(statement)
        user = result.scalar_one_or_none()
        return user

    async def update_last_login(self, user: User) -> User:
        """
        Update the last_login timestamp for a user.

        Args:
            user: User object to update

        Returns:
            Updated User object
        """
        from datetime import datetime
        user.last_login = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(user)
        return user