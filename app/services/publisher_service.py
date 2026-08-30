"""Publisher service with business logic."""

import logging
from typing import List, Optional

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models.exceptions import DatabaseError


class PublisherService:
    """Service for publisher business logic."""

    def __init__(self, db: AsyncIOMotorDatabase):
        """Initialize publisher service.

        Args:
            db: MongoDB database instance
        """
        self.db = db
        self.collection = db["publishers"]
        self.books_collection = db["books"]
        self.logger = logging.getLogger(__name__)

    async def create_publisher(self, name: str) -> dict:
        """Create a new publisher.

        Args:
            name: Publisher name

        Returns:
            Created publisher document

        Raises:
            DatabaseError: If publisher already exists
        """
        # Check for duplicate
        existing = await self.collection.find_one({"name": name})

        if existing:
            self.logger.warning(f"Duplicate publisher attempted: {name}")
            raise DatabaseError(f"Publisher '{name}' already exists")

        publisher_doc = {"name": name}

        result = await self.collection.insert_one(publisher_doc)

        self.logger.info(f"Publisher created: {result.inserted_id}")

        return {"_id": str(result.inserted_id), "name": name}

    async def get_publisher_avg_pages(self, publisher_name: str) -> float:
        """Get average number of pages for books by a publisher.

        Uses MongoDB aggregation pipeline to compute statistics.

        Args:
            publisher_name: Name of the publisher

        Returns:
            Average pages rounded to 2 decimals

        Raises:
            DatabaseError: If publisher has no books
        """
        # Aggregation pipeline to get average pages
        pipeline = [
            {"$match": {"publisher": {"$regex": publisher_name, "$options": "i"}}},
            {
                "$group": {
                    "_id": None,
                    "avg_pages": {"$avg": "$pages"},
                    "count": {"$sum": 1},
                }
            },
        ]

        cursor = self.books_collection.aggregate(pipeline)
        results = await cursor.to_list(length=1)

        if not results or results[0]["count"] == 0:
            self.logger.debug(f"No books found for publisher: {publisher_name}")
            raise DatabaseError(f"No books found for publisher: {publisher_name}")

        avg_pages = round(results[0]["avg_pages"], 2)

        self.logger.info(
            f"Publisher stats for {publisher_name}: avg_pages={avg_pages}"
        )

        return avg_pages

    async def get_all_publishers_with_stats(self) -> List[dict]:
        """Get all publishers with their book statistics.

        Uses MongoDB aggregation to compute statistics for each publisher
        efficiently in a single query.

        Returns:
            List of publishers with statistics
        """
        # Aggregation pipeline to get stats per publisher
        pipeline = [
            {
                "$group": {
                    "_id": "$publisher",
                    "count": {"$sum": 1},
                    "avg_pages": {"$avg": "$pages"},
                    "min_pages": {"$min": "$pages"},
                    "max_pages": {"$max": "$pages"},
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "name": "$_id",
                    "book_count": "$count",
                    "avg_pages": {"$round": ["$avg_pages", 2]},
                    "min_pages": 1,
                    "max_pages": 1,
                }
            },
            {"$sort": {"book_count": -1}},
        ]

        cursor = self.books_collection.aggregate(pipeline)
        publishers = await cursor.to_list(length=None)

        self.logger.info(f"Listed {len(publishers)} publishers with statistics")

        return publishers

    async def get_publisher_stats(self, publisher_name: str) -> dict:
        """Get comprehensive statistics for a publisher.

        Args:
            publisher_name: Name of the publisher

        Returns:
            Dictionary with publisher statistics

        Raises:
            DatabaseError: If publisher has no books
        """
        # Aggregation pipeline for detailed stats
        pipeline = [
            {"$match": {"publisher": {"$regex": publisher_name, "$options": "i"}}},
            {
                "$group": {
                    "_id": None,
                    "total_books": {"$sum": 1},
                    "avg_pages": {"$avg": "$pages"},
                    "min_pages": {"$min": "$pages"},
                    "max_pages": {"$max": "$pages"},
                    "median_pages": {"$avg": "$pages"},  # Approximation
                    "unique_authors": {"$addToSet": "$author"},
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "publisher_name": publisher_name,
                    "total_books": 1,
                    "avg_pages": {"$round": ["$avg_pages", 2]},
                    "min_pages": 1,
                    "max_pages": 1,
                    "unique_authors_count": {"$size": "$unique_authors"},
                }
            },
        ]

        cursor = self.books_collection.aggregate(pipeline)
        results = await cursor.to_list(length=1)

        if not results or results[0]["total_books"] == 0:
            self.logger.debug(f"No books found for publisher: {publisher_name}")
            raise DatabaseError(f"No books found for publisher: {publisher_name}")

        self.logger.info(f"Retrieved stats for publisher: {publisher_name}")

        return results[0]

    async def get_top_publishers(self, limit: int = 10) -> List[dict]:
        """Get top publishers by number of books.

        Args:
            limit: Number of top publishers to return

        Returns:
            List of top publishers with book counts
        """
        pipeline = [
            {
                "$group": {
                    "_id": "$publisher",
                    "book_count": {"$sum": 1},
                    "avg_pages": {"$avg": "$pages"},
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "name": "$_id",
                    "book_count": 1,
                    "avg_pages": {"$round": ["$avg_pages", 2]},
                }
            },
            {"$sort": {"book_count": -1}},
            {"$limit": limit},
        ]

        cursor = self.books_collection.aggregate(pipeline)
        publishers = await cursor.to_list(length=limit)

        self.logger.info(f"Retrieved top {len(publishers)} publishers by book count")

        return publishers

    async def get_publisher_by_tag_count(self, tag: str, limit: int = 10) -> List[dict]:
        """Get publishers with most books having a specific tag.

        Args:
            tag: Tag to search for
            limit: Number of publishers to return

        Returns:
            List of publishers with tag counts
        """
        pipeline = [
            {"$match": {"tags": tag}},
            {
                "$group": {
                    "_id": "$publisher",
                    "book_count": {"$sum": 1},
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "name": "$_id",
                    "book_count": 1,
                    "tag": tag,
                }
            },
            {"$sort": {"book_count": -1}},
            {"$limit": limit},
        ]

        cursor = self.books_collection.aggregate(pipeline)
        publishers = await cursor.to_list(length=limit)

        self.logger.info(
            f"Retrieved publishers with tag '{tag}': {len(publishers)} results"
        )

        return publishers

    async def get_publisher_overview() -> dict:
        """Get overview statistics of all publishers.

        Returns:
            Dictionary with overall publisher statistics
        """
        pipeline = [
            {
                "$group": {
                    "_id": None,
                    "total_publishers": {"$addToSet": "$publisher"},
                    "total_books": {"$sum": 1},
                    "avg_pages_overall": {"$avg": "$pages"},
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "unique_publishers": {"$size": "$total_publishers"},
                    "total_books": 1,
                    "avg_pages": {"$round": ["$avg_pages_overall", 2]},
                }
            },
        ]

        cursor = self.books_collection.aggregate(pipeline)
        results = await cursor.to_list(length=1)

        if results:
            return results[0]

        return {
            "unique_publishers": 0,
            "total_books": 0,
            "avg_pages": 0,
        }
