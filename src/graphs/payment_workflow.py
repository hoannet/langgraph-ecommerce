"""Payment workflow for handling payment processing."""

from typing import Any, Dict

from langgraph.graph import END, StateGraph
from langgraph.checkpoint.memory import MemorySaver

from src.core.logging import get_logger
from src.models.enums import PaymentStatus
from src.state.graph_state import PaymentState
from src.tools.payment_processor import PaymentProcessor
from src.utils.validators import validate_payment_data

logger = get_logger(__name__)


async def validate_payment_node(state: PaymentState) -> Dict[str, Any]:
    """
    Validate payment data.

    Args:
        state: Payment state

    Returns:
        Updated state with validation results
    """
    logger.info("Validating payment...")

    payment_data = {
        "amount": state.get("amount"),
        "currency": state.get("currency"),
    }

    errors = validate_payment_data(payment_data)

    if errors:
        return {
            "status": PaymentStatus.FAILED,
            "validation_errors": errors,
        }

    return {
        "status": PaymentStatus.PENDING,
        "validation_errors": [],
    }


async def process_payment_node(state: PaymentState) -> Dict[str, Any]:
    """
    Process payment.

    Args:
        state: Payment state

    Returns:
        Updated state with processing results
    """
    logger.info(f"Processing payment: {state.get('transaction_id')}")

    processor = PaymentProcessor()

    try:
        from src.models.schemas import PaymentRequest

        payment_request = PaymentRequest(
            amount=state["amount"],
            currency=state.get("currency", "USD"),
            description=state.get("description"),
            metadata=state.get("metadata", {}),
        )

        response = processor.process_payment(payment_request)

        return {
            "status": response.status,
            "transaction_id": response.transaction_id,
        }
    except Exception as e:
        logger.error(f"Payment processing failed: {e}")
        return {
            "status": PaymentStatus.FAILED,
            "validation_errors": [str(e)],
        }


def should_process_payment(state: PaymentState) -> str:
    """
    Determine if payment should be processed.

    Args:
        state: Payment state

    Returns:
        Next node name
    """
    if state.get("validation_errors"):
        return "end"
    return "process"


def create_payment_workflow() -> StateGraph:
    """
    Create payment workflow graph.

    Returns:
        StateGraph for payment processing
    """
    logger.info("Creating payment workflow...")

    workflow = StateGraph(PaymentState)

    # Add nodes
    workflow.add_node("validate", validate_payment_node)
    workflow.add_node("process", process_payment_node)

    # Set entry point
    workflow.set_entry_point("validate")

    # Add conditional routing
    workflow.add_conditional_edges(
        "validate",
        should_process_payment,
        {
            "process": "process",
            "end": END,
        },
    )

    # Process leads to END
    workflow.add_edge("process", END)

    logger.info("Payment workflow created successfully")
    return workflow


def get_payment_workflow(checkpointer: Any = None) -> Any:
    """
    Get compiled payment workflow.

    Args:
        checkpointer: Optional checkpointer

    Returns:
        Compiled workflow
    """
    workflow = create_payment_workflow()

    if checkpointer is None:
        checkpointer = MemorySaver()

    return workflow.compile(checkpointer=checkpointer)
