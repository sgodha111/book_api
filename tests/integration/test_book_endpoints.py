"""Integration tests for book endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_books_empty(client):
    """Test listing books when database is empty."""
    response = await client.get("/api/v1/books")
    assert response.status_code == 200
    data = response.json()
    assert data["data"] == []


@pytest.mark.asyncio
async def test_create_book_success(client):
    """Test creating a valid book."""
    book_data = {
        "title": "1984",
        "author": "George Orwell",
        "pages": 328,
        "publisher": "Penguin",
        "tags": ["fiction"],
    }
    response = await client.post("/api/v1/books", json=book_data)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "1984"
    assert data["author"] == "George Orwell"
    assert "id" in data


@pytest.mark.asyncio
async def test_create_book_missing_required_field(client):
    """Test creating book without required field."""
    book_data = {
        "title": "1984",
        # Missing author
        "pages": 328,
        "publisher": "Penguin",
    }
    response = await client.post("/api/v1/books", json=book_data)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_book_invalid_pages(client):
    """Test creating book with invalid pages."""
    book_data = {
        "title": "1984",
        "author": "George Orwell",
        "pages": -10,  # Invalid
        "publisher": "Penguin",
    }
    response = await client.post("/api/v1/books", json=book_data)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_list_books_with_pagination(client, sample_book_data):
    """Test pagination parameters."""
    # Create 3 books
    for i in range(3):
        book_data = {
            "title": f"Book {i}",
            "author": f"Author {i}",
            "pages": 100 + i,
            "publisher": "Publisher",
            "tags": ["fiction"],
        }
        await client.post("/api/v1/books", json=book_data)

    # Test page 1, limit 2
    response = await client.get("/api/v1/books?page=1&limit=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) == 2
    assert data["pagination"]["page"] == 1
    assert data["pagination"]["limit"] == 2


@pytest.mark.asyncio
async def test_get_book_not_found(client):
    """Test getting non-existent book."""
    response = await client.get("/api/v1/books/nonexistent")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_book_partial(client):
    """Test partial book update."""
    # Create a book
    book_data = {
        "title": "Original",
        "author": "Author",
        "pages": 200,
        "publisher": "Publisher",
        "tags": ["fiction"],
    }
    create_response = await client.post("/api/v1/books", json=book_data)
    book_id = create_response.json()["id"]

    # Update only title
    update_data = {"title": "Updated Title"}
    response = await client.patch(f"/api/v1/books/{book_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["author"] == "Author"  # Unchanged


@pytest.mark.asyncio
async def test_delete_book_success(client):
    """Test successful book deletion."""
    # Create a book
    book_data = {
        "title": "To Delete",
        "author": "Author",
        "pages": 100,
        "publisher": "Publisher",
        "tags": [],
    }
    create_response = await client.post("/api/v1/books", json=book_data)
    book_id = create_response.json()["id"]

    # Delete it
    response = await client.delete(f"/api/v1/books/{book_id}")
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_delete_book_not_found(client):
    """Test deleting non-existent book."""
    response = await client.delete("/api/v1/books/nonexistent")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_search_books(client):
    """Test searching books."""
    # Create books
    books = [
        {"title": "1984", "author": "Orwell", "pages": 328, "publisher": "Penguin", "tags": []},
        {"title": "Brave New World", "author": "Huxley", "pages": 288, "publisher": "Chatto", "tags": []},
    ]
    for book in books:
        await client.post("/api/v1/books", json=book)

    # Search
    response = await client.get("/api/v1/books/search?query=1984")
    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) >= 1


@pytest.mark.asyncio
async def test_book_count_stats(client):
    """Test book count statistics."""
    # Create 2 books
    for i in range(2):
        book_data = {
            "title": f"Book {i}",
            "author": f"Author {i}",
            "pages": 100,
            "publisher": "Publisher",
            "tags": [],
        }
        await client.post("/api/v1/books", json=book_data)

    response = await client.get("/api/v1/books/stats/count")
    assert response.status_code == 200
    data = response.json()
    assert data["total_count"] == 2
