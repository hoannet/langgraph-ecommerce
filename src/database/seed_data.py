"""Seed sample data into MongoDB."""

import asyncio
from datetime import datetime

from src.database.mongodb import MongoDB
from src.core.logging import get_logger

logger = get_logger(__name__)


SAMPLE_PRODUCTS = [
    {
        "_id": "prod_001",
        "name": "MacBook Pro 16\"",
        "description": "Apple M3 Max chip, 36GB RAM, 1TB SSD",
        "price": 2999.00,
        "category": "Electronics",
        "stock": 15,
        "image_url": "https://via.placeholder.com/300x200?text=MacBook+Pro",
        "created_at": datetime.now(),
    },
    {
        "_id": "prod_002",
        "name": "Dell XPS 15",
        "description": "Intel i9, 32GB RAM, 1TB SSD, RTX 4060",
        "price": 2199.00,
        "category": "Electronics",
        "stock": 20,
        "image_url": "https://via.placeholder.com/300x200?text=Dell+XPS",
        "created_at": datetime.now(),
    },
    {
        "_id": "prod_003",
        "name": "ThinkPad X1 Carbon",
        "description": "Intel i7, 16GB RAM, 512GB SSD, Business laptop",
        "price": 1599.00,
        "category": "Electronics",
        "stock": 25,
        "image_url": "https://via.placeholder.com/300x200?text=ThinkPad",
        "created_at": datetime.now(),
    },
    {
        "_id": "prod_004",
        "name": "iPhone 15 Pro",
        "description": "256GB, Titanium Blue, A17 Pro chip",
        "price": 1199.00,
        "category": "Electronics",
        "stock": 50,
        "image_url": "https://via.placeholder.com/300x200?text=iPhone+15",
        "created_at": datetime.now(),
    },
    {
        "_id": "prod_005",
        "name": "Samsung Galaxy S24 Ultra",
        "description": "512GB, Snapdragon 8 Gen 3, S Pen included",
        "price": 1299.00,
        "category": "Electronics",
        "stock": 40,
        "image_url": "https://via.placeholder.com/300x200?text=Galaxy+S24",
        "created_at": datetime.now(),
    },
    {
        "_id": "prod_006",
        "name": "Clean Code",
        "description": "A Handbook of Agile Software Craftsmanship by Robert C. Martin",
        "price": 39.99,
        "category": "Books",
        "stock": 100,
        "image_url": "https://via.placeholder.com/300x200?text=Clean+Code",
        "created_at": datetime.now(),
    },
    {
        "_id": "prod_007",
        "name": "The Pragmatic Programmer",
        "description": "Your Journey To Mastery, 20th Anniversary Edition",
        "price": 44.99,
        "category": "Books",
        "stock": 80,
        "image_url": "https://via.placeholder.com/300x200?text=Pragmatic+Programmer",
        "created_at": datetime.now(),
    },
    {
        "_id": "prod_008",
        "name": "Design Patterns",
        "description": "Elements of Reusable Object-Oriented Software",
        "price": 54.99,
        "category": "Books",
        "stock": 60,
        "image_url": "https://via.placeholder.com/300x200?text=Design+Patterns",
        "created_at": datetime.now(),
    },
    {
        "_id": "prod_009",
        "name": "Nike Air Max 270",
        "description": "Men's running shoes, Size 9-12 available",
        "price": 149.99,
        "category": "Clothing",
        "stock": 75,
        "image_url": "https://via.placeholder.com/300x200?text=Nike+Air+Max",
        "created_at": datetime.now(),
    },
    {
        "_id": "prod_010",
        "name": "Levi's 501 Original Jeans",
        "description": "Classic straight fit, Multiple sizes and colors",
        "price": 79.99,
        "category": "Clothing",
        "stock": 120,
        "image_url": "https://via.placeholder.com/300x200?text=Levis+501",
        "created_at": datetime.now(),
    },
    {
        "_id": "prod_011",
        "name": "Sony WH-1000XM5",
        "description": "Wireless noise-canceling headphones, 30hr battery",
        "price": 399.99,
        "category": "Electronics",
        "stock": 35,
        "image_url": "https://via.placeholder.com/300x200?text=Sony+Headphones",
        "created_at": datetime.now(),
    },
    {
        "_id": "prod_012",
        "name": "iPad Pro 12.9\"",
        "description": "M2 chip, 256GB, Wi-Fi + Cellular",
        "price": 1299.00,
        "category": "Electronics",
        "stock": 30,
        "image_url": "https://via.placeholder.com/300x200?text=iPad+Pro",
        "created_at": datetime.now(),
    },
]


async def seed_products():
    """Seed sample products into database."""
    try:
        await MongoDB.connect()
        db = MongoDB.get_database()
        products_collection = db["products"]

        # Clear existing products
        await products_collection.delete_many({})
        logger.info("Cleared existing products")

        # Insert sample products
        result = await products_collection.insert_many(SAMPLE_PRODUCTS)
        logger.info(f"Inserted {len(result.inserted_ids)} products")

        # Create indexes
        await products_collection.create_index("category")
        await products_collection.create_index("name")
        logger.info("Created indexes")

        logger.info("✅ Database seeded successfully!")

    except Exception as e:
        logger.error(f"Failed to seed database: {e}")
        raise
    finally:
        await MongoDB.close()


if __name__ == "__main__":
    asyncio.run(seed_products())
