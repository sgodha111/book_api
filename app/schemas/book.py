"""Book request and response schemas."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class BookCreate(BaseModel):
    """Schema for creating a new book."""

    title: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Book title",
    )
    author: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Author name",
    )
    pages: int = Field(
        ...,
        gt=0,
        le=50000,
        description="Number of pages",
    )
    publisher: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Publisher name",
    )
    tags: List[str] = Field(
        default_factory=list,
        max_length=10,
        description="Book tags/categories",
    )

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "title": "The Great Gatsby",
                "author": "F. Scott Fitzgerald",
                "pages": 180,
                "publisher": "Scribner",
                "tags": ["fiction", "classic"],
            }
        }


class BookUpdate(BaseModel):
    """Schema for updating a book (all fields optional)."""

    title: Optional[str] = Field(
        None,
        min_length=1,
        max_length=255,
        description="Book title",
    )
    author: Optional[str] = Field(
        None,
        min_length=1,
        max_length=255,
        description="Author name",
    )
    pages: Optional[int] = Field(
        None,
        gt=0,
        le=50000,
        description="Number of pages",
    )
    publisher: Optional[str] = Field(
        None,
        min_length=1,
        max_length=255,
        description="Publisher name",
    )
    tags: Optional[List[str]] = Field(
        None,
        max_length=10,
        description="Book tags/categories",
    )

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "title": "Updated Title",
                "pages": 200,
            }
        }


class BookResponse(BaseModel):
    """Schema for book response."""

    id: str = Field(..., description="Book ID (MongoDB ObjectId)")
    title: str = Field(..., description="Book title")
    author: str = Field(..., description="Author name")
    pages: int = Field(..., description="Number of pages")
    publisher: str = Field(..., description="Publisher name")
    tags: List[str] = Field(..., description="Book tags/categories")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        """Pydantic config."""

        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "507f1f77bcf86cd799439011",
                "title": "The Great Gatsby",
                "author": "F. Scott Fitzgerald",
                "pages": 180,
                "publisher": "Scribner",
                "tags": ["fiction", "classic"],
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-15T10:30:00Z",
            }
        }


class BookList(BaseModel):
    """Schema for book list response."""

    id: str = Field(..., description="Book ID")
    title: str = Field(..., description="Book title")
    author: str = Field(..., description="Author name")
    pages: int = Field(..., description="Number of pages")
    publisher: str = Field(..., description="Publisher name")
    created_at: datetime = Field(..., description="Creation timestamp")

    class Config:
        """Pydantic config."""

        from_attributes = True
