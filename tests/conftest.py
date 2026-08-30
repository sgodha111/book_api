"""Pytest configuration and fixtures."""

import asyncio
from datetime import datetime
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from mongomock_motor import AsyncMongoMockClient

from app.main import app, create_app
from app.models.database import MongoDB
from app.schemas.book import BookCreate
from app.schemas.author import AuthorCreate


@pytest.fixture
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def mock_db() -> AsyncGenerator:
    """Create mock MongoDB database for testing."""
    client = AsyncMongoMockClient()
    db = client["test_db"]
    yield db
    # Cleanup
    client.close()


@pytest.fixture
def client():
    """Create test client with FastAPI app."""
    return TestClient(app)


@pytest.fixture
def sample_book_data() -> BookCreate:
    """Sample book data for testing."""
    return BookCreate(
        title="Test Book",
        author="Test Author",
        pages=300,
        publisher="Test Publisher",
        tags=["test", "fiction"]
    )


@pytest.fixture
def sample_book_data_2() -> BookCreate:
    """Second sample book data for testing."""
    return BookCreate(
        title="Another Book",
        author="Another Author",
        pages=250,
        publisher="Another Publisher",
        tags=["test", "mystery"]
    )


@pytest.fixture
def sample_author_data() -> AuthorCreate:
    """Sample author data for testing."""
    from datetime import date
    return AuthorCreate(
        id="test_author",
        name="Test Author",
        birth_date=date(1990, 1, 1)
    )


@pytest.fixture
def sample_author_data_2() -> AuthorCreate:
    """Second sample author data for testing."""
    from datetime import date
    return AuthorCreate(
        id="another_author",
        name="Another Author",
        birth_date=date(1985, 6, 15)
    )


@pytest.fixture
async def populated_db(mock_db):
    """Database pre-populated with test data."""
    books_collection = mock_db["books"]
    now = datetime.utcnow()

    # Insert sample books
    await books_collection.insert_many([
        {
            "title": "1984",
            "author": "George Orwell",
            "pages": 328,
            "publisher": "Penguin",
            "tags": ["fiction", "dystopian"],
            "created_at": now,
            "updated_at": now
        },
        {
            "title": "Brave New World",
            "author": "Aldous Huxley",
            "pages": 311,
            "publisher": "Penguin",
            "tags": ["fiction", "dystopian"],
            "created_at": now,
            "updated_at": now
        },
        {
            "title": "The Great Gatsby",
            "author": "F. Scott Fitzgerald",
            "pages": 180,
            "publisher": "Scribner",
            "tags": ["fiction", "classic"],
            "created_at": now,
            "updated_at": now
        }
    ])

    return mock_db
