"""Reusable node functions for LangGraph workflows."""

from typing import Any, Dict

from langchain_core.messages import AIMessage, HumanMessage

from src.agents.conversation import ConversationAgent
from src.agents.faq import FAQAgent
from src.agents.intent_classifier import IntentClassifierAgent
from src.agents.order import OrderAgent
from src.agents.payment import PaymentAgent
from src.agents.product_search import ProductSearchAgent
from src.core.logging import get_logger
from src.models.enums import IntentType
from src.services.context_service import get_context_service
from src.services.llm_service import LLMService
from src.state.graph_state import ChatState

logger = get_logger(__name__)

# Get global context service
context_service = get_context_service()


def _load_context(state: ChatState) -> ChatState:
    """Load session context into state."""
    if "session_context" not in state or state["session_context"] is None:
        state["session_context"] = context_service.get_context(state["session_id"])
    return state


def _save_context(state: ChatState) -> ChatState:
    """Save session context from state."""
    if "session_context" in state and state["session_context"]:
        context_service.save_context(state["session_context"])
    return state


async def classify_intent_node(state: ChatState) -> Dict[str, Any]:
    """
    Node to classify user intent.

    Args:
        state: Current chat state

    Returns:
        Updated state with intent classification
    """
    logger.info("Classifying intent...")

    llm_service = LLMService()
    classifier = IntentClassifierAgent(llm_service=llm_service)

    try:
        # Classify intent
        classification = await classifier.classify(state["messages"])

        return {
            "intent": classification.intent,
            "intent_confidence": classification.confidence,
            "context": {
                **state.get("context", {}),
                "intent_reasoning": classification.reasoning,
            },
        }
    except Exception as e:
        logger.error(f"Intent classification failed: {e}")
        return {
            "intent": IntentType.GENERAL,
            "intent_confidence": 0.5,
        }


async def conversation_node(state: ChatState) -> Dict[str, Any]:
    """
    Node for general conversation.

    Args:
        state: Current chat state

    Returns:
        Updated state with response
    """
    logger.info("Processing conversation...")

    llm_service = LLMService()
    agent = ConversationAgent(llm_service=llm_service)

    try:
        response = await agent.process(state["messages"], state.get("context"))
        return {"final_response": response}
    except Exception as e:
        logger.error(f"Conversation processing failed: {e}")
        return {"final_response": "I apologize, but I encountered an error. Please try again."}


async def payment_node(state: ChatState) -> Dict[str, Any]:
    """
    Node for payment processing.

    Args:
        state: Current chat state

    Returns:
        Updated state with payment response
    """
    logger.info("Processing payment...")

    # Load context
    _load_context(state)

    llm_service = LLMService()
    agent = PaymentAgent(llm_service=llm_service)

    try:
        # Prepare context with session_context
        agent_context = state.get("context", {}).copy()
        if state.get("session_context"):
            agent_context["session_context"] = state["session_context"]

        response = await agent.process(
            messages=state["messages"],
            context=agent_context,
        )

        # Save context after processing
        _save_context(state)

        return {
            "messages": [AIMessage(content=response)],
            "final_response": response,
        }
    except Exception as e:
        logger.error(f"Payment processing failed: {e}")
        error_msg = "Payment processing failed. Please try again."
        return {
            "messages": [AIMessage(content=error_msg)],
            "final_response": error_msg,
        }


async def faq_node(state: ChatState) -> Dict[str, Any]:
    """
    Node for FAQ handling.

    Args:
        state: Current chat state

    Returns:
        Updated state with FAQ response
    """
    logger.info("Processing FAQ...")

    llm_service = LLMService()
    agent = FAQAgent(llm_service=llm_service)

    try:
        response = await agent.process(state["messages"], state.get("context"))
        return {"final_response": response}
    except Exception as e:
        logger.error(f"FAQ processing failed: {e}")
        return {"final_response": "I couldn't find an answer to your question. Please contact support."}


