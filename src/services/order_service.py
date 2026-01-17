"""Order service for database operations."""

from datetime import datetime
from typing import List, Optional
from uuid import uuid4

from src.core.logging import get_logger
from src.database.models import Order, OrderItem, OrderStatus
from src.database.mongodb import MongoDB
from src.services.product_service import ProductService

logger = get_logger(__name__)


class OrderService:
    """Service for order operations."""

    @staticmethod
    async def create_order(
        session_id: str,
        items: List[dict],
    ) -> Optional[Order]:
        """
        Create a new order.

        Args:
            session_id: User session ID
            items: List of items with product_id and quantity

        Returns:
            Created order or None if failed
        """
        try:
            # Validate and prepare order items
            order_items = []
            total = 0.0

            for item in items:
                product = await ProductService.get_product(item["product_id"])
                if not product:
                    logger.error(f"Product not found: {item['product_id']}")
                    return None

                quantity = item.get("quantity", 1)

                # Check stock
                if not await ProductService.check_stock(product.id, quantity):
                    logger.error(f"Insufficient stock for {product.name}")
                    return None

                subtotal = product.price * quantity
                order_item = OrderItem(
                    product_id=product.id,
                    product_name=product.name,
                    quantity=quantity,
                    price=product.price,
                    subtotal=subtotal,
                )
                order_items.append(order_item)
                total += subtotal

            # Create order
            order_id = f"ord_{uuid4().hex[:12]}"
            order = Order(
                id=order_id,
                session_id=session_id,
                items=order_items,
                total=total,
                status=OrderStatus.PENDING,
            )

            # Save to database
            collection = MongoDB.get_collection("orders")
            await collection.insert_one(order.model_dump(by_alias=True))

            # Update stock
            for item in order_items:
                await ProductService.update_stock(item.product_id, -item.quantity)

            logger.info(f"Created order {order_id} with {len(order_items)} items, total: ${total}")
            return order

        except Exception as e:
            logger.error(f"Failed to create order: {e}")
            return None

    @staticmethod
    async def get_order(order_id: str) -> Optional[Order]:
        """
        Get order by ID.

        Args:
            order_id: Order ID

        Returns:
            Order or None if not found
        """
        try:
            collection = MongoDB.get_collection("orders")
            doc = await collection.find_one({"_id": order_id})

            if doc:
                return Order(**doc)
            return None

        except Exception as e:
            logger.error(f"Failed to get order {order_id}: {e}")
            return None

    @staticmethod
    async def update_order_status(
        order_id: str,
        status: OrderStatus,
        payment_id: Optional[str] = None,
    ) -> bool:
        """
        Update order status.

        Args:
            order_id: Order ID
            status: New status
            payment_id: Payment transaction ID (optional)

        Returns:
            True if successful
        """
        try:
            collection = MongoDB.get_collection("orders")
            update_dict = {
                "status": status.value,
                "updated_at": datetime.now(),
            }

            if payment_id:
                update_dict["payment_id"] = payment_id

            result = await collection.update_one(
                {"_id": order_id},
                {"$set": update_dict},
            )

            if result.modified_count > 0:
                logger.info(f"Updated order {order_id} status to {status.value}")
                return True
            return False

        except Exception as e:
            logger.error(f"Failed to update order status: {e}")
            return False

    @staticmethod
    async def get_session_orders(session_id: str) -> List[Order]:
        """
        Get all orders for a session.

        Args:
            session_id: Session ID

        Returns:
            List of orders
        """
        try:
            collection = MongoDB.get_collection("orders")
            cursor = collection.find({"session_id": session_id}).sort("created_at", -1)

            orders = []
            async for doc in cursor:
                orders.append(Order(**doc))

            return orders

        except Exception as e:
            logger.error(f"Failed to get session orders: {e}")
            return []

    @staticmethod
    def calculate_total(items: List[OrderItem]) -> float:
        """Calculate total from order items."""
        return sum(item.subtotal for item in items)
