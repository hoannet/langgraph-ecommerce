"""Chat API routes."""

from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException
from langchain_core.messages import HumanMessage

from src.core.logging import get_logger
from src.graphs.chat_workflow import get_chat_workflow
from src.memory.conversation import SessionMemoryManager
from src.models.schemas import ChatRequest, ChatResponse
from src.utils.helpers import generate_session_id

logger = get_logger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    workflow: Any = Depends(get_chat_workflow),
) -> ChatResponse:
    """
    Process a chat message.

    Args:
        request: Chat request
        workflow: Chat workflow dependency

    Returns:
        Chat response
    """
    logger.info(f"Received chat request: session_id={request.session_id}")

    # Generate session ID if not provided
    session_id = request.session_id or generate_session_id()

    try:
        # Create initial state
        initial_state = {
            "messages": [HumanMessage(content=request.message)],
            "session_id": session_id,
            "context": request.metadata,
        }

        # Configure workflow with session
        config = {"configurable": {"thread_id": session_id}}

        # Run workflow
        result = await workflow.ainvoke(initial_state, config=config)

        # Extract response
        response_message = result.get("final_response", "I'm sorry, I couldn't process your request.")
        intent = result.get("intent")

        return ChatResponse(
            message=response_message,
            session_id=session_id,
            intent=intent,
            metadata={
                "intent_confidence": result.get("intent_confidence"),
            },
        )

    except Exception as e:
        logger.error(f"Chat processing failed: {e}")
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(e)}")


@router.get("/{session_id}/history")
async def get_chat_history(
    session_id: str,
    session_manager: SessionMemoryManager = Depends(),
) -> Dict[str, Any]:
    """
    Get chat history for a session.

    Args:
        session_id: Session ID
        session_manager: Session memory manager

    Returns:
        Chat history
    """
    logger.info(f"Getting chat history for session: {session_id}")

    try:
        memory = session_manager.get_session(session_id)
        messages = memory.get_messages()

        return {
            "session_id": session_id,
            "message_count": len(messages),
            "messages": [
                {
                    "role": msg.type,
                    "content": msg.content,
                }
                for msg in messages
            ],
        }
    except Exception as e:
        logger.error(f"Failed to get chat history: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get history: {str(e)}")


@router.post("/{session_id}/clear")
async def clear_chat_history(
    session_id: str,
    session_manager: SessionMemoryManager = Depends(),
) -> Dict[str, str]:
    """
    Clear chat history for a session.

    Args:
        session_id: Session ID
        session_manager: Session memory manager

    Returns:
        Success message
    """
    logger.info(f"Clearing chat history for session: {session_id}")

    try:
        session_manager.clear_session(session_id)
        return {"message": f"Chat history cleared for session {session_id}"}
    except Exception as e:
        logger.error(f"Failed to clear chat history: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to clear history: {str(e)}")