async def escalation_node(state: ChatState) -> Dict[str, Any]:
    """
    Node for escalation handling.

    Args:
        state: Current chat state

    Returns:
        Updated state with escalation response
    """
    logger.info("Processing escalation...")

    llm_service = LLMService()
    agent = EscalationAgent(llm_service=llm_service)

    try:
        response = await agent.process(state["messages"], state.get("context"))
        return {"final_response": response}
    except Exception as e:
        logger.error(f"Escalation processing failed: {e}")
        return {
            "final_response": "I'll connect you with our support team. Please hold on."
        }


async def product_search_node(state: ChatState) -> Dict[str, Any]:
    """
    Node to handle product search.

    Args:
        state: Current chat state

    Returns:
        Updated state with product search results
    """
    logger.info("Processing product search...")

    # Load context
    _load_context(state)

    llm_service = LLMService()
    agent = ProductSearchAgent(llm_service=llm_service)

    try:
        # Prepare context with session_context
        agent_context = state.get("context", {}).copy()
        if state.get("session_context"):
            agent_context["session_context"] = state["session_context"]

        # Process search
        response = await agent.process(
            messages=state["messages"],
            context=agent_context,
        )

        # Save context after processing
        _save_context(state)

        return {
            "messages": [AIMessage(content=response)],
            "final_response": response,
        }
    except Exception as e:
        logger.error(f"Product search failed: {e}")
        error_msg = "I encountered an error while searching for products. Please try again."
        return {
            "messages": [AIMessage(content=error_msg)],
            "final_response": error_msg,
        }


async def order_node(state: ChatState) -> Dict[str, Any]:
    """
    Node to handle order creation.

    Args:
        state: Current chat state

    Returns:
        Updated state with order response
    """
    logger.info("Processing order...")

    # Load context
    _load_context(state)

    llm_service = LLMService()
    agent = OrderAgent(llm_service=llm_service)

    try:
        # Prepare context with session_context
        agent_context = state.get("context", {}).copy()
        agent_context["session_id"] = state.get("session_id", "default_session")
        if state.get("session_context"):
            agent_context["session_context"] = state["session_context"]

        response = await agent.process(
            messages=state["messages"],
            context=agent_context,
        )

        # Extract order_id from context if agent set it
        if "order_id" in agent_context and state.get("session_context"):
            from src.models.session_context import ConversationState
            
            state["session_context"].pending_order_id = agent_context["order_id"]
            state["session_context"].conversation_state = ConversationState.ORDERED
            logger.info(f"Saved pending order: {agent_context['order_id']}")

        # Save context
        _save_context(state)

        return {
            "messages": [AIMessage(content=response)],
            "final_response": response,
        }
    except Exception as e:
        logger.error(f"Order creation failed: {e}")
        error_msg = "I encountered an error while creating your order. Please try again."
        return {
            "messages": [AIMessage(content=error_msg)],
            "final_response": error_msg,
        }


def route_by_intent(state: ChatState) -> str:
    """
    Route to appropriate node based on intent.

    Args:
        state: Current chat state

    Returns:
        Next node name
    """
    intent = state.get("intent", IntentType.GENERAL)
    confidence = state.get("intent_confidence", 0.0)

    logger.info(f"Routing based on intent: {intent} (confidence: {confidence})")

    # Route based on intent
    if intent == IntentType.PAYMENT:
        return "payment"
    elif intent == IntentType.FAQ:
        return "faq"
    elif intent == IntentType.ESCALATION:
        return "escalation"
    elif intent == IntentType.PRODUCT_SEARCH:
        return "product_search"
    elif intent == IntentType.ORDER:
        return "order"
    else:
        return "conversation"


def should_continue(state: ChatState) -> str:
    """
    Determine if workflow should continue or end.

    Args:
        state: Current chat state

    Returns:
        "end" or "continue"
    """
    if state.get("final_response"):
        return "end"
    return "continue"
