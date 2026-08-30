"""Author API endpoints."""

import logging
from typing import List

from fastapi import APIRouter, Depends, status

from app.models.database import get_db
from app.schemas.author import AuthorCreate, AuthorResponse
from app.schemas.book import BookList
from app.services.author_service import AuthorService
from app.services.book_service import BookService
from app.utils.pagination import PaginatedResponse, PaginationParams

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/authors", tags=["authors"])


async def get_author_service(db=Depends(get_db)) -> AuthorService:
    """Dependency: Get author service instance."""
    return AuthorService(db)


async def get_book_service(db=Depends(get_db)) -> BookService:
    """Dependency: Get book service instance."""
    return BookService(db)


@router.get("", response_model=List[AuthorResponse], status_code=status.HTTP_200_OK)
async def list_authors(
    service: AuthorService = Depends(get_author_service),
) -> List[AuthorResponse]:
    """List all authors with book counts.

    Uses efficient MongoDB aggregation to compute book counts for all authors
    in a single query.

    Returns:
    - List of authors with computed book counts
    - Status: 200 OK

    Example:
    ```
    GET /api/v1/authors
    ```
    """
    logger.info("Listing all authors")
    return await service.list_authors_with_counts()


@router.get("/{author_id}", response_model=AuthorResponse, status_code=status.HTTP_200_OK)
async def get_author(
    author_id: str,
    service: AuthorService = Depends(get_author_service),
) -> AuthorResponse:
    """Get a single author with book count.

    Path Parameters:
    - author_id: Author identifier

    Returns:
    - Author details with computed book count
    - Status: 200 OK

    Errors:
    - 404 Not Found: If author doesn't exist

    Example:
    ```
    GET /api/v1/authors/orwell_george
    ```
    """
    logger.info(f"Getting author: {author_id}")
    return await service.get_author(author_id)


@router.post("", response_model=AuthorResponse, status_code=status.HTTP_201_CREATED)
async def create_author(
    author_data: AuthorCreate,
    service: AuthorService = Depends(get_author_service),
) -> AuthorResponse:
    """Create a new author.

    Request Body:
    - id: Unique author identifier (1-100 chars)
    - name: Author full name (1-255 chars)
    - birth_date: Optional birth date (YYYY-MM-DD)

    Returns:
    - Created author with book count (initially 0)
    - Status: 201 Created

    Errors:
    - 409 Conflict: If author ID already exists
    - 422 Unprocessable Entity: If validation fails

    Example:
    ```json
    POST /api/v1/authors
    {
      "id": "orwell_george",
      "name": "George Orwell",
      "birth_date": "1903-06-25"
    }
    ```
    """
    logger.info(f"Creating author: {author_data.id}")
    return await service.create_author(author_data)


@router.patch(
    "/{author_id}", response_model=AuthorResponse, status_code=status.HTTP_200_OK
)
async def update_author(
    author_id: str,
    name: str,
    birth_date: str = None,
    service: AuthorService = Depends(get_author_service),
) -> AuthorResponse:
    """Update an author's information.

    Path Parameters:
    - author_id: Author identifier

    Query Parameters:
    - name: New author name
    - birth_date: Optional new birth date (YYYY-MM-DD)

    Returns:
    - Updated author with recomputed book count
    - Status: 200 OK

    Errors:
    - 404 Not Found: If author doesn't exist
    - 422 Unprocessable Entity: If validation fails

    Example:
    ```
    PATCH /api/v1/authors/orwell_george?name=Eric%20Arthur%20Blair
    ```
    """
    logger.info(f"Updating author: {author_id}")

    from datetime import datetime

    birth_date_obj = None
    if birth_date:
        try:
            birth_date_obj = datetime.fromisoformat(birth_date).date()
        except ValueError:
            pass

    return await service.update_author(author_id, name, birth_date_obj)


@router.delete("/{author_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_author(
    author_id: str,
    service: AuthorService = Depends(get_author_service),
) -> None:
    """Delete an author.

    Path Parameters:
    - author_id: Author identifier

    Returns:
    - No content
    - Status: 204 No Content

    Note:
    - Deleting an author does NOT delete their books

    Errors:
    - 404 Not Found: If author doesn't exist

    Example:
    ```
    DELETE /api/v1/authors/orwell_george
    ```
    """
    logger.info(f"Deleting author: {author_id}")
    await service.delete_author(author_id)


@router.get(
    "/{author_id}/books",
    response_model=PaginatedResponse[BookList],
    status_code=status.HTTP_200_OK,
)
async def get_author_books(
    author_id: str,
    page: int = 1,
    limit: int = 10,
    book_service: BookService = Depends(get_book_service),
    author_service: AuthorService = Depends(get_author_service),
) -> dict:
    """Get all books by a specific author.

    Path Parameters:
    - author_id: Author identifier

    Query Parameters:
    - page: Page number (1-indexed), default: 1
    - limit: Items per page (1-100), default: 10

    Returns:
    - List of books by author with pagination
    - Status: 200 OK

    Errors:
    - 404 Not Found: If author doesn't exist

    Example:
    ```
    GET /api/v1/authors/orwell_george/books?page=1&limit=10
    ```
    """
    # Verify author exists
    author = await author_service.get_author(author_id)

    # Get books by author name
    pagination = PaginationParams(page=page, limit=limit)
    books, pagination_meta = await book_service.get_books_by_author(
        author.name, pagination
    )

    logger.info(f"Listed books for author: {author_id}")

    return {
        "data": books,
        "pagination": pagination_meta,
    }


@router.get("/stats/overview", response_model=dict, status_code=status.HTTP_200_OK)
async def get_author_stats(
    service: AuthorService = Depends(get_author_service),
) -> dict:
    """Get overview statistics about authors.

    Returns:
    - Total number of authors
    - Average books per author
    - Maximum books by single author
    - Minimum books by single author
    - Status: 200 OK

    Example:
    ```
    GET /api/v1/authors/stats/overview
    ```
    """
    logger.info("Getting author statistics")
    return await service.get_author_stats()
