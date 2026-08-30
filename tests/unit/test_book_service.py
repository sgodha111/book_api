"""Unit tests for BookService."""

import pytest
from datetime import datetime

from app.models.exceptions import BookNotFound, DuplicateBook
from app.schemas.book import BookCreate, BookUpdate
from app.services.book_service import BookService
from app.utils.pagination import PaginationParams


class TestBookServiceCreate:
    """Test BookService.create_book method."""

    @pytest.mark.asyncio
    async def test_create_book_success(self, mock_db, sample_book_data):
        """Test successful book creation."""
        service = BookService(mock_db)

        book = await service.create_book(sample_book_data)

        assert book.id is not None
        assert book.title == sample_book_data.title
        assert book.author == sample_book_data.author
        assert book.pages == sample_book_data.pages
        assert book.publisher == sample_book_data.publisher
        assert book.tags == sample_book_data.tags
        assert book.created_at is not None
        assert book.updated_at is not None

    @pytest.mark.asyncio
    async def test_create_book_duplicate(self, mock_db, sample_book_data):
        """Test that duplicate book creation raises error."""
        service = BookService(mock_db)

        # Create first book
        await service.create_book(sample_book_data)

        # Try to create duplicate
        with pytest.raises(DuplicateBook):
            await service.create_book(sample_book_data)

    @pytest.mark.asyncio
    async def test_create_book_validation_error(self, mock_db):
        """Test that validation errors are caught."""
        service = BookService(mock_db)

        invalid_data = BookCreate(
            title="",  # Empty title should fail
            author="Test",
            pages=100,
            publisher="Pub"
        )

        with pytest.raises(Exception):  # Pydantic validation error
            await service.create_book(invalid_data)


class TestBookServiceRead:
    """Test BookService.get_book method."""

    @pytest.mark.asyncio
    async def test_get_book_success(self, mock_db, sample_book_data):
        """Test successful book retrieval."""
        service = BookService(mock_db)

        # Create book
        created = await service.create_book(sample_book_data)

        # Retrieve it
        retrieved = await service.get_book(created.id)

        assert retrieved.id == created.id
        assert retrieved.title == created.title
        assert retrieved.author == created.author

    @pytest.mark.asyncio
    async def test_get_book_not_found(self, mock_db):
        """Test that getting non-existent book raises error."""
        service = BookService(mock_db)

        with pytest.raises(BookNotFound):
            await service.get_book("invalid_id")

    @pytest.mark.asyncio
    async def test_get_book_invalid_id_format(self, mock_db):
        """Test that invalid ObjectId format raises error."""
        service = BookService(mock_db)

        with pytest.raises(BookNotFound):
            await service.get_book("not_a_valid_objectid")


class TestBookServiceUpdate:
    """Test BookService.update_book method."""

    @pytest.mark.asyncio
    async def test_update_book_success(self, mock_db, sample_book_data):
        """Test successful book update."""
        service = BookService(mock_db)

        # Create book
        created = await service.create_book(sample_book_data)

        # Update it
        updates = BookUpdate(pages=350)
        updated = await service.update_book(created.id, updates)

        assert updated.id == created.id
        assert updated.pages == 350
        assert updated.updated_at > created.updated_at

    @pytest.mark.asyncio
    async def test_update_book_partial(self, mock_db, sample_book_data):
        """Test partial update preserves other fields."""
        service = BookService(mock_db)

        created = await service.create_book(sample_book_data)

        updates = BookUpdate(title="New Title")
        updated = await service.update_book(created.id, updates)

        assert updated.title == "New Title"
        assert updated.author == created.author  # Unchanged

    @pytest.mark.asyncio
    async def test_update_book_not_found(self, mock_db):
        """Test updating non-existent book raises error."""
        service = BookService(mock_db)

        updates = BookUpdate(pages=100)

        with pytest.raises(BookNotFound):
            await service.update_book("invalid_id", updates)


