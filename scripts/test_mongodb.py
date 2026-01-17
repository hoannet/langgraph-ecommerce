"""Test MongoDB connection."""

import asyncio
from src.database.mongodb import MongoDB
from src.core.logging import get_logger

logger = get_logger(__name__)


async def test_connection():
    """Test MongoDB connection."""
    try:
        logger.info("Testing MongoDB connection...")
        await MongoDB.connect()
        
        # Test database access
        db = MongoDB.get_database()
        logger.info(f"Connected to database: {db.name}")
        
        # List collections
        collections = await db.list_collection_names()
        logger.info(f"Collections: {collections}")
        
        logger.info("✅ MongoDB connection successful!")
        
    except Exception as e:
        logger.error(f"❌ MongoDB connection failed: {e}")
        logger.error("Please ensure MongoDB is running:")
        logger.error("  Docker: docker run -d -p 27017:27017 --name mongodb mongo:latest")
        logger.error("  Or local: brew services start mongodb-community")
        
    finally:
        await MongoDB.close()


if __name__ == "__main__":
    asyncio.run(test_connection())
