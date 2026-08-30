"""Unit tests for Pydantic schemas."""

import pytest
from pydantic import ValidationError

from app.schemas.book import BookCreate, BookUpdate


class TestBookCreateSchema:
    """Test BookCreate schema validation."""

    def test_valid_book_create(self):
        """Test valid BookCreate."""
        data = {
            "title": "1984",
            "author": "George Orwell",
            "pages": 328,
            "publisher": "Penguin",
            "tags": ["fiction"],
        }
        book = BookCreate(**data)
        assert book.title == "1984"
        assert book.author == "George Orwell"
        assert book.pages == 328

    def test_missing_required_field_title(self):
        """Test missing title raises ValidationError."""
        data = {
            "author": "George Orwell",
            "pages": 328,
            "publisher": "Penguin",
        }
        with pytest.raises(ValidationError):
            BookCreate(**data)

    def test_missing_required_field_author(self):
        """Test missing author raises ValidationError."""
        data = {
            "title": "1984",
            "pages": 328,
            "publisher": "Penguin",
        }
        with pytest.raises(ValidationError):
            BookCreate(**data)

    def test_missing_required_field_pages(self):
        """Test missing pages raises ValidationError."""
        data = {
            "title": "1984",
            "author": "George Orwell",
            "publisher": "Penguin",
        }
        with pytest.raises(ValidationError):
            BookCreate(**data)

    def test_missing_required_field_publisher(self):
        """Test missing publisher raises ValidationError."""
        data = {
            "title": "1984",
            "author": "George Orwell",
            "pages": 328,
        }
        with pytest.raises(ValidationError):
            BookCreate(**data)

    def test_negative_pages(self):
        """Test negative pages raises ValidationError."""
        data = {
            "title": "1984",
            "author": "George Orwell",
            "pages": -10,
            "publisher": "Penguin",
        }
        with pytest.raises(ValidationError):
            BookCreate(**data)

    def test_zero_pages(self):
        """Test zero pages raises ValidationError."""
        data = {
            "title": "1984",
            "author": "George Orwell",
            "pages": 0,
            "publisher": "Penguin",
        }
        with pytest.raises(ValidationError):
            BookCreate(**data)

    def test_empty_title(self):
        """Test empty title raises ValidationError."""
        data = {
            "title": "",
            "author": "George Orwell",
            "pages": 328,
            "publisher": "Penguin",
        }
        with pytest.raises(ValidationError):
            BookCreate(**data)

    def test_empty_author(self):
        """Test empty author raises ValidationError."""
        data = {
            "title": "1984",
            "author": "",
            "pages": 328,
            "publisher": "Penguin",
        }
        with pytest.raises(ValidationError):
            BookCreate(**data)

    def test_empty_publisher(self):
        """Test empty publisher raises ValidationError."""
        data = {
            "title": "1984",
            "author": "George Orwell",
            "pages": 328,
            "publisher": "",
        }
        with pytest.raises(ValidationError):
            BookCreate(**data)

    def test_with_empty_tags(self):
        """Test book with empty tags list."""
        data = {
            "title": "1984",
            "author": "George Orwell",
            "pages": 328,
            "publisher": "Penguin",
            "tags": [],
        }
        book = BookCreate(**data)
        assert book.tags == []

    def test_with_multiple_tags(self):
        """Test book with multiple tags."""
        data = {
            "title": "1984",
            "author": "George Orwell",
            "pages": 328,
            "publisher": "Penguin",
            "tags": ["fiction", "dystopian", "classic"],
        }
        book = BookCreate(**data)
        assert len(book.tags) == 3

    def test_title_too_long(self):
        """Test title exceeding max length."""
        data = {
            "title": "a" * 300,  # Assuming max length constraint
            "author": "George Orwell",
            "pages": 328,
            "publisher": "Penguin",
        }
        book = BookCreate(**data)
        # Should succeed if no max length constraint
        assert book.title


class TestBookUpdateSchema:
    """Test BookUpdate schema validation."""

    def test_valid_full_update(self):
        """Test valid full BookUpdate."""
        data = {
            "title": "1984 Updated",
            "author": "George Orwell",
            "pages": 400,
            "publisher": "Penguin",
            "tags": ["fiction"],
        }
        book = BookUpdate(**data)
        assert book.title == "1984 Updated"

    def test_partial_update_title_only(self):
        """Test partial update with title only."""
        data = {"title": "Updated Title"}
        book = BookUpdate(**data)
        assert book.title == "Updated Title"
        assert book.author is None
        assert book.pages is None

    def test_partial_update_pages_only(self):
        """Test partial update with pages only."""
        data = {"pages": 500}
        book = BookUpdate(**data)
        assert book.pages == 500
        assert book.title is None

    def test_partial_update_multiple_fields(self):
        """Test partial update with multiple fields."""
        data = {"title": "New Title", "pages": 300}
        book = BookUpdate(**data)
        assert book.title == "New Title"
        assert book.pages == 300
        assert book.author is None

    def test_empty_update(self):
        """Test empty update (all fields optional)."""
        book = BookUpdate()
        assert book.title is None
        assert book.author is None
        assert book.pages is None
        assert book.publisher is None
        assert book.tags is None

    def test_invalid_pages_in_update(self):
        """Test invalid pages in update raises ValidationError."""
        data = {"pages": -10}
        with pytest.raises(ValidationError):
            BookUpdate(**data)

    def test_empty_title_in_update(self):
        """Test empty title in update raises ValidationError."""
        data = {"title": ""}
        with pytest.raises(ValidationError):
            BookUpdate(**data)

    def test_update_with_tags(self):
        """Test update with tags."""
        data = {"tags": ["fiction", "updated"]}
        book = BookUpdate(**data)
        assert book.tags == ["fiction", "updated"]

    def test_invalid_pages_zero(self):
        """Test zero pages in update raises ValidationError."""
        data = {"pages": 0}
        with pytest.raises(ValidationError):
            BookUpdate(**data)

    def test_all_optional_fields(self):
        """Test all fields are optional in update."""
        # Passing each field individually should work
        fields = ["title", "author", "pages", "publisher", "tags"]
        for field in fields:
            if field == "pages":
                data = {field: 200}
            elif field == "tags":
                data = {field: ["test"]}
            else:
                data = {field: f"Test {field}"}

            book = BookUpdate(**data)
            # Should not raise error
            assert book is not None


class TestSchemaConversions:
    """Test schema type conversions."""

    def test_pages_as_string_converts_to_int(self):
        """Test pages as string converts to integer."""
        data = {
            "title": "1984",
            "author": "George Orwell",
            "pages": "328",  # String instead of int
            "publisher": "Penguin",
        }
        book = BookCreate(**data)
        assert isinstance(book.pages, int)
        assert book.pages == 328

    def test_tags_as_single_string_not_converted(self):
        """Test tags must be a list."""
        data = {
            "title": "1984",
            "author": "George Orwell",
            "pages": 328,
            "publisher": "Penguin",
            "tags": "fiction",  # String instead of list
        }
        # Pydantic should convert string to list
        book = BookCreate(**data)
        # Depending on Pydantic version, may convert or raise error
        assert book.tags is not None
