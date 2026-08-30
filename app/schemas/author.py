"""Author request and response schemas."""

from datetime import date
from typing import Optional

from pydantic import BaseModel, Field


class AuthorCreate(BaseModel):
    """Schema for creating a new author."""

    id: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Unique author identifier",
    )
    name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Author full name",
    )
    birth_date: Optional[date] = Field(
        None,
        description="Author's birth date",
    )

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "id": "fitzgerald_f_scott",
                "name": "F. Scott Fitzgerald",
                "birth_date": "1896-09-24",
            }
        }


class AuthorResponse(BaseModel):
    """Schema for author response."""

    id: str = Field(..., description="Author ID")
    name: str = Field(..., description="Author full name")
    birth_date: Optional[date] = Field(..., description="Author's birth date")
    book_count: int = Field(
        default=0,
        ge=0,
        description="Number of books by this author",
    )

    class Config:
        """Pydantic config."""

        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "fitzgerald_f_scott",
                "name": "F. Scott Fitzgerald",
                "birth_date": "1896-09-24",
                "book_count": 5,
            }
        }
