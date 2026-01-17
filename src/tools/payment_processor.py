"""Payment processing tool."""

import time
from typing import Dict, Any
from datetime import datetime

from src.core.config import get_settings
from src.core.exceptions import PaymentError
from src.core.logging import get_logger
from src.models.enums import PaymentStatus
from src.models.schemas import PaymentRequest, PaymentResponse
from src.utils.helpers import generate_transaction_id
from src.utils.validators import validate_payment_data

logger = get_logger(__name__)


class PaymentProcessor:
    """Tool for processing payments."""

    def __init__(self) -> None:
        """Initialize payment processor."""
        settings = get_settings()
        self.mock_mode = settings.payment_mock_mode
        self.timeout = settings.payment_timeout
        logger.info(f"Initialized PaymentProcessor (mock_mode={self.mock_mode})")

    def process_payment(self, payment_request: PaymentRequest) -> PaymentResponse:
        """
        Process a payment request.

        Args:
            payment_request: Payment request data

        Returns:
            Payment response

        Raises:
            PaymentError: If payment processing fails
        """
        logger.info(
            f"Processing payment: amount={payment_request.amount}, "
            f"currency={payment_request.currency}"
        )

        # Validate payment data
        payment_dict = payment_request.model_dump()
        errors = validate_payment_data(payment_dict)
        if errors:
            error_msg = "; ".join(errors)
            logger.error(f"Payment validation failed: {error_msg}")
            raise PaymentError(f"Payment validation failed: {error_msg}")

        # Generate transaction ID
        transaction_id = generate_transaction_id()

        # Mock payment processing
        if self.mock_mode:
            return self._mock_process_payment(transaction_id, payment_request)

        # Real payment processing would go here
        raise PaymentError("Real payment processing not implemented")

    def _mock_process_payment(
        self,
        transaction_id: str,
        payment_request: PaymentRequest,
    ) -> PaymentResponse:
        """
        Mock payment processing for testing.

        Args:
            transaction_id: Transaction ID
            payment_request: Payment request

        Returns:
            Payment response
        """
        # Simulate processing delay
        time.sleep(0.5)

        # Mock success for amounts < 10000
        if payment_request.amount < 10000:
            logger.info(f"Mock payment successful: {transaction_id}")
            return PaymentResponse(
                transaction_id=transaction_id,
                status=PaymentStatus.COMPLETED,
                amount=payment_request.amount,
                currency=payment_request.currency,
                message=f"Payment of {payment_request.amount} {payment_request.currency} "
                f"processed successfully. Transaction ID: {transaction_id}",
            )
        else:
            logger.warning(f"Mock payment failed: {transaction_id}")
            return PaymentResponse(
                transaction_id=transaction_id,
                status=PaymentStatus.FAILED,
                amount=payment_request.amount,
                currency=payment_request.currency,
                message="Payment failed: Amount exceeds limit for mock processing",
            )

    def get_transaction_status(self, transaction_id: str) -> Dict[str, Any]:
        """
        Get status of a transaction.

        Args:
            transaction_id: Transaction ID

        Returns:
            Transaction status dict
        """
        logger.info(f"Getting transaction status: {transaction_id}")

        # Mock implementation
        if self.mock_mode:
            return {
                "transaction_id": transaction_id,
                "status": PaymentStatus.COMPLETED.value,
                "timestamp": datetime.now().isoformat(),
                "message": "Transaction completed successfully (mock)",
            }

        raise PaymentError("Transaction lookup not implemented")


def get_payment_processor() -> PaymentProcessor:
    """Get payment processor instance."""
    return PaymentProcessor()
