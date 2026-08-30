"""Tests for advanced book filtering and search."""

import pytest
from httpx import AsyncClient
from app.main import create_app
from app.schemas.book import BookCreate


@pytest.fixture
async def setup_test_books(client: AsyncClient):
    """Create test books for filtering."""
    books = [
        {
            "title": "1984",
            "author": "George Orwell",
            "pages": 328,
            "publisher": "Penguin",
            "tags": ["fiction", "dystopian"],
        },
        {
            "title": "Brave New World",
            "author": "Aldous Huxley",
            "pages": 311,
            "publisher": "Chatto & Windus",
            "tags": ["fiction", "dystopian", "sci-fi"],
        },
        {
            "title": "The Great Gatsby",
            "author": "F. Scott Fitzgerald",
            "pages": 180,
            "publisher": "Scribner",
            "tags": ["fiction", "romance"],
        },
        {
            "title": "To Kill a Mockingbird",
            "author": "Harper Lee",
            "pages": 281,
            "publisher": "Lippincott",
            "tags": ["fiction", "drama"],
        },
        {
            "title": "Python Programming",
            "author": "Mark Lutz",
            "pages": 1516,
            "publisher": "O'Reilly",
            "tags": ["technical", "programming", "python"],
        },
    ]

    for book in books:
        await client.post("/api/v1/books", json=book)

    return books


