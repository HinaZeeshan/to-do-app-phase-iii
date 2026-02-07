"""Shared fixtures for backend tests."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

from src.main import app
from src.database import get_db
from src.config import Settings
from src.auth.dependencies import verify_jwt


@pytest.fixture
def client():
    """Test client for the FastAPI app."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
async def mock_db_session():
    """Mock database session for testing."""
    # Create an in-memory SQLite database for testing
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        yield session


@pytest.fixture
def jwt_token():
    """Mock JWT token for testing."""
    # In real tests, this would be a properly encoded JWT
    # For now, returning a placeholder - would be replaced with actual JWT creation
    return "mock_jwt_token"