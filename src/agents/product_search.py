"""Product search agent for finding products."""

import json
import re
from typing import Any, Dict, List, Optional

from langchain_core.messages import BaseMessage

from src.agents.base import BaseAgent
from src.core.exceptions import AgentError
from src.core.logging import get_logger
from src.models.enums import AgentType
from src.services.llm_service import LLMService
from src.services.product_service import ProductService

logger = get_logger(__name__)


class ProductSearchAgent(BaseAgent):
    """Agent for searching products."""

    def __init__(
        self,
        llm_service: Optional[LLMService] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize product search agent."""
        super().__init__(
            agent_type=AgentType.PRODUCT_SEARCH,
            llm_service=llm_service,
            config=config,
        )
        self.product_service = ProductService()

    async def process(
        self,
        messages: List[BaseMessage],
        context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Process product search request.

        Args:
            messages: Conversation messages
            context: Additional context

        Returns:
            Product search results
        """
        if not messages:
            raise AgentError("No messages provided for product search")

        user_message = messages[-1].content

        try:
            # Extract search query and category using LLM
            extraction_prompt = f"""Extract product search information from this message:

User message: {user_message}

Extract the search query and optional category. Categories can be: Electronics, Books, Clothing.

Respond in JSON format:
{{
    "query": "<search terms>",
    "category": "<category or null>"
}}

Examples:
- "Show me laptops" -> {{"query": "laptop", "category": "Electronics"}}
- "I want to buy books about programming" -> {{"query": "programming", "category": "Books"}}
- "Show me products" -> {{"query": "", "category": null}}

IMPORTANT: Return valid JSON only."""

            llm_response = await self.llm.ainvoke([{"role": "user", "content": extraction_prompt}])
            response_text = llm_response.content.strip()
            
            # Extract JSON
            json_match = re.search(r'\{[^}]+\}', response_text)
            if json_match:
                search_data = json.loads(json_match.group())
            else:
                search_data = {"query": user_message, "category": None}

            logger.info(f"Search data extracted: {search_data}")

            # Search products
            products = await self.product_service.search_products(
                query=search_data.get("query"),
                category=search_data.get("category"),
                max_results=10,
            )

            if not products:
                return "I couldn't find any products matching your search. Please try different keywords."

            # Save products to context if provided
            if context and "session_context" in context:
                session_ctx = context["session_context"]
                # Convert products to dict for storage
                session_ctx.last_viewed_products = [
                    {
                        "id": p.id,
                        "name": p.name,
                        "price": p.price,
                        "category": p.category,
                        "stock": p.stock,
                    }
                    for p in products
                ]
                from src.models.session_context import ConversationState
                session_ctx.conversation_state = ConversationState.BROWSING
                logger.info(f"Saved {len(products)} products to context")

            # Format results
            result = f"I found {len(products)} product(s):\n\n"
            for i, product in enumerate(products, 1):
                result += f"{i}. **{product.name}**\n"
                result += f"   Price: ${product.price:.2f}\n"
                result += f"   Category: {product.category}\n"
                result += f"   Stock: {product.stock} available\n"
                result += f"   ID: {product.id}\n\n"

            result += "\nTo order a product, say: 'I want the first one' or 'I want product #1'"

            logger.info(f"Returning {len(products)} products")
            return result

        except Exception as e:
            logger.error(f"Product search failed: {e}")
            return "I encountered an error while searching for products. Please try again."
