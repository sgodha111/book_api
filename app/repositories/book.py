"""Book repository for database operations."""

import logging
from datetime import datetime
from typing import List, Optional

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection, AsyncIOMotorDatabase

from app.models.exceptions import BookNotFound, DuplicateBook
from app.schemas.book import BookCreate, BookResponse, BookUpdate
from app.utils.pagination import PaginationMeta, paginate_query


class BookRepository:
    """Repository for book database operations."""

    def __init__(self, db: AsyncIOMotorDatabase):
        """Initialize book repository.

        Args:
            db: MongoDB database instance
        """
        self.collection: AsyncIOMotorCollection = db["books"]
        self.logger = logging.getLogger(__name__)

    async def create(self, book_data: BookCreate) -> BookResponse:
        """Create a new book.

        Args:
            book_data: Book creation data

        Raises:
            DuplicateBook: If a book with same title/author exists

        Returns:
            Created book response
        """
        # Check for duplicates
        existing = await self.collection.find_one({
            "title": book_data.title,
            "author": book_data.author,
        })

        if existing:
            raise DuplicateBook("book with this title and author")

        now = datetime.utcnow()
        book_doc = {
            **book_data.model_dump(),
            "created_at": now,
            "updated_at": now,
        }

        result = await self.collection.insert_one(book_doc)

        self.logger.info(f"Book created with ID: {result.inserted_id}")

        return BookResponse(
            id=str(result.inserted_id),
            **book_doc,
        )

    async def get_by_id(self, book_id: str) -> BookResponse:
        """Get a book by ID.

        Args:
            book_id: Book ID

        Raises:
            BookNotFound: If book doesn't exist

        Returns:
            Book response
        """
        try:
            obj_id = ObjectId(book_id)
        except Exception:
            raise BookNotFound(book_id)

        book = await self.collection.find_one({"_id": obj_id})

        if not book:
            raise BookNotFound(book_id)

        return BookResponse(
            id=str(book["_id"]),
            **{k: v for k, v in book.items() if k != "_id"},
        )

    async def list_all(
        self,
        page: int = 1,
        limit: int = 10,
        search: Optional[str] = None,
    ) -> tuple[List[dict], PaginationMeta]:
        """List all books with pagination.

        Args:
            page: Page number
            limit: Items per page
            search: Optional search query for title/author

        Returns:
            Tuple of (books, pagination_meta)
        """
        filter_query = {}

        if search:
            filter_query["$or"] = [
                {"title": {"$regex": search, "$options": "i"}},
                {"author": {"$regex": search, "$options": "i"}},
            ]

        results, pagination = await paginate_query(
            self.collection,
            filter_query,
            page=page,
            limit=limit,
            sort_by="created_at",
            sort_order=-1,
        )

        # Convert ObjectId to string
        for book in results:
            book["id"] = str(book.pop("_id"))

        return results, pagination

    async def update(self, book_id: str, book_data: BookUpdate) -> BookResponse:
        """Update a book.

        Args:
            book_id: Book ID
            book_data: Update data

        Raises:
            BookNotFound: If book doesn't exist

        Returns:
            Updated book response
        """
        try:
            obj_id = ObjectId(book_id)
        except Exception:
            raise BookNotFound(book_id)

        update_data = book_data.model_dump(exclude_none=True)

        if update_data:
            update_data["updated_at"] = datetime.utcnow()

            result = await self.collection.find_one_and_update(
                {"_id": obj_id},
                {"$set": update_data},
                return_document=True,
            )

            if not result:
                raise BookNotFound(book_id)

            self.logger.info(f"Book updated: {book_id}")

            return BookResponse(
                id=str(result["_id"]),
                **{k: v for k, v in result.items() if k != "_id"},
            )

        # No updates provided
        return await self.get_by_id(book_id)

    async def delete(self, book_id: str) -> bool:
        """Delete a book.

        Args:
            book_id: Book ID

        Raises:
            BookNotFound: If book doesn't exist

        Returns:
            True if deleted
        """
        try:
            obj_id = ObjectId(book_id)
        except Exception:
            raise BookNotFound(book_id)

        result = await self.collection.delete_one({"_id": obj_id})

        if result.deleted_count == 0:
            raise BookNotFound(book_id)

        self.logger.info(f"Book deleted: {book_id}")
        return True

    async def count(self, filter_query: Optional[dict] = None) -> int:
        """Count books matching filter.

        Args:
            filter_query: Optional filter query

        Returns:
            Number of matching books
        """
        if filter_query is None:
            filter_query = {}

        return await self.collection.count_documents(filter_query)

    async def search(
        self,
        query: str,
        page: int = 1,
        limit: int = 10,
    ) -> tuple[List[dict], PaginationMeta]:
        """Search books by title or author.

        Args:
            query: Search query
            page: Page number
            limit: Items per page

        Returns:
            Tuple of (books, pagination_meta)
        """
        filter_query = {
            "$or": [
                {"title": {"$regex": query, "$options": "i"}},
                {"author": {"$regex": query, "$options": "i"}},
                {"tags": {"$in": [query]}},
            ]
        }

        return await self.list_all(page=page, limit=limit, search=query)
