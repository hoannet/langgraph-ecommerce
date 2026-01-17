"""Payment API routes."""

from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException

from src.core.logging import get_logger
from src.graphs.payment_workflow import get_payment_workflow
from src.models.schemas import PaymentRequest, PaymentResponse
from src.tools.payment_processor import PaymentProcessor
from src.utils.helpers import generate_transaction_id

logger = get_logger(__name__)

router = APIRouter(prefix="/payment", tags=["payment"])


@router.post("/process", response_model=PaymentResponse)
async def process_payment(
    request: PaymentRequest,
    processor: PaymentProcessor = Depends(PaymentProcessor),
) -> PaymentResponse:
    """
    Process a payment.

    Args:
        request: Payment request
        processor: Payment processor dependency

    Returns:
        Payment response
    """
    logger.info(f"Processing payment: amount={request.amount}, currency={request.currency}")

    try:
        response = processor.process_payment(request)
        return response
    except Exception as e:
        logger.error(f"Payment processing failed: {e}")
        raise HTTPException(status_code=400, detail=f"Payment failed: {str(e)}")


@router.get("/{transaction_id}")
async def get_transaction_status(
    transaction_id: str,
    processor: PaymentProcessor = Depends(PaymentProcessor),
) -> Dict[str, Any]:
    """
    Get transaction status.

    Args:
        transaction_id: Transaction ID
        processor: Payment processor dependency

    Returns:
        Transaction status
    """
    logger.info(f"Getting transaction status: {transaction_id}")

    try:
        status = processor.get_transaction_status(transaction_id)
        return status
    except Exception as e:
        logger.error(f"Failed to get transaction status: {e}")
        raise HTTPException(status_code=404, detail=f"Transaction not found: {str(e)}")
