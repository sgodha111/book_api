"""Publisher API endpoints."""

import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, status

from app.models.database import get_db
from app.services.publisher_service import PublisherService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/publishers", tags=["publishers"])


async def get_publisher_service(db=Depends(get_db)) -> PublisherService:
    """Dependency: Get publisher service instance."""
    return PublisherService(db)


@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_publisher(
    name: str,
    service: PublisherService = Depends(get_publisher_service),
) -> dict:
    """Create a new publisher.

    Query Parameters:
    - name: Publisher name (must be unique)

    Returns:
    - Created publisher with ID
    - Status: 201 Created

    Errors:
    - 409 Conflict: If publisher with same name exists
    - 422 Unprocessable Entity: If validation fails

    Example:
    ```
    POST /api/v1/publishers?name=Penguin%20Books
    ```
    """
    logger.info(f"Creating publisher: {name}")
    return await service.create_publisher(name)


@router.get("", response_model=List[dict], status_code=status.HTTP_200_OK)
async def list_publishers(
    service: PublisherService = Depends(get_publisher_service),
) -> List[dict]:
    """List all publishers with statistics.

    Returns:
    - List of publishers with:
      - name: Publisher name
      - book_count: Number of books published
      - avg_pages: Average pages per book
      - min_pages: Minimum pages in any book
      - max_pages: Maximum pages in any book
    - Status: 200 OK

    Example:
    ```
    GET /api/v1/publishers
    ```
    """
    logger.info("Listing all publishers with statistics")
    return await service.get_all_publishers_with_stats()


@router.get("/top", response_model=List[dict], status_code=status.HTTP_200_OK)
async def get_top_publishers(
    limit: int = 10,
    service: PublisherService = Depends(get_publisher_service),
) -> List[dict]:
    """Get top publishers ranked by number of books.

    Query Parameters:
    - limit: Number of top publishers to return (default: 10, max: 100)

    Returns:
    - List of top publishers with:
      - name: Publisher name
      - book_count: Number of books published
      - avg_pages: Average pages per book
    - Status: 200 OK

    Example:
    ```
    GET /api/v1/publishers/top?limit=5
    ```
    """
    logger.info(f"Getting top {limit} publishers")
    return await service.get_top_publishers(limit=limit)


@router.get(
    "/{publisher_name}/average-pages",
    response_model=dict,
    status_code=status.HTTP_200_OK,
)
async def get_publisher_average_pages(
    publisher_name: str,
    service: PublisherService = Depends(get_publisher_service),
) -> dict:
    """Get average number of pages for books by a publisher.

    Path Parameters:
    - publisher_name: Publisher name

    Returns:
    - Publisher name and average pages
    - Status: 200 OK

    Errors:
    - 404 Not Found: If publisher has no books

    Example:
    ```
    GET /api/v1/publishers/Penguin/average-pages
    ```
    """
    logger.info(f"Getting average pages for publisher: {publisher_name}")

    avg_pages = await service.get_publisher_avg_pages(publisher_name)

    return {
        "publisher": publisher_name,
        "average_pages": avg_pages,
    }


@router.get(
    "/{publisher_name}/stats",
    response_model=dict,
    status_code=status.HTTP_200_OK,
)
async def get_publisher_stats(
    publisher_name: str,
    service: PublisherService = Depends(get_publisher_service),
) -> dict:
    """Get detailed statistics for a publisher.

    Path Parameters:
    - publisher_name: Publisher name

    Returns:
    - Comprehensive statistics:
      - publisher_name: Publisher name
      - total_books: Number of books published
      - avg_pages: Average pages per book
      - min_pages: Shortest book
      - max_pages: Longest book
      - unique_authors_count: Number of different authors
    - Status: 200 OK

    Errors:
    - 404 Not Found: If publisher has no books

    Example:
    ```
    GET /api/v1/publishers/Penguin/stats
    ```
    """
    logger.info(f"Getting statistics for publisher: {publisher_name}")
    return await service.get_publisher_stats(publisher_name)


@router.get(
    "/by-tag/{tag}",
    response_model=List[dict],
    status_code=status.HTTP_200_OK,
)
async def get_publishers_by_tag(
    tag: str,
    limit: int = 10,
    service: PublisherService = Depends(get_publisher_service),
) -> List[dict]:
    """Get publishers with most books having a specific tag.

    Path Parameters:
    - tag: Book tag/genre to search for

    Query Parameters:
    - limit: Number of publishers to return (default: 10)

    Returns:
    - List of publishers with:
      - name: Publisher name
      - book_count: Number of books with this tag
      - tag: The searched tag
    - Status: 200 OK

    Example:
    ```
    GET /api/v1/publishers/by-tag/fiction?limit=5
    ```
    """
    logger.info(f"Getting publishers by tag: {tag}")
    return await service.get_publisher_by_tag_count(tag, limit=limit)


@router.get("/overview", response_model=dict, status_code=status.HTTP_200_OK)
async def get_publishers_overview(
    service: PublisherService = Depends(get_publisher_service),
) -> dict:
    """Get overview statistics of all publishers.

    Returns:
    - Statistics:
      - unique_publishers: Number of unique publishers
      - total_books: Total books across all publishers
      - avg_pages: Average pages across all books
    - Status: 200 OK

    Example:
    ```
    GET /api/v1/publishers/overview
    ```
    """
    logger.info("Getting publishers overview")
    return await service.get_publisher_overview()
