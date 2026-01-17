"""Main chat workflow using LangGraph."""

from typing import Any, Dict

from langgraph.graph import END, StateGraph
from langgraph.checkpoint.memory import MemorySaver

from src.core.logging import get_logger
from src.graphs.nodes import (
    classify_intent_node,
    conversation_node,
    escalation_node,
    faq_node,
    order_node,
    payment_node,
    product_search_node,
    route_by_intent,
)
from src.state.graph_state import ChatState

logger = get_logger(__name__)


def create_chat_workflow() -> StateGraph:
    """
    Create the main chat workflow graph.

    Returns:
        Compiled StateGraph
    """
    logger.info("Creating chat workflow...")

    # Create graph
    workflow = StateGraph(ChatState)

    # Add nodes
    workflow.add_node("classify_intent", classify_intent_node)
    workflow.add_node("conversation", conversation_node)
    workflow.add_node("payment", payment_node)
    workflow.add_node("faq", faq_node)
    workflow.add_node("escalation", escalation_node)
    workflow.add_node("product_search", product_search_node)
    workflow.add_node("order", order_node)

    # Set entry point
    workflow.set_entry_point("classify_intent")

    # Add conditional routing from intent classification
    workflow.add_conditional_edges(
        "classify_intent",
        route_by_intent,
        {
            "conversation": "conversation",
            "payment": "payment",
            "faq": "faq",
            "escalation": "escalation",
            "product_search": "product_search",
            "order": "order",
        },
    )

    # All agent nodes lead to END
    workflow.add_edge("conversation", END)
    workflow.add_edge("payment", END)
    workflow.add_edge("faq", END)
    workflow.add_edge("escalation", END)
    workflow.add_edge("product_search", END)
    workflow.add_edge("order", END)

    logger.info("Chat workflow created successfully")
    return workflow


def get_chat_workflow(checkpointer: Any = None) -> Any:
    """
    Get compiled chat workflow.

    Args:
        checkpointer: Optional checkpointer for state persistence

    Returns:
        Compiled workflow
    """
    workflow = create_chat_workflow()

    # Use memory saver if no checkpointer provided
    if checkpointer is None:
        checkpointer = MemorySaver()

    return workflow.compile(checkpointer=checkpointer)
