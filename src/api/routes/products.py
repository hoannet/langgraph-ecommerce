"""Product API routes."""

from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query

from src.core.logging import get_logger
from src.database.models import Product
from src.services.product_service import ProductService

logger = get_logger(__name__)

router = APIRouter(prefix="/products", tags=["products"])


@router.get("/", response_model=List[Product])
async def list_products(
    category: Optional[str] = Query(None, description="Filter by category"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of products"),
) -> List[Product]:
    """
    List products with optional category filter.

    Args:
        category: Filter by category
        limit: Maximum number of products

    Returns:
        List of products
    """
    logger.info(f"Listing products: category={category}, limit={limit}")

    try:
        products = await ProductService.list_products(category=category, limit=limit)
        return products
    except Exception as e:
        logger.error(f"Failed to list products: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve products")


@router.get("/{product_id}", response_model=Product)
async def get_product(product_id: str) -> Product:
    """
    Get product by ID.

    Args:
        product_id: Product ID

    Returns:
        Product details
    """
    logger.info(f"Getting product: {product_id}")

    try:
        product = await ProductService.get_product(product_id)
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {product_id} not found")
        return product
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get product: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve product")


@router.post("/search", response_model=List[Product])
async def search_products(
    query: Optional[str] = Query(None, description="Search query"),
    category: Optional[str] = Query(None, description="Filter by category"),
    max_results: int = Query(10, ge=1, le=50, description="Maximum results"),
) -> List[Product]:
    """
    Search products by query and/or category.

    Args:
        query: Search query
        category: Filter by category
        max_results: Maximum number of results

    Returns:
        List of matching products
    """
    logger.info(f"Searching products: query={query}, category={category}")

    try:
        products = await ProductService.search_products(
            query=query,
            category=category,
            max_results=max_results,
        )
        return products
    except Exception as e:
        logger.error(f"Failed to search products: {e}")
        raise HTTPException(status_code=500, detail="Failed to search products")
