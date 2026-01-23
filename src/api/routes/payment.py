"""Payment API routes."""

from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException

from src.core.logging import get_logger
from src.models.schemas import PaymentRequest, PaymentResponse
from src.tools.payment_processor import PaymentProcessor

logger = get_logger(__name__)

router = APIRouter(prefix="/payment", tags=["payment"])


@router.post("/process", response_model=PaymentResponse)
async def process_payment(
    request: PaymentRequest,
) -> PaymentResponse:
    """
    Process a payment request.

    Args:
        request: Payment request

    Returns:
        Payment response with QR code
    """
    logger.info(f"Processing payment: amount={request.amount}, currency={request.currency}")

    try:
        processor = PaymentProcessor()
        response = await processor.process_payment(request)
        return response
    except Exception as e:
        logger.error(f"Payment processing failed: {e}")
        raise HTTPException(status_code=400, detail=f"Payment failed: {str(e)}")


@router.post("/confirm/{transaction_id}")
async def confirm_payment(
    transaction_id: str,
) -> Dict[str, Any]:
    """
    Confirm a pending payment.

    Args:
        transaction_id: Transaction ID to confirm

    Returns:
        Confirmation result
    """
    logger.info(f"Confirming payment: {transaction_id}")

    try:
        processor = PaymentProcessor()
        result = await processor.confirm_payment(transaction_id)
        return result
    except Exception as e:
        logger.error(f"Payment confirmation failed: {e}")
        raise HTTPException(status_code=400, detail=f"Confirmation failed: {str(e)}")


@router.get("/{transaction_id}")
async def get_transaction_status(
    transaction_id: str,
) -> Dict[str, Any]:
    """
    Get transaction status.

    Args:
        transaction_id: Transaction ID

    Returns:
        Transaction status
    """
    logger.info(f"Getting transaction status: {transaction_id}")

    try:
        processor = PaymentProcessor()
        status = await processor.get_transaction_status(transaction_id)
        return status
    except Exception as e:
        logger.error(f"Failed to get transaction status: {e}")
        raise HTTPException(status_code=404, detail=f"Transaction not found: {str(e)}")
