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
    author: Optional[str] = None,
    publisher: Optional[str] = None,
    tags: Optional[str] = None,
    min_pages: Optional[int] = None,
    max_pages: Optional[int] = None,
    sort_by: str = "created_at",
    order: str = "desc",
    service: BookService = Depends(get_book_service),
) -> dict:
    """List all books with advanced filtering and pagination.

    Query Parameters:
    - page: Page number (1-indexed), default: 1
    - limit: Items per page (1-100), default: 10
    - search: Optional search query for title/author
    - author: Optional author filter (case-insensitive)
    - publisher: Optional publisher filter (case-insensitive)
    - tags: Optional comma-separated tags (match any tag)
    - min_pages: Optional minimum page count
    - max_pages: Optional maximum page count
    - sort_by: Field to sort by (created_at, title, author, pages, updated_at), default: created_at
    - order: Sort order (asc, desc), default: desc

    Returns:
    - List of books with pagination metadata
    - Status: 200 OK

    Examples:
    ```
    GET /api/v1/books?page=1&limit=10
    GET /api/v1/books?author=Orwell&sort_by=pages&order=desc
    GET /api/v1/books?tags=fiction,dystopian&min_pages=100&max_pages=500
    GET /api/v1/books?publisher=Penguin&sort_by=title&order=asc
    ```
    """
    pagination = PaginationParams(page=page, limit=limit)

    # Parse tags from comma-separated string
    tags_list = [t.strip() for t in tags.split(",")] if tags else None

    books, pagination_meta = await service.list_books(
        pagination=pagination,
        search=search,
        author=author,
        publisher=publisher,
        tags=tags_list,
        min_pages=min_pages,
        max_pages=max_pages,
        sort_by=sort_by,
        order=order,
    )

    logger.info(
        f"Listed books: page={page}, limit={limit}, "
        f"filters=[search={search}, author={author}, publisher={publisher}, tags={tags_list}]"
    )

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
    q: str,
    page: int = 1,
    limit: int = 10,
    service: BookService = Depends(get_book_service),
) -> dict:
    """Full-text search across title, author, and publisher.

    Query Parameters:
    - q: Search query (required)
    - page: Page number (1-indexed), default: 1
    - limit: Items per page (1-100), default: 10

    Returns:
    - List of matching books with pagination
    - Status: 200 OK

    Example:
    ```
    GET /api/v1/books/search?q=1984&page=1&limit=10
    GET /api/v1/books/search?q=Penguin
    ```
    """
    pagination = PaginationParams(page=page, limit=limit)

    books, pagination_meta = await service.full_text_search(q, pagination)

    logger.info(f"Full-text searched books: query={q}, found={pagination_meta.total}")

    return {
        "data": books,
        "pagination": pagination_meta,
    }


@router.get("/stats", response_model=dict, status_code=status.HTTP_200_OK)
async def get_book_stats(
    service: BookService = Depends(get_book_service),
) -> dict:
    """Get comprehensive book statistics.

    Returns:
    - total_books: Total number of books
    - avg_pages: Average pages per book
    - min_pages: Minimum pages in collection
    - max_pages: Maximum pages in collection
    - books_by_tag: Count of books per tag
    - most_common_publisher: Publisher with most books
    - Status: 200 OK

    Example:
    ```
    GET /api/v1/books/stats
    ```
    """
    stats = await service.get_stats()
    logger.info(f"Retrieved book statistics: {stats}")
    return stats


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


