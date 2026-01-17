"""Verify MongoDB data."""

import asyncio
from src.database.mongodb import MongoDB
from src.core.logging import get_logger

logger = get_logger(__name__)


async def verify_data():
    """Verify database has been seeded correctly."""
    try:
        await MongoDB.connect()
        db = MongoDB.get_database()
        
        # Check products collection
        products_collection = db["products"]
        product_count = await products_collection.count_documents({})
        
        logger.info(f"📊 Total products: {product_count}")
        
        if product_count == 0:
            logger.warning("⚠️  No products found! Run: python src/database/seed_data.py")
            return
        
        # Count by category
        pipeline = [
            {"$group": {"_id": "$category", "count": {"$sum": 1}}}
        ]
        categories = await products_collection.aggregate(pipeline).to_list(None)
        
        logger.info("\n📦 Products by category:")
        for cat in categories:
            logger.info(f"  - {cat['_id']}: {cat['count']} products")
        
        # Sample products
        logger.info("\n🔍 Sample products:")
        async for product in products_collection.find().limit(3):
            logger.info(f"  - {product['name']} (${product['price']}) - {product['stock']} in stock")
        
        # Check orders collection
        orders_collection = db["orders"]
        order_count = await orders_collection.count_documents({})
        logger.info(f"\n📋 Total orders: {order_count}")
        
        logger.info("\n✅ Database verification complete!")
        
    except Exception as e:
        logger.error(f"❌ Verification failed: {e}")
        raise
    finally:
        await MongoDB.close()


if __name__ == "__main__":
    asyncio.run(verify_data())
