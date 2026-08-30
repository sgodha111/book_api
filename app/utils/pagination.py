"""Pagination utilities and models."""

from dataclasses import dataclass
from typing import Any, Generic, List, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


@dataclass
class PaginationParams:
    """Pagination parameters for queries."""

    page: int = Field(default=1, ge=1, description="Page number (1-indexed)")
    limit: int = Field(default=10, ge=1, le=100, description="Items per page")

    @property
    def skip(self) -> int:
        """Calculate skip value for database queries."""
        return (self.page - 1) * self.limit

    def calculate_total_pages(self, total_items: int) -> int:
        """Calculate total number of pages."""
        return (total_items + self.limit - 1) // self.limit


class PaginationMeta(BaseModel):
    """Pagination metadata."""

    page: int = Field(..., ge=1, description="Current page number")
    limit: int = Field(..., ge=1, le=100, description="Items per page")
    total: int = Field(..., ge=0, description="Total number of items")
    pages: int = Field(..., ge=0, description="Total number of pages")
    has_next: bool = Field(..., description="Whether there's a next page")
    has_prev: bool = Field(..., description="Whether there's a previous page")

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "page": 1,
                "limit": 10,
                "total": 50,
                "pages": 5,
                "has_next": True,
                "has_prev": False,
            }
        }


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response."""

    data: List[T] = Field(..., description="List of items")
    pagination: PaginationMeta = Field(..., description="Pagination metadata")

    class Config:
        """Pydantic config."""

        arbitrary_types_allowed = True


def create_pagination_meta(
    page: int,
    limit: int,
    total: int,
) -> PaginationMeta:
    """Create pagination metadata."""
    pages = (total + limit - 1) // limit if total > 0 else 0
    return PaginationMeta(
        page=page,
        limit=limit,
        total=total,
        pages=pages,
        has_next=page < pages,
        has_prev=page > 1,
    )


async def paginate_query(
    collection: Any,
    filter_query: dict,
    page: int = 1,
    limit: int = 10,
    sort_by: str = "_id",
    sort_order: int = -1,
) -> tuple[List[dict], PaginationMeta]:
    """Execute a paginated query on a MongoDB collection.

    Args:
        collection: MongoDB collection instance
        filter_query: Query filter dictionary
        page: Page number (1-indexed)
        limit: Items per page
        sort_by: Field to sort by
        sort_order: 1 for ascending, -1 for descending

    Returns:
        Tuple of (results, pagination_meta)
    """
    # Get total count
    total = await collection.count_documents(filter_query)

    # Calculate skip
    skip = (page - 1) * limit

    # Execute query
    cursor = collection.find(filter_query).sort(sort_by, sort_order).skip(skip).limit(limit)
    results = await cursor.to_list(length=limit)

    # Create pagination metadata
    pagination = create_pagination_meta(page, limit, total)

    return results, pagination
