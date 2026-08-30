"""Book service with business logic."""

import logging
from typing import Optional

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models.exceptions import BookNotFound, DuplicateBook
from app.schemas.book import BookCreate, BookResponse, BookUpdate, BookList
from app.utils.pagination import PaginationParams, PaginationMeta, create_pagination_meta


class BookService:
    """Service for book business logic."""

    def __init__(self, db: AsyncIOMotorDatabase):
        """Initialize book service.

        Args:
            db: MongoDB database instance
        """
        self.db = db
        self.collection = db["books"]
        self.logger = logging.getLogger(__name__)

    async def create_book(self, book_data: BookCreate) -> BookResponse:
        """Create a new book.

        Checks for duplicate books with same title and author.
        Automatically sets created_at and updated_at timestamps.

        Args:
            book_data: Book creation data

        Returns:
            Created book response with ID

        Raises:
            DuplicateBook: If book with same title/author exists
        """
        # Check for duplicates
        existing = await self.collection.find_one({
            "title": book_data.title,
            "author": book_data.author,
        })

        if existing:
            self.logger.warning(
                f"Duplicate book attempted: {book_data.title} by {book_data.author}"
            )
            raise DuplicateBook("book with this title and author")

        # Create document with timestamps
        from datetime import datetime
        now = datetime.utcnow()

        book_doc = {
            **book_data.model_dump(),
            "created_at": now,
            "updated_at": now,
        }

        result = await self.collection.insert_one(book_doc)

        self.logger.info(f"Book created: {result.inserted_id}")

        return BookResponse(
            id=str(result.inserted_id),
            **book_doc,
        )

    async def get_book(self, book_id: str) -> BookResponse:
        """Retrieve a single book by ID.

        Args:
            book_id: MongoDB ObjectId as string

        Returns:
            Book response with all details

        Raises:
            BookNotFound: If book doesn't exist
        """
        try:
            obj_id = ObjectId(book_id)
        except Exception:
            self.logger.debug(f"Invalid book ID format: {book_id}")
            raise BookNotFound(book_id)

        book = await self.collection.find_one({"_id": obj_id})

        if not book:
            self.logger.debug(f"Book not found: {book_id}")
            raise BookNotFound(book_id)

        return BookResponse(
            id=str(book["_id"]),
            **{k: v for k, v in book.items() if k != "_id"},
        )

    async def list_books(
        self,
        pagination: PaginationParams,
        search: Optional[str] = None,
        author: Optional[str] = None,
        publisher: Optional[str] = None,
        tags: Optional[list[str]] = None,
        min_pages: Optional[int] = None,
        max_pages: Optional[int] = None,
        sort_by: str = "created_at",
        order: str = "desc",
    ) -> tuple[list[BookList], PaginationMeta]:
        """List books with advanced filtering and pagination.

        Args:
            pagination: Pagination parameters (page, limit)
            search: Optional search query for title/author
            author: Optional author filter (case-insensitive)
            publisher: Optional publisher filter (case-insensitive)
            tags: Optional list of tags (match any tag)
            min_pages: Optional minimum page count
            max_pages: Optional maximum page count
            sort_by: Field to sort by (created_at, title, author, pages)
            order: Sort order (asc, desc)

        Returns:
            Tuple of (books, pagination_meta)
        """
        filter_query = {}

        # Text search
        if search:
            filter_query["$or"] = [
                {"title": {"$regex": search, "$options": "i"}},
                {"author": {"$regex": search, "$options": "i"}},
            ]

        # Author filter
        if author:
            filter_query["author"] = {"$regex": author, "$options": "i"}

        # Publisher filter
        if publisher:
            filter_query["publisher"] = {"$regex": publisher, "$options": "i"}

        # Tags filter (match any)
        if tags:
            filter_query["tags"] = {"$in": tags}

        # Page range filter
        if min_pages is not None or max_pages is not None:
            pages_query = {}
            if min_pages is not None:
                pages_query["$gte"] = min_pages
            if max_pages is not None:
                pages_query["$lte"] = max_pages
            filter_query["pages"] = pages_query

        # Validate sort_by field
        valid_sort_fields = {"created_at", "title", "author", "pages", "updated_at"}
        sort_field = sort_by if sort_by in valid_sort_fields else "created_at"

        # Validate order
        sort_direction = -1 if order.lower() == "desc" else 1

        # Get total count
        total = await self.collection.count_documents(filter_query)

        # Execute paginated query
        cursor = (
            self.collection.find(filter_query)
            .sort(sort_field, sort_direction)
            .skip(pagination.skip)
            .limit(pagination.limit)
        )

        books_data = await cursor.to_list(length=pagination.limit)

        # Convert to BookList responses
        books = [
            BookList(
                id=str(book["_id"]),
                **{k: v for k, v in book.items() if k != "_id"},
            )
            for book in books_data
        ]

        # Create pagination metadata
        pagination_meta = create_pagination_meta(
            page=pagination.page,
            limit=pagination.limit,
            total=total,
        )

        self.logger.info(
            f"Listed books: page={pagination.page}, limit={pagination.limit}, "
            f"total={total}, filters=[search={search}, author={author}, "
            f"publisher={publisher}, tags={tags}, pages={min_pages}-{max_pages}], "
            f"sort_by={sort_field}, order={order}"
        )

        return books, pagination_meta

    async def update_book(self, book_id: str, updates: BookUpdate) -> BookResponse:
        """Update a book with partial data.

        Only provided fields are updated. Automatically updates the updated_at timestamp.

        Args:
            book_id: Book ID to update
            updates: Partial update data

        Returns:
            Updated book response

        Raises:
            BookNotFound: If book doesn't exist
        """
        try:
            obj_id = ObjectId(book_id)
        except Exception:
            self.logger.debug(f"Invalid book ID format: {book_id}")
            raise BookNotFound(book_id)

        # Get update data excluding None values
        update_data = updates.model_dump(exclude_none=True)

        if update_data:
            from datetime import datetime
            update_data["updated_at"] = datetime.utcnow()

            # Update and return new document
            result = await self.collection.find_one_and_update(
                {"_id": obj_id},
                {"$set": update_data},
                return_document=True,
            )

            if not result:
                self.logger.debug(f"Book not found for update: {book_id}")
                raise BookNotFound(book_id)

            self.logger.info(f"Book updated: {book_id}")

            return BookResponse(
                id=str(result["_id"]),
                **{k: v for k, v in result.items() if k != "_id"},
            )

        # No updates provided, return existing
        return await self.get_book(book_id)

    async def delete_book(self, book_id: str) -> bool:
        """Delete a book by ID.

        Args:
            book_id: Book ID to delete

        Returns:
            True if deleted successfully

        Raises:
            BookNotFound: If book doesn't exist
        """
        try:
            obj_id = ObjectId(book_id)
        except Exception:
            self.logger.debug(f"Invalid book ID format: {book_id}")
            raise BookNotFound(book_id)

        result = await self.collection.delete_one({"_id": obj_id})

        if result.deleted_count == 0:
            self.logger.debug(f"Book not found for deletion: {book_id}")
            raise BookNotFound(book_id)

        self.logger.info(f"Book deleted: {book_id}")
        return True

    async def search_books(
        self,
        query: str,
        pagination: PaginationParams,
    ) -> tuple[list[BookList], PaginationMeta]:
        """Search books by title, author, or tags.

        Args:
            query: Search query string
            pagination: Pagination parameters

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

        self.logger.info(f"Searching books: query={query}, page={pagination.page}")

        return await self.list_books(pagination, search=query)

    async def count_books(self) -> int:
        """Get total number of books.

        Returns:
            Total book count
        """
        count = await self.collection.count_documents({})
        return count

    async def full_text_search(
        self,
        query: str,
        pagination: PaginationParams,
    ) -> tuple[list[BookList], PaginationMeta]:
        """Full-text search across title, author, and publisher.

        Args:
            query: Search query string
            pagination: Pagination parameters

        Returns:
            Tuple of (books, pagination_meta)
        """
        filter_query = {
            "$or": [
                {"title": {"$regex": query, "$options": "i"}},
                {"author": {"$regex": query, "$options": "i"}},
                {"publisher": {"$regex": query, "$options": "i"}},
            ]
        }

        total = await self.collection.count_documents(filter_query)

        cursor = (
            self.collection.find(filter_query)
            .sort("created_at", -1)
            .skip(pagination.skip)
            .limit(pagination.limit)
        )

        books_data = await cursor.to_list(length=pagination.limit)

        books = [
            BookList(
                id=str(book["_id"]),
                **{k: v for k, v in book.items() if k != "_id"},
            )
            for book in books_data
        ]

        pagination_meta = create_pagination_meta(
            page=pagination.page,
            limit=pagination.limit,
            total=total,
        )

        self.logger.info(f"Full-text search: query={query}, found={total}")

        return books, pagination_meta

    async def get_stats(self) -> dict:
        """Get book statistics including aggregations.

        Returns:
            Dictionary with:
            - total_books: Total book count
            - avg_pages: Average pages
            - min_pages: Minimum pages
            - max_pages: Maximum pages
            - books_by_tag: Count of books per tag
            - most_common_publisher: Publisher with most books
        """
        # Get total count
        total = await self.collection.count_documents({})

        # Aggregation pipeline for statistics
        pipeline = [
            {
                "$group": {
                    "_id": None,
                    "avg_pages": {"$avg": "$pages"},
                    "min_pages": {"$min": "$pages"},
                    "max_pages": {"$max": "$pages"},
                }
            }
        ]

        stats_data = await self.collection.aggregate(pipeline).to_list(length=1)
        stats = stats_data[0] if stats_data else {
            "avg_pages": 0,
            "min_pages": 0,
            "max_pages": 0,
        }

        # Books by tag
        tag_pipeline = [
            {"$unwind": "$tags"},
            {"$group": {"_id": "$tag", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
        ]

        tags_data = await self.collection.aggregate(tag_pipeline).to_list(length=None)
        books_by_tag = {tag["_id"]: tag["count"] for tag in tags_data} if tags_data else {}

        # Most common publisher
        publisher_pipeline = [
            {"$group": {"_id": "$publisher", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 1},
        ]

        publisher_data = await self.collection.aggregate(
            publisher_pipeline
        ).to_list(length=1)

        most_common_publisher = (
            publisher_data[0]["_id"] if publisher_data else "N/A"
        )

        self.logger.info(f"Generated book statistics: total={total}")

        return {
            "total_books": total,
            "avg_pages": round(stats.get("avg_pages", 0), 2),
            "min_pages": stats.get("min_pages", 0),
            "max_pages": stats.get("max_pages", 0),
            "books_by_tag": books_by_tag,
            "most_common_publisher": most_common_publisher,
        }

    async def get_books_by_author(
        self,
        author: str,
        pagination: PaginationParams,
    ) -> tuple[list[BookList], PaginationMeta]:
        """Get all books by a specific author.

        Args:
            author: Author name
            pagination: Pagination parameters

        Returns:
            Tuple of (books, pagination_meta)
        """
        self.logger.info(f"Getting books by author: {author}")
        return await self.list_books(pagination, search=author)

    async def get_books_by_publisher(
        self,
        publisher: str,
        pagination: PaginationParams,
    ) -> tuple[list[BookList], PaginationMeta]:
        """Get all books by a specific publisher.

        Args:
            publisher: Publisher name
            pagination: Pagination parameters

        Returns:
            Tuple of (books, pagination_meta)
        """
        filter_query = {"publisher": {"$regex": publisher, "$options": "i"}}

        total = await self.collection.count_documents(filter_query)

        cursor = (
            self.collection.find(filter_query)
            .sort("created_at", -1)
            .skip(pagination.skip)
            .limit(pagination.limit)
        )

        books_data = await cursor.to_list(length=pagination.limit)

        books = [
            BookList(
                id=str(book["_id"]),
                **{k: v for k, v in book.items() if k != "_id"},
            )
            for book in books_data
        ]

        pagination_meta = create_pagination_meta(
            page=pagination.page,
            limit=pagination.limit,
            total=total,
        )

        self.logger.info(f"Listed books by publisher: {publisher}")

        return books, pagination_meta
