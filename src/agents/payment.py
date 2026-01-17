"""Payment agent for handling payment requests with order integration."""

import re
from typing import Any, Dict, List, Optional

from langchain_core.messages import BaseMessage

from src.agents.base import BaseAgent
from src.core.exceptions import AgentError
from src.core.logging import get_logger
from src.models.enums import AgentType
from src.services.llm_service import LLMService
from src.tools.payment_processor import PaymentProcessor

logger = get_logger(__name__)


class PaymentAgent(BaseAgent):
    """Agent for processing payment requests."""

    def __init__(
        self,
        llm_service: Optional[LLMService] = None,
        payment_processor: Optional[PaymentProcessor] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Initialize payment agent.

        Args:
            llm_service: LLM service instance
            payment_processor: Payment processor tool
            config: Agent configuration
        """
        super().__init__(
            agent_type=AgentType.PAYMENT,
            llm_service=llm_service,
            config=config,
        )
        self.payment_processor = payment_processor or PaymentProcessor()

    async def process(
        self,
        messages: List[BaseMessage],
        context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Process payment request with order integration.

        Args:
            messages: Conversation messages
            context: Additional context

        Returns:
            Payment confirmation message
        """
        if not messages:
            raise AgentError("No messages provided for payment processing")

        user_message = messages[-1].content
        payment_data = (context or {}).get("payment_data")
        order_id = (context or {}).get("order_id")
        session_ctx = (context or {}).get("session_context")

        try:
            # Try to extract order ID from message first
            order_id_match = re.search(r'ord_[a-f0-9]+', user_message.lower())
            if order_id_match:
                order_id = order_id_match.group()
                logger.info(f"Extracted order ID from message: {order_id}")
            
            # If no order ID in message, check session context for pending order
            elif not order_id and session_ctx and session_ctx.pending_order_id:
                order_id = session_ctx.pending_order_id
                logger.info(f"Using pending order from context: {order_id}")

            # If we have an order ID, process order payment
            if order_id:
                result = await self._process_order_payment(order_id)
                
                # Clear pending order after successful payment
                if session_ctx and "successful" in result.lower():
                    from src.models.session_context import ConversationState
                    session_ctx.pending_order_id = None
                    session_ctx.conversation_state = ConversationState.COMPLETED
                    logger.info("Cleared pending order from context")
                
                return result

            # Otherwise, process regular payment
            return await self._process_regular_payment(user_message, payment_data)

        except Exception as e:
            logger.error(f"Payment processing failed: {e}")
            return f"Payment processing failed: {str(e)}. Please try again."

    async def _process_order_payment(self, order_id: str) -> str:
        """Process payment for an order."""
        from src.services.order_service import OrderService
        from src.database.models import OrderStatus

        # Get order from database
        order = await OrderService.get_order(order_id)
        if not order:
            return f"❌ Order {order_id} not found. Please check the order ID."

        if order.status == OrderStatus.PAID:
            return f"ℹ️ Order {order_id} has already been paid."

        # Create payment request
        from src.models.schemas import PaymentRequest
        
        payment_request = PaymentRequest(
            amount=order.total,
            currency="USD",
            description=f"Payment for order {order_id}",
        )

        logger.info(f"Processing payment for order {order_id}: ${order.total}")

        # Process payment
        result = self.payment_processor.process_payment(payment_request)

        # If payment successful, update order status
        if result.status.value == "completed":
            await OrderService.update_order_status(
                order_id=order_id,
                status=OrderStatus.PAID,
                payment_id=result.transaction_id,
            )
            logger.info(f"Order {order_id} updated to PAID")

            # Format success response
            response = f"""✅ **Payment Successful!**

**Order Details:**
- Order ID: `{order_id}`
- Status: **PAID** ✓

**Payment Information:**
- Transaction ID: `{result.transaction_id}`
- Amount: **${order.total:.2f}** USD
- Status: {result.status.value.upper()}

**Items Purchased:**
"""
            for item in order.items:
                response += f"- {item.product_name} x{item.quantity} = ${item.subtotal:.2f}\n"

            response += f"\n**Total Paid: ${order.total:.2f}**\n\nThank you for your purchase! 🎉"
            return response
        else:
            return f"❌ Payment failed: {result.message}"

    async def _process_regular_payment(
        self, user_message: str, payment_data: Optional[Dict] = None
    ) -> str:
        """Process regular payment (without order)."""
        # Extract payment data if not provided
        if not payment_data:
            logger.info("Extracting payment data from message...")
            try:
                from src.prompts.agent_prompts import PAYMENT_EXTRACTION_PROMPT

                extraction_prompt = PAYMENT_EXTRACTION_PROMPT.format_messages(
                    system_prompt=self.system_prompt,
                    user_message=user_message,
                )
                llm_response = await self.llm.ainvoke(extraction_prompt)

                import json
                response_text = llm_response.content.strip()
                json_match = re.search(r'\{[^}]+\}', response_text)

                if json_match:
                    payment_data = json.loads(json_match.group())
                    logger.info(f"Extracted: {payment_data}")
                else:
                    return "I couldn't extract payment info. Please specify: 'I want to pay $50' or 'Pay Order ID: ord_xxx'"

            except Exception as e:
                logger.error(f"Extraction failed: {e}")
                return "Please specify payment amount or order ID."

        amount = payment_data.get("amount")
        currency = payment_data.get("currency", "USD")
        description = payment_data.get("description", "Payment")

        if not amount:
            return "Please specify the payment amount. Example: 'I want to pay $50'"

        logger.info(f"Processing payment: ${amount} {currency}")

        # Create payment request
        from src.models.schemas import PaymentRequest
        
        payment_request = PaymentRequest(
            amount=amount,
            currency=currency,
            description=description,
        )

        # Process payment
        result = self.payment_processor.process_payment(payment_request)

        # Format response
        response = f"""✅ **Payment Processed!**

**Transaction Details:**
- Transaction ID: `{result.transaction_id}`
- Amount: **${amount}** {currency}
- Status: {result.status.value.upper()}
- Description: {description}

Thank you for your payment!"""

        return response

