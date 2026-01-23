"""Payment processing tool with MongoDB and QR code generation."""

import io
import base64
from typing import Dict, Any, Optional
from datetime import datetime

import qrcode
from motor.motor_asyncio import AsyncIOMotorClient

from src.core.config import get_settings
from src.core.exceptions import PaymentError
from src.core.logging import get_logger
from src.models.enums import PaymentStatus
from src.models.schemas import PaymentRequest, PaymentResponse
from src.utils.helpers import generate_transaction_id
from src.utils.validators import validate_payment_data

logger = get_logger(__name__)


class PaymentProcessor:
    """Tool for processing payments with MongoDB and QR code generation."""

    def __init__(self) -> None:
        """Initialize payment processor."""
        settings = get_settings()
        self.timeout = settings.payment_timeout
        
        # MongoDB connection
        self.mongodb_url = settings.mongodb_url
        self.db_name = settings.mongodb_db_name
        self.client: Optional[AsyncIOMotorClient] = None
        self.db = None
        
        logger.info("Initialized PaymentProcessor with MongoDB and QR code support")

    async def _get_db(self):
        """Get or create MongoDB connection."""
        if self.client is None:
            self.client = AsyncIOMotorClient(self.mongodb_url)
            self.db = self.client[self.db_name]
            logger.info(f"Connected to MongoDB: {self.db_name}")
        return self.db

    def _generate_qr_code(self, payment_data: Dict[str, Any]) -> str:
        """
        Generate QR code for payment.

        Args:
            payment_data: Payment information to encode

        Returns:
            Base64 encoded QR code image
        """
        # Create payment URL or data string
        qr_data = (
            f"PAYMENT:{payment_data['transaction_id']}\n"
            f"AMOUNT:{payment_data['amount']}\n"
            f"CURRENCY:{payment_data['currency']}\n"
            f"DESCRIPTION:{payment_data.get('description', 'Payment')}"
        )

        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)

        # Create image
        img = qr.make_image(fill_color="black", back_color="white")

        # Convert to base64
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        img_base64 = base64.b64encode(buffer.getvalue()).decode()

        logger.info(f"Generated QR code for transaction: {payment_data['transaction_id']}")
        return f"data:image/png;base64,{img_base64}"

    async def process_payment(self, payment_request: PaymentRequest) -> PaymentResponse:
        """
        Process a payment request.

        Args:
            payment_request: Payment request data

        Returns:
            Payment response with QR code

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

        try:
            # Get database
            db = await self._get_db()

            # Create payment document
            payment_doc = {
                "transaction_id": transaction_id,
                "amount": payment_request.amount,
                "currency": payment_request.currency,
                "description": payment_request.description,
                "order_id": payment_request.order_id,  # Link to order
                "status": PaymentStatus.PENDING.value,
                "metadata": payment_request.metadata,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            }

            # Save to MongoDB
            await db.payments.insert_one(payment_doc)
            logger.info(f"Payment saved to MongoDB: {transaction_id}")

            # Generate QR code
            qr_code = self._generate_qr_code({
                "transaction_id": transaction_id,
                "amount": payment_request.amount,
                "currency": payment_request.currency,
                "description": payment_request.description,
            })

            # Build response message
            message_parts = [
                "✅ Yêu cầu thanh toán đã được tạo thành công!",
                "",
                "📋 **Thông tin thanh toán:**",
                f"- Mã giao dịch: `{transaction_id}`",
                f"- Số tiền: **{payment_request.amount:,.0f} {payment_request.currency}**",
            ]
            
            if payment_request.order_id:
                message_parts.append(f"- Mã đơn hàng: `{payment_request.order_id}`")
            
            if payment_request.description:
                message_parts.append(f"- Mô tả: {payment_request.description}")
            
            message_parts.extend([
                "",
                "⏳ **Trạng thái: CHỜ THANH TOÁN**",
                "",
                "📱 Vui lòng quét mã QR bên dưới để hoàn tất thanh toán.",
                "Sau khi thanh toán thành công, hệ thống sẽ tự động cập nhật trạng thái.",
            ])

            # Return response with QR code
            return PaymentResponse(
                transaction_id=transaction_id,
                status=PaymentStatus.PENDING,
                amount=payment_request.amount,
                currency=payment_request.currency,
                message="\n".join(message_parts),
                metadata={
                    "qr_code": qr_code,
                    "payment_url": f"/payment/confirm/{transaction_id}",
                    "order_id": payment_request.order_id,
                }
            )

        except Exception as e:
            logger.error(f"Payment processing failed: {e}")
            raise PaymentError(f"Payment processing failed: {str(e)}")

    async def confirm_payment(self, transaction_id: str) -> Dict[str, Any]:
        """
        Confirm a pending payment.

        Args:
            transaction_id: Transaction ID to confirm

        Returns:
            Updated payment status

        Raises:
            PaymentError: If confirmation fails
        """
        logger.info(f"Confirming payment: {transaction_id}")

        try:
            db = await self._get_db()

            # Find payment
            payment = await db.payments.find_one({"transaction_id": transaction_id})
            if not payment:
                raise PaymentError(f"Payment not found: {transaction_id}")

            if payment["status"] != PaymentStatus.PENDING.value:
                raise PaymentError(
                    f"Payment cannot be confirmed. Current status: {payment['status']}"
                )

            # Update status to completed
            result = await db.payments.update_one(
                {"transaction_id": transaction_id},
                {
                    "$set": {
                        "status": PaymentStatus.COMPLETED.value,
                        "confirmed_at": datetime.utcnow(),
                        "updated_at": datetime.utcnow(),
                    }
                }
            )

            if result.modified_count == 0:
                raise PaymentError("Failed to update payment status")

            logger.info(f"Payment confirmed: {transaction_id}")

            return {
                "transaction_id": transaction_id,
                "status": PaymentStatus.COMPLETED.value,
                "message": "Payment confirmed successfully",
                "confirmed_at": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"Payment confirmation failed: {e}")
            raise PaymentError(f"Payment confirmation failed: {str(e)}")

    async def get_transaction_status(self, transaction_id: str) -> Dict[str, Any]:
        """
        Get status of a transaction.

        Args:
            transaction_id: Transaction ID

        Returns:
            Transaction status dict

        Raises:
            PaymentError: If transaction not found
        """
        logger.info(f"Getting transaction status: {transaction_id}")

        try:
            db = await self._get_db()

            # Find payment
            payment = await db.payments.find_one(
                {"transaction_id": transaction_id},
                {"_id": 0}  # Exclude MongoDB _id field
            )

            if not payment:
                raise PaymentError(f"Transaction not found: {transaction_id}")

            # Convert datetime to ISO format
            if "created_at" in payment:
                payment["created_at"] = payment["created_at"].isoformat()
            if "updated_at" in payment:
                payment["updated_at"] = payment["updated_at"].isoformat()
            if "confirmed_at" in payment:
                payment["confirmed_at"] = payment["confirmed_at"].isoformat()

            return payment

        except Exception as e:
            logger.error(f"Failed to get transaction status: {e}")
            raise PaymentError(f"Failed to get transaction status: {str(e)}")

    async def close(self):
        """Close MongoDB connection."""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")


def get_payment_processor() -> PaymentProcessor:
    """Get payment processor instance."""
    return PaymentProcessor()

