"""
Database connection and session management.
Uses async SQLAlchemy with connection pooling configured for Neon Serverless.
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

from src.config import settings

# Create async engine with connection pooling
# pool_pre_ping: Verify connections before use (handles Neon serverless wakeup)
# pool_recycle: Recycle connections after 1 hour (Neon recommendation)
engine = create_async_engine(
    settings.database_url,
    echo=False,  # Set True for SQL logging in development
    pool_size=10,  # Minimum connections
    max_overflow=20,  # Additional connections under load
    pool_pre_ping=True,  # Verify connections before use
    pool_recycle=3600,  # Recycle after 1 hour
)

# Async session factory
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncSession:
    """
    Dependency that provides database session to FastAPI endpoints.

    Usage:
        @app.get("/endpoint")
        async def endpoint(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with AsyncSessionLocal() as session:
        yield session


async def create_db_and_tables():
    """Create all database tables. Used for testing."""
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
