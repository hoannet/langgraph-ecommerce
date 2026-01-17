"""Product service for database operations."""

from typing import List, Optional

from src.core.logging import get_logger
from src.database.models import Product
from src.database.mongodb import MongoDB

logger = get_logger(__name__)


class ProductService:
    """Service for product operations."""

    @staticmethod
    async def search_products(
        query: Optional[str] = None,
        category: Optional[str] = None,
        max_results: int = 10,
    ) -> List[Product]:
        """
        Search products by query and/or category.

        Args:
            query: Search query for name/description
            category: Filter by category
            max_results: Maximum number of results

        Returns:
            List of matching products
        """
        try:
            collection = MongoDB.get_collection("products")
            filter_dict = {}

            if category:
                filter_dict["category"] = category

            if query:
                filter_dict["$or"] = [
                    {"name": {"$regex": query, "$options": "i"}},
                    {"description": {"$regex": query, "$options": "i"}},
                ]

            cursor = collection.find(filter_dict).limit(max_results)
            products = []

            async for doc in cursor:
                products.append(Product(**doc))

            logger.info(f"Found {len(products)} products for query: {query}, category: {category}")
            return products

        except Exception as e:
            logger.error(f"Failed to search products: {e}")
            return []

    @staticmethod
    async def get_product(product_id: str) -> Optional[Product]:
        """
        Get product by ID.

        Args:
            product_id: Product ID

        Returns:
            Product or None if not found
        """
        try:
            collection = MongoDB.get_collection("products")
            doc = await collection.find_one({"_id": product_id})

            if doc:
                return Product(**doc)
            return None

        except Exception as e:
            logger.error(f"Failed to get product {product_id}: {e}")
            return None

    @staticmethod
    async def list_products(
        category: Optional[str] = None,
        limit: int = 20,
    ) -> List[Product]:
        """
        List products with optional category filter.

        Args:
            category: Filter by category
            limit: Maximum number of products

        Returns:
            List of products
        """
        try:
            collection = MongoDB.get_collection("products")
            filter_dict = {"category": category} if category else {}

            cursor = collection.find(filter_dict).limit(limit)
            products = []

            async for doc in cursor:
                products.append(Product(**doc))

            return products

        except Exception as e:
            logger.error(f"Failed to list products: {e}")
            return []

    @staticmethod
    async def check_stock(product_id: str, quantity: int) -> bool:
        """
        Check if product has sufficient stock.

        Args:
            product_id: Product ID
            quantity: Required quantity

        Returns:
            True if sufficient stock available
        """
        product = await ProductService.get_product(product_id)
        if not product:
            return False
        return product.stock >= quantity

    @staticmethod
    async def update_stock(product_id: str, quantity_change: int) -> bool:
        """
        Update product stock.

        Args:
            product_id: Product ID
            quantity_change: Change in quantity (negative to decrease)

        Returns:
            True if successful
        """
        try:
            collection = MongoDB.get_collection("products")
            result = await collection.update_one(
                {"_id": product_id},
                {"$inc": {"stock": quantity_change}},
            )
            return result.modified_count > 0

        except Exception as e:
            logger.error(f"Failed to update stock for {product_id}: {e}")
            return False