class TestAdvancedFilters:
    """Test advanced filtering on GET /books endpoint."""

    async def test_filter_by_author(self, client: AsyncClient, setup_test_books):
        """Test filtering books by author."""
        response = await client.get("/api/v1/books?author=George")
        assert response.status_code == 200
        data = response.json()
        assert data["pagination"]["total"] == 1
        assert data["data"][0]["author"] == "George Orwell"

    async def test_filter_by_publisher(self, client: AsyncClient, setup_test_books):
        """Test filtering books by publisher."""
        response = await client.get("/api/v1/books?publisher=Penguin")
        assert response.status_code == 200
        data = response.json()
        assert data["pagination"]["total"] == 1
        assert data["data"][0]["publisher"] == "Penguin"

    async def test_filter_by_single_tag(self, client: AsyncClient, setup_test_books):
        """Test filtering books by single tag."""
        response = await client.get("/api/v1/books?tags=dystopian")
        assert response.status_code == 200
        data = response.json()
        assert data["pagination"]["total"] == 2
        # Both books should have dystopian tag
        for book in data["data"]:
            assert "dystopian" in book["tags"]

    async def test_filter_by_multiple_tags(self, client: AsyncClient, setup_test_books):
        """Test filtering books by multiple tags (match any)."""
        response = await client.get("/api/v1/books?tags=python,romance")
        assert response.status_code == 200
        data = response.json()
        # Should return books with either python or romance tag
        assert data["pagination"]["total"] >= 2

    async def test_filter_by_min_pages(self, client: AsyncClient, setup_test_books):
        """Test filtering books by minimum pages."""
        response = await client.get("/api/v1/books?min_pages=300")
        assert response.status_code == 200
        data = response.json()
        # Should return books with >= 300 pages
        for book in data["data"]:
            assert book["pages"] >= 300

    async def test_filter_by_max_pages(self, client: AsyncClient, setup_test_books):
        """Test filtering books by maximum pages."""
        response = await client.get("/api/v1/books?max_pages=300")
        assert response.status_code == 200
        data = response.json()
        # Should return books with <= 300 pages
        for book in data["data"]:
            assert book["pages"] <= 300

    async def test_filter_by_page_range(self, client: AsyncClient, setup_test_books):
        """Test filtering books by page range."""
        response = await client.get("/api/v1/books?min_pages=200&max_pages=400")
        assert response.status_code == 200
        data = response.json()
        # Should return books between 200-400 pages
        for book in data["data"]:
            assert 200 <= book["pages"] <= 400

    async def test_sort_by_title_asc(self, client: AsyncClient, setup_test_books):
        """Test sorting books by title ascending."""
        response = await client.get("/api/v1/books?sort_by=title&order=asc&limit=100")
        assert response.status_code == 200
        data = response.json()
        titles = [book["title"] for book in data["data"]]
        assert titles == sorted(titles)

    async def test_sort_by_title_desc(self, client: AsyncClient, setup_test_books):
        """Test sorting books by title descending."""
        response = await client.get("/api/v1/books?sort_by=title&order=desc&limit=100")
        assert response.status_code == 200
        data = response.json()
        titles = [book["title"] for book in data["data"]]
        assert titles == sorted(titles, reverse=True)

    async def test_sort_by_pages_asc(self, client: AsyncClient, setup_test_books):
        """Test sorting books by page count ascending."""
        response = await client.get("/api/v1/books?sort_by=pages&order=asc&limit=100")
        assert response.status_code == 200
        data = response.json()
        pages = [book["pages"] for book in data["data"]]
        assert pages == sorted(pages)

    async def test_sort_by_pages_desc(self, client: AsyncClient, setup_test_books):
        """Test sorting books by page count descending."""
        response = await client.get("/api/v1/books?sort_by=pages&order=desc&limit=100")
        assert response.status_code == 200
        data = response.json()
        pages = [book["pages"] for book in data["data"]]
        assert pages == sorted(pages, reverse=True)

    async def test_sort_by_author(self, client: AsyncClient, setup_test_books):
        """Test sorting books by author."""
        response = await client.get("/api/v1/books?sort_by=author&order=asc&limit=100")
        assert response.status_code == 200
        data = response.json()
        authors = [book["author"] for book in data["data"]]
        assert authors == sorted(authors)

    async def test_combined_filters(self, client: AsyncClient, setup_test_books):
        """Test combining multiple filters."""
        response = await client.get(
            "/api/v1/books?tags=fiction&min_pages=200&max_pages=400&sort_by=pages&order=desc"
        )
        assert response.status_code == 200
        data = response.json()
        # All books should have fiction tag, 200-400 pages
        for book in data["data"]:
            assert "fiction" in book["tags"]
            assert 200 <= book["pages"] <= 400

    async def test_search_and_filter(self, client: AsyncClient, setup_test_books):
        """Test combining search with filters."""
        response = await client.get("/api/v1/books?search=orwell&publisher=Penguin")
        assert response.status_code == 200
        data = response.json()
        assert data["pagination"]["total"] == 1
        assert data["data"][0]["author"] == "George Orwell"

    async def test_invalid_sort_field_defaults(self, client: AsyncClient, setup_test_books):
        """Test that invalid sort field defaults to created_at."""
        response = await client.get("/api/v1/books?sort_by=invalid_field")
        assert response.status_code == 200
        # Should still return results, just with default sort

    async def test_pagination_with_filters(self, client: AsyncClient, setup_test_books):
        """Test pagination works with filters."""
        # Get first page
        response1 = await client.get("/api/v1/books?tags=fiction&limit=2&page=1")
        assert response1.status_code == 200
        data1 = response1.json()
        first_page_ids = [book["id"] for book in data1["data"]]

        # Get second page
        response2 = await client.get("/api/v1/books?tags=fiction&limit=2&page=2")
        assert response2.status_code == 200
        data2 = response2.json()
        second_page_ids = [book["id"] for book in data2["data"]]

        # Pages should have different books
        assert len(set(first_page_ids) & set(second_page_ids)) == 0


