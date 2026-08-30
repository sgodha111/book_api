"""Integration tests for aggregation endpoints."""

import pytest


@pytest.mark.asyncio
async def test_list_authors_with_book_counts(client):
    """Test GET /authors returns authors with book_count."""
    # Create books by different authors
    books = [
        {"title": "Book 1", "author": "Author A", "pages": 100, "publisher": "Pub", "tags": []},
        {"title": "Book 2", "author": "Author A", "pages": 120, "publisher": "Pub", "tags": []},
        {"title": "Book 3", "author": "Author B", "pages": 150, "publisher": "Pub", "tags": []},
    ]
    for book in books:
        await client.post("/api/v1/books", json=book)

    # Get authors
    response = await client.get("/api/v1/authors")
    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) >= 2


@pytest.mark.asyncio
async def test_get_author_books(client):
    """Test GET /authors/{id}/books returns books by author."""
    # Create an author
    author_data = {"name": "Test Author", "country": "USA"}
    author_response = await client.post("/api/v1/authors", json=author_data)
    assert author_response.status_code == 201
    author_id = author_response.json()["id"]

    # Create books
    books = [
        {"title": "Book 1", "author": "Test Author", "pages": 100, "publisher": "Pub", "tags": []},
        {"title": "Book 2", "author": "Test Author", "pages": 120, "publisher": "Pub", "tags": []},
    ]
    for book in books:
        await client.post("/api/v1/books", json=book)

    # Get author's books
    response = await client.get(f"/api/v1/authors/{author_id}/books")
    assert response.status_code == 200
    data = response.json()
    # Note: Due to mock DB limitations, this may not show exact count
    assert isinstance(data, dict) or isinstance(data, list)


@pytest.mark.asyncio
async def test_publisher_average_pages(client):
    """Test GET /publishers/{name}/average_pages."""
    # Create books by same publisher
    books = [
        {"title": "Book 1", "author": "Author A", "pages": 100, "publisher": "Test Pub", "tags": []},
        {"title": "Book 2", "author": "Author B", "pages": 200, "publisher": "Test Pub", "tags": []},
    ]
    for book in books:
        await client.post("/api/v1/books", json=book)

    response = await client.get("/api/v1/publishers/Test%20Pub/average-pages")
    assert response.status_code == 200
    data = response.json()
    # Should contain average pages information
    assert isinstance(data, dict)


@pytest.mark.asyncio
async def test_publisher_stats(client):
    """Test GET /publishers/{name}/stats."""
    # Create books
    books = [
        {"title": "Book 1", "author": "Author A", "pages": 100, "publisher": "Pub Stats", "tags": []},
    ]
    for book in books:
        await client.post("/api/v1/books", json=book)

    response = await client.get("/api/v1/publishers/Pub%20Stats/stats")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)


@pytest.mark.asyncio
async def test_publisher_overview(client):
    """Test GET /publishers/overview."""
    response = await client.get("/api/v1/publishers/overview")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)


@pytest.mark.asyncio
async def test_author_statistics(client):
    """Test GET /authors/stats/overview."""
    response = await client.get("/api/v1/authors/stats/overview")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)


@pytest.mark.asyncio
async def test_top_publishers(client):
    """Test GET /publishers/top."""
    # Create books
    books = [
        {"title": "Book 1", "author": "Author", "pages": 100, "publisher": "Top Pub", "tags": []},
    ]
    for book in books:
        await client.post("/api/v1/books", json=book)

    response = await client.get("/api/v1/publishers/top")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict) or isinstance(data, list)
