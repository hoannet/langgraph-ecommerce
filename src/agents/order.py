"""Order agent for creating and managing orders."""

import json
import re
from typing import Any, Dict, List, Optional

from langchain_core.messages import BaseMessage

from src.agents.base import BaseAgent
from src.core.exceptions import AgentError
from src.core.logging import get_logger
from src.models.enums import AgentType
from src.services.llm_service import LLMService
from src.services.order_service import OrderService
from src.services.product_service import ProductService

logger = get_logger(__name__)


class OrderAgent(BaseAgent):
    """Agent for creating orders."""

    def __init__(
        self,
        llm_service: Optional[LLMService] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize order agent."""
        super().__init__(
            agent_type=AgentType.ORDER,
            llm_service=llm_service,
            config=config,
        )
        self.order_service = OrderService()
        self.product_service = ProductService()

    async def process(
        self,
        messages: List[BaseMessage],
        context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Process order creation request.

        Args:
            messages: Conversation messages
            context: Additional context (should contain session_id)

        Returns:
            Order confirmation
        """
        if not messages:
            raise AgentError("No messages provided for order creation")

        user_message = messages[-1].content
        user_message_lower = user_message.lower()
        session_id = (context or {}).get("session_id", "default_session")
        session_ctx = (context or {}).get("session_context")

        try:
            product_id = None
            quantity = 1

            # Smart selection from context
            if session_ctx and session_ctx.last_viewed_products:
                products = session_ctx.last_viewed_products
                
                # Handle references like "first one", "second", "#1", "#2", "that"
                if any(word in user_message_lower for word in ["first", "#1", "1st"]):
                    if len(products) >= 1:
                        product_id = products[0]["id"]
                        logger.info(f"Smart selection: first product -> {product_id}")
                elif any(word in user_message_lower for word in ["second", "#2", "2nd"]):
                    if len(products) >= 2:
                        product_id = products[1]["id"]
                        logger.info(f"Smart selection: second product -> {product_id}")
                elif any(word in user_message_lower for word in ["third", "#3", "3rd"]):
                    if len(products) >= 3:
                        product_id = products[2]["id"]
                        logger.info(f"Smart selection: third product -> {product_id}")
                elif any(word in user_message_lower for word in ["that", "this", "it"]):
                    # Default to first product for ambiguous references
                    if len(products) >= 1:
                        product_id = products[0]["id"]
                        logger.info(f"Smart selection: ambiguous reference -> {product_id}")

            # If no smart selection, try LLM extraction
            if not product_id:
                extraction_prompt = f"""Extract product selection from this message:

User message: {user_message}

The user wants to order a product. Extract the product ID or number.

Respond in JSON format:
{{
    "product_id": "<product_id>",
    "quantity": <number>
}}

Examples:
- "Order product prod_001" -> {{"product_id": "prod_001", "quantity": 1}}
- "I want 2 of product prod_002" -> {{"product_id": "prod_002", "quantity": 2}}

IMPORTANT: Return valid JSON only."""

                llm_response = await self.llm.ainvoke([{"role": "user", "content": extraction_prompt}])
                response_text = llm_response.content.strip()
                
                # Extract JSON
                json_match = re.search(r'\{[^}]+\}', response_text)
                if not json_match:
                    return "I couldn't understand which product you want to order. Please say 'I want the first one' or specify the product ID."

                order_data = json.loads(json_match.group())
                product_id = order_data.get("product_id")
                quantity = order_data.get("quantity", 1)

                # If product_id is a number, try to map from context
                if product_id and not product_id.startswith("prod_"):
                    try:
                        idx = int(product_id) - 1
                        if session_ctx and 0 <= idx < len(session_ctx.last_viewed_products):
                            product_id = session_ctx.last_viewed_products[idx]["id"]
                            logger.info(f"Mapped #{idx+1} to {product_id}")
                    except ValueError:
                        pass

            if not product_id or not product_id.startswith("prod_"):
                return "Please specify which product you want. You can say 'I want the first one' or provide a product ID."

            logger.info(f"Creating order for product {product_id}, quantity {quantity}")

            # Get product details
            product = await self.product_service.get_product(product_id)
            if not product:
                return f"Product {product_id} not found. Please search for products first."

            # Check stock
            if not await self.product_service.check_stock(product_id, quantity):
                return f"Sorry, {product.name} is out of stock or doesn't have enough quantity."

            # Create order
            order = await self.order_service.create_order(
                session_id=session_id,
                items=[{"product_id": product_id, "quantity": quantity}],
            )

            if not order:
                return "Failed to create order. Please try again."

            # Format order summary
            result = "✅ **Order Created Successfully!**\n\n"
            result += f"Order ID: {order.id}\n"
            result += f"Status: {order.status.value}\n\n"
            result += "**Items:**\n"
            for item in order.items:
                result += f"- {item.product_name} x{item.quantity} = ${item.subtotal:.2f}\n"
            result += f"\n**Total: ${order.total:.2f}**\n\n"
            result += "Ready to proceed with payment? Say 'Pay now' or 'I want to pay'"

            logger.info(f"Order {order.id} created successfully")
            
            # Store order_id in context for payment
            if context:
                context["order_id"] = order.id
                context["order_total"] = order.total

            return result

        except Exception as e:
            logger.error(f"Order creation failed: {e}")
            return "I encountered an error while creating your order. Please try again."
