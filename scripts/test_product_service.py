"""Test product service directly."""

import asyncio
from src.database.mongodb import MongoDB
from src.services.product_service import ProductService
from src.core.logging import get_logger

logger = get_logger(__name__)


async def test_product_service():
    """Test product service."""
    try:
        # Connect to MongoDB
        await MongoDB.connect()
        logger.info("✅ MongoDB connected")
        
        # Test ProductService
        service = ProductService()
        
        # Test search
        logger.info("\n🔍 Testing search for 'iPad'...")
        products = await service.search_products(query="iPad", max_results=10)
        logger.info(f"Found {len(products)} products")
        
        for product in products:
            logger.info(f"  - {product.name} (${product.price})")
        
        # Test list all
        logger.info("\n📋 Testing list all products...")
        all_products = await service.list_products(limit=20)
        logger.info(f"Total products: {len(all_products)}")
        
        # Test by category
        logger.info("\n📦 Testing search by category 'Electronics'...")
        electronics = await service.list_products(category="Electronics")
        logger.info(f"Electronics: {len(electronics)} products")
        
        if len(products) == 0:
            logger.error("❌ No products found! Database might be empty or search is broken")
        else:
            logger.info("✅ Product service working correctly!")
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await MongoDB.close()


if __name__ == "__main__":
    asyncio.run(test_product_service())