class TestFullTextSearch:
    """Test full-text search endpoint."""

    async def test_search_by_title(self, client: AsyncClient, setup_test_books):
        """Test full-text search by book title."""
        response = await client.get("/api/v1/books/search?q=1984")
        assert response.status_code == 200
        data = response.json()
        assert data["pagination"]["total"] >= 1
        found_1984 = any(book["title"] == "1984" for book in data["data"])
        assert found_1984

    async def test_search_by_author(self, client: AsyncClient, setup_test_books):
        """Test full-text search by author."""
        response = await client.get("/api/v1/books/search?q=Orwell")
        assert response.status_code == 200
        data = response.json()
        assert data["pagination"]["total"] >= 1
        found_orwell = any("Orwell" in book["author"] for book in data["data"])
        assert found_orwell

    async def test_search_by_publisher(self, client: AsyncClient, setup_test_books):
        """Test full-text search by publisher."""
        response = await client.get("/api/v1/books/search?q=Penguin")
        assert response.status_code == 200
        data = response.json()
        assert data["pagination"]["total"] >= 1
        found_penguin = any(book["publisher"] == "Penguin" for book in data["data"])
        assert found_penguin

    async def test_search_case_insensitive(self, client: AsyncClient, setup_test_books):
        """Test that search is case-insensitive."""
        response_lower = await client.get("/api/v1/books/search?q=orwell")
        response_upper = await client.get("/api/v1/books/search?q=ORWELL")
        response_mixed = await client.get("/api/v1/books/search?q=OreWeLl")

        assert response_lower.status_code == 200
        assert response_upper.status_code == 200
        assert response_mixed.status_code == 200

        # All should return same number of results
        data_lower = response_lower.json()
        data_upper = response_upper.json()
        data_mixed = response_mixed.json()

        assert data_lower["pagination"]["total"] == data_upper["pagination"]["total"]
        assert data_lower["pagination"]["total"] == data_mixed["pagination"]["total"]

    async def test_search_pagination(self, client: AsyncClient, setup_test_books):
        """Test pagination on search results."""
        response = await client.get("/api/v1/books/search?q=fiction&limit=2&page=1")
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) <= 2


class TestBookStats:
    """Test book statistics endpoint."""

    async def test_get_stats(self, client: AsyncClient, setup_test_books):
        """Test retrieving book statistics."""
        response = await client.get("/api/v1/books/stats")
        assert response.status_code == 200
        data = response.json()

        # Check required fields
        assert "total_books" in data
        assert "avg_pages" in data
        assert "min_pages" in data
        assert "max_pages" in data
        assert "books_by_tag" in data
        assert "most_common_publisher" in data

    async def test_stats_totals(self, client: AsyncClient, setup_test_books):
        """Test that stats totals are correct."""
        response = await client.get("/api/v1/books/stats")
        assert response.status_code == 200
        data = response.json()

        # Should have created 5 books
        assert data["total_books"] == 5

    async def test_stats_page_ranges(self, client: AsyncClient, setup_test_books):
        """Test that page statistics are in correct order."""
        response = await client.get("/api/v1/books/stats")
        assert response.status_code == 200
        data = response.json()

        # Min should be less than or equal to avg, avg should be less than or equal to max
        assert data["min_pages"] <= data["avg_pages"] <= data["max_pages"]

    async def test_stats_tags(self, client: AsyncClient, setup_test_books):
        """Test that tag statistics are present."""
        response = await client.get("/api/v1/books/stats")
        assert response.status_code == 200
        data = response.json()

        # Should have tags
        assert len(data["books_by_tag"]) > 0
        # Fiction should be most common
        assert "fiction" in data["books_by_tag"]

    async def test_stats_publisher(self, client: AsyncClient, setup_test_books):
        """Test most common publisher is set."""
        response = await client.get("/api/v1/books/stats")
        assert response.status_code == 200
        data = response.json()

        # Should have a publisher
        assert data["most_common_publisher"] != "N/A"


class TestRateLimiting:
    """Test rate limiting middleware."""

    async def test_rate_limit_headers(self, client: AsyncClient, setup_test_books):
        """Test that rate limit headers are present in responses."""
        response = await client.get("/api/v1/books")
        assert response.status_code == 200

        # Check rate limit headers
        assert "X-RateLimit-Limit" in response.headers
        assert "X-RateLimit-Remaining" in response.headers
        assert "X-RateLimit-Reset" in response.headers

        # Values should be reasonable
        limit = int(response.headers["X-RateLimit-Limit"])
        assert limit == 100

    async def test_response_time_header(self, client: AsyncClient, setup_test_books):
        """Test that response time header is present."""
        response = await client.get("/api/v1/books")
        assert response.status_code == 200
        assert "X-Process-Time" in response.headers

        # Should be a valid float
        process_time = float(response.headers["X-Process-Time"])
        assert process_time >= 0
