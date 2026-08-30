"""Book API endpoints."""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, status

from app.models.database import get_db
from app.schemas.book import BookCreate, BookResponse, BookUpdate, BookList
from app.services.book_service import BookService
from app.utils.pagination import PaginatedResponse, PaginationParams, PaginationMeta

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/books", tags=["books"])


async def get_book_service(db=Depends(get_db)) -> BookService:
    """Dependency: Get book service instance."""
    return BookService(db)


@router.get("", response_model=PaginatedResponse[BookList], status_code=status.HTTP_200_OK)
async def list_books(
    page: int = 1,
    limit: int = 10,
    search: Optional[str] = None,
    service: BookService = Depends(get_book_service),
) -> dict:
    """List all books with pagination and optional search.

    Query Parameters:
    - page: Page number (1-indexed), default: 1
    - limit: Items per page (1-100), default: 10
    - search: Optional search query for title/author

    Returns:
    - List of books with pagination metadata
    - Status: 200 OK

    Example:
    ```
    GET /api/v1/books?page=1&limit=10&search=orwell
    ```
    """
    pagination = PaginationParams(page=page, limit=limit)

    books, pagination_meta = await service.list_books(pagination, search=search)

    logger.info(f"Listed books: page={page}, limit={limit}, search={search}")

    return {
        "data": books,
        "pagination": pagination_meta,
    }


@router.get("/{book_id}", response_model=BookResponse, status_code=status.HTTP_200_OK)
async def get_book(
    book_id: str,
    service: BookService = Depends(get_book_service),
) -> BookResponse:
    """Get a single book by ID.

    Path Parameters:
    - book_id: MongoDB ObjectId as string

    Returns:
    - Book with all details
    - Status: 200 OK

    Errors:
    - 404 Not Found: If book doesn't exist

    Example:
    ```
    GET /api/v1/books/507f1f77bcf86cd799439011
    ```
    """
    logger.info(f"Getting book: {book_id}")
    return await service.get_book(book_id)


@router.post("", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
async def create_book(
    book_data: BookCreate,
    service: BookService = Depends(get_book_service),
) -> BookResponse:
    """Create a new book.

    Request Body:
    - title: Book title (1-255 chars)
    - author: Author name (1-255 chars)
    - pages: Number of pages (1-50000)
    - publisher: Publisher name (1-255 chars)
    - tags: Optional list of tags (max 10)

    Returns:
    - Created book with ID and timestamps
    - Status: 201 Created

    Errors:
    - 409 Conflict: If book with same title/author exists
    - 422 Unprocessable Entity: If validation fails

    Example:
    ```json
    POST /api/v1/books
    {
      "title": "1984",
      "author": "George Orwell",
      "pages": 328,
      "publisher": "Penguin",
      "tags": ["fiction", "dystopian"]
    }
    ```
    """
    logger.info(f"Creating book: {book_data.title} by {book_data.author}")
    return await service.create_book(book_data)


@router.patch("/{book_id}", response_model=BookResponse, status_code=status.HTTP_200_OK)
async def update_book(
    book_id: str,
    updates: BookUpdate,
    service: BookService = Depends(get_book_service),
) -> BookResponse:
    """Update a book with partial data.

    Path Parameters:
    - book_id: MongoDB ObjectId as string

    Request Body (all fields optional):
    - title: New title
    - author: New author
    - pages: New page count
    - publisher: New publisher
    - tags: New tags list

    Returns:
    - Updated book
    - Status: 200 OK

    Errors:
    - 404 Not Found: If book doesn't exist
    - 422 Unprocessable Entity: If validation fails

    Example:
    ```json
    PATCH /api/v1/books/507f1f77bcf86cd799439011
    {
      "pages": 330
    }
    ```
    """
    logger.info(f"Updating book: {book_id}")
    return await service.update_book(book_id, updates)


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(
    book_id: str,
    service: BookService = Depends(get_book_service),
) -> None:
    """Delete a book by ID.

    Path Parameters:
    - book_id: MongoDB ObjectId as string

    Returns:
    - No content
    - Status: 204 No Content

    Errors:
    - 404 Not Found: If book doesn't exist

    Example:
    ```
    DELETE /api/v1/books/507f1f77bcf86cd799439011
    ```
    """
    logger.info(f"Deleting book: {book_id}")
    await service.delete_book(book_id)


@router.get(
    "/search",
    response_model=PaginatedResponse[BookList],
    status_code=status.HTTP_200_OK,
)
async def search_books(
    query: str,
    page: int = 1,
    limit: int = 10,
    service: BookService = Depends(get_book_service),
) -> dict:
    """Search books by title, author, or tags.

    Query Parameters:
    - query: Search query (required)
    - page: Page number (1-indexed), default: 1
    - limit: Items per page (1-100), default: 10

    Returns:
    - List of matching books with pagination
    - Status: 200 OK

    Example:
    ```
    GET /api/v1/books/search?query=orwell&page=1&limit=10
    ```
    """
    pagination = PaginationParams(page=page, limit=limit)

    books, pagination_meta = await service.search_books(query, pagination)

    logger.info(f"Searched books: query={query}, found={pagination_meta.total}")

    return {
        "data": books,
        "pagination": pagination_meta,
    }


@router.get(
    "/author/{author}",
    response_model=PaginatedResponse[BookList],
    status_code=status.HTTP_200_OK,
)
async def get_books_by_author(
    author: str,
    page: int = 1,
    limit: int = 10,
    service: BookService = Depends(get_book_service),
) -> dict:
    """Get all books by a specific author.

    Path Parameters:
    - author: Author name

    Query Parameters:
    - page: Page number (1-indexed), default: 1
    - limit: Items per page (1-100), default: 10

    Returns:
    - List of books by author with pagination
    - Status: 200 OK

    Example:
    ```
    GET /api/v1/books/author/George%20Orwell?page=1&limit=10
    ```
    """
    pagination = PaginationParams(page=page, limit=limit)

    books, pagination_meta = await service.get_books_by_author(author, pagination)

    logger.info(f"Listed books by author: {author}")

    return {
        "data": books,
        "pagination": pagination_meta,
    }


@router.get(
    "/publisher/{publisher}",
    response_model=PaginatedResponse[BookList],
    status_code=status.HTTP_200_OK,
)
async def get_books_by_publisher(
    publisher: str,
    page: int = 1,
    limit: int = 10,
    service: BookService = Depends(get_book_service),
) -> dict:
    """Get all books by a specific publisher.

    Path Parameters:
    - publisher: Publisher name

    Query Parameters:
    - page: Page number (1-indexed), default: 1
    - limit: Items per page (1-100), default: 10

    Returns:
    - List of books by publisher with pagination
    - Status: 200 OK

    Example:
    ```
    GET /api/v1/books/publisher/Penguin?page=1&limit=10
    ```
    """
    pagination = PaginationParams(page=page, limit=limit)

    books, pagination_meta = await service.get_books_by_publisher(publisher, pagination)

    logger.info(f"Listed books by publisher: {publisher}")

    return {
        "data": books,
        "pagination": pagination_meta,
    }


@router.get("/stats/count", response_model=dict, status_code=status.HTTP_200_OK)
async def get_book_count(
    service: BookService = Depends(get_book_service),
) -> dict:
    """Get total number of books.

    Returns:
    - Total book count
    - Status: 200 OK

    Example:
    ```
    GET /api/v1/books/stats/count
    ```
    """
    count = await service.count_books()
    logger.info(f"Total books: {count}")
    return {"total": count}
