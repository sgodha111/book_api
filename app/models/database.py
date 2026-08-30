"""MongoDB database initialization and management."""

import logging
from typing import Optional

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo import ASCENDING, DESCENDING
from pymongo.errors import ServerSelectionTimeoutError

from app.config import get_settings


class MongoDB:
    """MongoDB connection manager singleton."""

    _instance: Optional["MongoDB"] = None
    _client: Optional[AsyncIOMotorClient] = None
    _db: Optional[AsyncIOMotorDatabase] = None
    _connected: bool = False
    _logger = logging.getLogger(__name__)

    def __new__(cls) -> "MongoDB":
        """Implement singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def connect(self) -> AsyncIOMotorDatabase:
        """Initialize MongoDB connection and create indexes."""
        if self._db is not None and self._connected:
            self._logger.info("Using existing MongoDB connection")
            return self._db

        settings = get_settings()

        try:
            self._client = AsyncIOMotorClient(
                settings.mongodb_url,
                serverSelectionTimeoutMS=3000,
                connectTimeoutMS=5000,
            )
            # Test connection (non-blocking)
            await self._client.admin.command("ping")
            self._db = self._client[settings.database_name]
            self._connected = True

            # Create indexes asynchronously (don't wait)
            try:
                await self._create_indexes()
            except Exception as e:
                self._logger.warning(f"Failed to create indexes: {e}")

            self._logger.info("MongoDB connected successfully")
            return self._db

        except ServerSelectionTimeoutError as e:
            self._logger.warning(f"MongoDB connection timeout (will retry): {e}")
            # Initialize client anyway for future retries
            self._client = AsyncIOMotorClient(settings.mongodb_url)
            self._db = self._client[settings.database_name]
            self._connected = False
            return self._db
        except Exception as e:
            self._logger.warning(f"MongoDB connection failed (will retry): {e}")
            # Initialize client anyway for future retries
            self._client = AsyncIOMotorClient(settings.mongodb_url)
            self._db = self._client[settings.database_name]
            self._connected = False
            return self._db

    async def disconnect(self) -> None:
        """Close MongoDB connection."""
        if self._client:
            self._client.close()
            self._db = None
            self._client = None
            self._connected = False
            self._logger.info("MongoDB connection closed")

    async def _create_indexes(self) -> None:
        """Create database indexes for better query performance."""
        if not self._db:
            return

        try:
            # Books collection indexes
            books_collection = self._db["books"]
            await books_collection.create_index([("title", ASCENDING)])
            await books_collection.create_index([("author", ASCENDING)])
            await books_collection.create_index([("publisher", ASCENDING)])
            await books_collection.create_index([("created_at", DESCENDING)])
            await books_collection.create_index([("tags", ASCENDING)])

            # Authors collection indexes
            authors_collection = self._db["authors"]
            await authors_collection.create_index([("name", ASCENDING)])
            await authors_collection.create_index([("_id", ASCENDING)], unique=True)

            # Publishers collection indexes
            publishers_collection = self._db["publishers"]
            await publishers_collection.create_index([("name", ASCENDING)], unique=True)

            self._logger.info("Database indexes created successfully")
        except Exception as e:
            self._logger.warning(f"Could not create indexes: {e}")

    async def get_collection(self, collection_name: str):
        """Get a specific collection."""
        if not self._db:
            raise RuntimeError("Database not initialized. Call connect() first.")
        return self._db[collection_name]

    @property
    def db(self) -> Optional[AsyncIOMotorDatabase]:
        """Get database instance."""
        return self._db

    @property
    def client(self) -> Optional[AsyncIOMotorClient]:
        """Get client instance."""
        return self._client

    @property
    def is_connected(self) -> bool:
        """Check if connected to MongoDB."""
        return self._connected


# Singleton instance
_mongodb: Optional[MongoDB] = None


async def init_db() -> AsyncIOMotorDatabase:
    """Initialize and return database connection."""
    global _mongodb
    _mongodb = MongoDB()
    return await _mongodb.connect()


async def close_db() -> None:
    """Close database connection."""
    global _mongodb
    if _mongodb:
        await _mongodb.disconnect()


async def get_db() -> AsyncIOMotorDatabase:
    """Get database instance for dependency injection."""
    if _mongodb is None or _mongodb.db is None:
        raise RuntimeError("Database not initialized. Call init_db() in lifespan.")
    return _mongodb.db


def get_mongodb() -> MongoDB:
    """Get MongoDB singleton instance."""
    global _mongodb
    if _mongodb is None:
        _mongodb = MongoDB()
    return _mongodb
