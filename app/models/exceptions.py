"""Custom application exceptions."""

from fastapi import HTTPException, status


class BookNotFound(HTTPException):
    """Exception raised when a book is not found."""

    def __init__(self, book_id: str | None = None):
        """Initialize BookNotFound exception."""
        if book_id:
            detail = f"Book with ID '{book_id}' not found"
        else:
            detail = "Book not found"

        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
        )


class InvalidBook(HTTPException):
    """Exception raised when book data is invalid."""

    def __init__(self, message: str = "Invalid book data"):
        """Initialize InvalidBook exception."""
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message,
        )


class DuplicateBook(HTTPException):
    """Exception raised when attempting to create a duplicate book."""

    def __init__(self, field: str = "book"):
        """Initialize DuplicateBook exception."""
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"A {field} with this data already exists",
        )


class AuthorNotFound(HTTPException):
    """Exception raised when an author is not found."""

    def __init__(self, author_id: str | None = None):
        """Initialize AuthorNotFound exception."""
        if author_id:
            detail = f"Author with ID '{author_id}' not found"
        else:
            detail = "Author not found"

        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
        )


class DuplicateAuthor(HTTPException):
    """Exception raised when attempting to create a duplicate author."""

    def __init__(self, author_id: str | None = None):
        """Initialize DuplicateAuthor exception."""
        if author_id:
            detail = f"Author with ID '{author_id}' already exists"
        else:
            detail = "Author already exists"

        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
        )


class DatabaseError(HTTPException):
    """Exception raised for database operation errors."""

    def __init__(self, message: str = "Database operation failed"):
        """Initialize DatabaseError exception."""
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=message,
        )
