"""Order API routes."""

from typing import List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src.core.logging import get_logger
from src.database.models import Order, OrderStatus
from src.services.order_service import OrderService

logger = get_logger(__name__)

router = APIRouter(prefix="/orders", tags=["orders"])


class CreateOrderRequest(BaseModel):
    """Create order request."""

    session_id: str
    items: List[dict]  # List of {product_id, quantity}


@router.post("/", response_model=Order)
async def create_order(request: CreateOrderRequest) -> Order:
    """
    Create a new order.

    Args:
        request: Order creation request

    Returns:
        Created order
    """
    logger.info(f"Creating order for session: {request.session_id}")

    try:
        order = await OrderService.create_order(
            session_id=request.session_id,
            items=request.items,
        )

        if not order:
            raise HTTPException(status_code=400, detail="Failed to create order")

        return order
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create order: {e}")
        raise HTTPException(status_code=500, detail=f"Order creation failed: {str(e)}")


@router.get("/{order_id}", response_model=Order)
async def get_order(order_id: str) -> Order:
    """
    Get order by ID.

    Args:
        order_id: Order ID

    Returns:
        Order details
    """
    logger.info(f"Getting order: {order_id}")

    try:
        order = await OrderService.get_order(order_id)
        if not order:
            raise HTTPException(status_code=404, detail=f"Order {order_id} not found")
        return order
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get order: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve order")


class UpdateOrderStatusRequest(BaseModel):
    """Update order status request."""

    status: OrderStatus
    payment_id: str | None = None


@router.patch("/{order_id}/status")
async def update_order_status(
    order_id: str,
    request: UpdateOrderStatusRequest,
) -> dict:
    """
    Update order status.

    Args:
        order_id: Order ID
        request: Status update request

    Returns:
        Success message
    """
    logger.info(f"Updating order {order_id} status to {request.status}")

    try:
        success = await OrderService.update_order_status(
            order_id=order_id,
            status=request.status,
            payment_id=request.payment_id,
        )

        if not success:
            raise HTTPException(status_code=404, detail=f"Order {order_id} not found")

        return {"message": f"Order {order_id} status updated to {request.status.value}"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update order status: {e}")
        raise HTTPException(status_code=500, detail="Failed to update order status")


@router.get("/session/{session_id}", response_model=List[Order])
async def get_session_orders(session_id: str) -> List[Order]:
    """
    Get all orders for a session.

    Args:
        session_id: Session ID

    Returns:
        List of orders
    """
    logger.info(f"Getting orders for session: {session_id}")

    try:
        orders = await OrderService.get_session_orders(session_id)
        return orders
    except Exception as e:
        logger.error(f"Failed to get session orders: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve orders")