class TestBookServiceDelete:
    """Test BookService.delete_book method."""

    @pytest.mark.asyncio
    async def test_delete_book_success(self, mock_db, sample_book_data):
        """Test successful book deletion."""
        service = BookService(mock_db)

        # Create book
        created = await service.create_book(sample_book_data)

        # Delete it
        result = await service.delete_book(created.id)
        assert result is True

        # Verify it's gone
        with pytest.raises(BookNotFound):
            await service.get_book(created.id)

    @pytest.mark.asyncio
    async def test_delete_book_not_found(self, mock_db):
        """Test deleting non-existent book raises error."""
        service = BookService(mock_db)

        with pytest.raises(BookNotFound):
            await service.delete_book("invalid_id")


class TestBookServiceList:
    """Test BookService.list_books method."""

    @pytest.mark.asyncio
    async def test_list_books_success(self, populated_db):
        """Test successful book listing."""
        service = BookService(populated_db)
        pagination = PaginationParams(page=1, limit=10)

        books, meta = await service.list_books(pagination)

        assert len(books) == 3
        assert meta.total == 3
        assert meta.page == 1
        assert meta.has_next is False

    @pytest.mark.asyncio
    async def test_list_books_pagination(self, populated_db):
        """Test pagination works correctly."""
        service = BookService(populated_db)

        # First page
        pagination = PaginationParams(page=1, limit=2)
        books1, meta1 = await service.list_books(pagination)

        assert len(books1) == 2
        assert meta1.total == 3
        assert meta1.pages == 2
        assert meta1.has_next is True

        # Second page
        pagination = PaginationParams(page=2, limit=2)
        books2, meta2 = await service.list_books(pagination)

        assert len(books2) == 1
        assert meta2.has_next is False
        assert meta2.has_prev is True

    @pytest.mark.asyncio
    async def test_list_books_with_search(self, populated_db):
        """Test search filtering."""
        service = BookService(populated_db)
        pagination = PaginationParams(page=1, limit=10)

        books, meta = await service.list_books(pagination, search="Orwell")

        assert len(books) == 1
        assert books[0]["author"] == "George Orwell"

    @pytest.mark.asyncio
    async def test_list_books_empty(self, mock_db):
        """Test listing empty collection."""
        service = BookService(mock_db)
        pagination = PaginationParams(page=1, limit=10)

        books, meta = await service.list_books(pagination)

        assert len(books) == 0
        assert meta.total == 0
        assert meta.pages == 0


class TestBookServiceSearch:
    """Test BookService.search_books method."""

    @pytest.mark.asyncio
    async def test_search_books_by_title(self, populated_db):
        """Test searching books by title."""
        service = BookService(populated_db)
        pagination = PaginationParams(page=1, limit=10)

        books, meta = await service.search_books("1984", pagination)

        assert len(books) == 1
        assert "1984" in books[0]["title"]

    @pytest.mark.asyncio
    async def test_search_books_by_author(self, populated_db):
        """Test searching books by author."""
        service = BookService(populated_db)
        pagination = PaginationParams(page=1, limit=10)

        books, meta = await service.search_books("Huxley", pagination)

        assert len(books) == 1
        assert books[0]["author"] == "Aldous Huxley"

    @pytest.mark.asyncio
    async def test_search_books_no_results(self, populated_db):
        """Test search with no results."""
        service = BookService(populated_db)
        pagination = PaginationParams(page=1, limit=10)

        books, meta = await service.search_books("NonExistent", pagination)

        assert len(books) == 0
        assert meta.total == 0


class TestBookServiceCount:
    """Test BookService.count_books method."""

    @pytest.mark.asyncio
    async def test_count_books(self, populated_db):
        """Test book counting."""
        service = BookService(populated_db)

        count = await service.count_books()

        assert count == 3

    @pytest.mark.asyncio
    async def test_count_books_empty(self, mock_db):
        """Test counting empty collection."""
        service = BookService(mock_db)

        count = await service.count_books()

        assert count == 0
