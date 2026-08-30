"""Author service with business logic."""

import logging
from typing import List

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models.exceptions import AuthorNotFound, DuplicateAuthor
from app.schemas.author import AuthorCreate, AuthorResponse


class AuthorService:
    """Service for author business logic."""

    def __init__(self, db: AsyncIOMotorDatabase):
        """Initialize author service.

        Args:
            db: MongoDB database instance
        """
        self.db = db
        self.collection = db["authors"]
        self.books_collection = db["books"]
        self.logger = logging.getLogger(__name__)

    async def create_author(self, author_data: AuthorCreate) -> AuthorResponse:
        """Create a new author.

        Checks for duplicate author IDs.

        Args:
            author_data: Author creation data

        Returns:
            Created author response with book count

        Raises:
            DuplicateAuthor: If author with same ID exists
        """
        # Check for duplicate
        existing = await self.collection.find_one({"_id": author_data.id})

        if existing:
            self.logger.warning(f"Duplicate author attempted: {author_data.id}")
            raise DuplicateAuthor(author_data.id)

        # Create author document
        author_doc = author_data.model_dump()

        result = await self.collection.insert_one(author_doc)

        self.logger.info(f"Author created: {result.inserted_id}")

        return AuthorResponse(
            id=author_data.id,
            name=author_data.name,
            birth_date=author_data.birth_date,
            book_count=0,
        )

    async def get_author(self, author_id: str) -> AuthorResponse:
        """Retrieve an author with book count.

        Uses MongoDB aggregation to count books by this author.

        Args:
            author_id: Author ID

        Returns:
            Author response with computed book count

        Raises:
            AuthorNotFound: If author doesn't exist
        """
        author = await self.collection.find_one({"_id": author_id})

        if not author:
            self.logger.debug(f"Author not found: {author_id}")
            raise AuthorNotFound(author_id)

        # Count books by this author
        book_count = await self.books_collection.count_documents(
            {"author": author["name"]}
        )

        self.logger.info(f"Retrieved author: {author_id} with {book_count} books")

        return AuthorResponse(
            id=author["_id"],
            name=author["name"],
            birth_date=author.get("birth_date"),
            book_count=book_count,
        )

    async def list_authors_with_counts(self) -> List[AuthorResponse]:
        """List all authors with book counts using aggregation.

        Uses MongoDB aggregation pipeline to efficiently compute book counts
        for all authors in a single query.

        Returns:
            List of authors with computed book counts
        """
        # Aggregation pipeline to join authors with book counts
        pipeline = [
            {
                "$lookup": {
                    "from": "books",
                    "let": {"author_name": "$name"},
                    "pipeline": [
                        {
                            "$match": {
                                "$expr": {"$eq": ["$author", "$$author_name"]}
                            }
                        },
                        {"$count": "count"},
                    ],
                    "as": "books",
                }
            },
            {
                "$addFields": {
                    "book_count": {
                        "$cond": [
                            {"$eq": [{"$size": "$books"}, 0]},
                            0,
                            {"$arrayElemAt": ["$books.count", 0]},
                        ]
                    }
                }
            },
            {
                "$project": {
                    "_id": 1,
                    "name": 1,
                    "birth_date": 1,
                    "book_count": 1,
                }
            },
            {"$sort": {"name": 1}},
        ]

        cursor = self.collection.aggregate(pipeline)
        authors_data = await cursor.to_list(length=None)

        authors = [
            AuthorResponse(
                id=author["_id"],
                name=author["name"],
                birth_date=author.get("birth_date"),
                book_count=author.get("book_count", 0),
            )
            for author in authors_data
        ]

        self.logger.info(f"Listed {len(authors)} authors with book counts")

        return authors

    async def update_author(
        self, author_id: str, name: str, birth_date=None
    ) -> AuthorResponse:
        """Update author information.

        Args:
            author_id: Author ID to update
            name: New author name
            birth_date: New birth date

        Returns:
            Updated author response

        Raises:
            AuthorNotFound: If author doesn't exist
        """
        update_data = {"name": name}
        if birth_date is not None:
            update_data["birth_date"] = birth_date

        result = await self.collection.find_one_and_update(
            {"_id": author_id},
            {"$set": update_data},
            return_document=True,
        )

        if not result:
            self.logger.debug(f"Author not found for update: {author_id}")
            raise AuthorNotFound(author_id)

        # Get book count for updated author
        book_count = await self.books_collection.count_documents(
            {"author": result["name"]}
        )

        self.logger.info(f"Author updated: {author_id}")

        return AuthorResponse(
            id=result["_id"],
            name=result["name"],
            birth_date=result.get("birth_date"),
            book_count=book_count,
        )

    async def delete_author(self, author_id: str) -> bool:
        """Delete an author.

        Note: Does not delete associated books.

        Args:
            author_id: Author ID to delete

        Returns:
            True if deleted successfully

        Raises:
            AuthorNotFound: If author doesn't exist
        """
        result = await self.collection.delete_one({"_id": author_id})

        if result.deleted_count == 0:
            self.logger.debug(f"Author not found for deletion: {author_id}")
            raise AuthorNotFound(author_id)

        self.logger.info(f"Author deleted: {author_id}")
        return True

    async def get_author_stats(self) -> dict:
        """Get statistics about authors.

        Returns:
            Dictionary with author statistics
        """
        total_authors = await self.collection.count_documents({})

        # Aggregation to get stats
        pipeline = [
            {
                "$lookup": {
                    "from": "books",
                    "let": {"author_name": "$name"},
                    "pipeline": [
                        {
                            "$match": {
                                "$expr": {"$eq": ["$author", "$$author_name"]}
                            }
                        },
                        {"$count": "count"},
                    ],
                    "as": "books",
                }
            },
            {
                "$addFields": {
                    "book_count": {
                        "$cond": [
                            {"$eq": [{"$size": "$books"}, 0]},
                            0,
                            {"$arrayElemAt": ["$books.count", 0]},
                        ]
                    }
                }
            },
            {
                "$group": {
                    "_id": None,
                    "avg_books": {"$avg": "$book_count"},
                    "max_books": {"$max": "$book_count"},
                    "min_books": {"$min": "$book_count"},
                }
            },
        ]

        cursor = self.collection.aggregate(pipeline)
        stats = await cursor.to_list(length=1)

        if stats:
            stat = stats[0]
            return {
                "total_authors": total_authors,
                "average_books_per_author": round(stat.get("avg_books", 0), 2),
                "max_books_by_author": stat.get("max_books", 0),
                "min_books_by_author": stat.get("min_books", 0),
            }

        return {
            "total_authors": total_authors,
            "average_books_per_author": 0,
            "max_books_by_author": 0,
            "min_books_by_author": 0,
        }
