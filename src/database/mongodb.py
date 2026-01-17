"""MongoDB database connection and management."""

from typing import Optional

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import ConnectionFailure

from src.core.config import get_settings
from src.core.logging import get_logger

logger = get_logger(__name__)


class MongoDB:
    """MongoDB connection manager."""

    client: Optional[AsyncIOMotorClient] = None
    db: Optional[AsyncIOMotorDatabase] = None

    @classmethod
    async def connect(cls) -> None:
        """Connect to MongoDB."""
        try:
            settings = get_settings()
            logger.info(f"Connecting to MongoDB at {settings.mongodb_url}")
            cls.client = AsyncIOMotorClient(settings.mongodb_url)
            cls.db = cls.client[settings.mongodb_db_name]

            # Test connection
            await cls.client.admin.command("ping")
            logger.info("MongoDB connection established")

        except ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise

    @classmethod
    async def close(cls) -> None:
        """Close MongoDB connection."""
        if cls.client:
            cls.client.close()
            logger.info("MongoDB connection closed")

    @classmethod
    def get_database(cls) -> AsyncIOMotorDatabase:
        """Get database instance."""
        if cls.db is None:
            raise RuntimeError("Database not initialized. Call connect() first.")
        return cls.db

    @classmethod
    def get_collection(cls, name: str):
        """Get collection by name."""
        return cls.get_database()[name]


# Convenience function
async def get_db() -> AsyncIOMotorDatabase:
    """Get database instance."""
    return MongoDB.get_database()
