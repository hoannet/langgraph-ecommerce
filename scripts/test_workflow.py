"""Test script for workflow."""

import asyncio
from langchain_core.messages import HumanMessage

from src.core.logging import setup_logging
from src.graphs.chat_workflow import get_chat_workflow
from src.services.llm_service import LLMService

# Setup logging
setup_logging()


async def test_chat_workflow():
    """Test the chat workflow."""
    print("=" * 60)
    print("Testing Chat Workflow")
    print("=" * 60)

    # Test LM Studio connection
    print("\n1. Testing LM Studio connection...")
    llm_service = LLMService()
    is_connected = await llm_service.test_connection()

    if not is_connected:
        print("❌ LM Studio is not running or not accessible")
        print("Please start LM Studio and load a model, then try again.")
        return

    print("✅ LM Studio connection successful")

    # Create workflow
    print("\n2. Creating chat workflow...")
    workflow = get_chat_workflow()
    print("✅ Workflow created")

    # Test cases
    test_messages = [
        "Hello, how are you?",
        "I want to make a payment of $100",
        "What are your business hours?",
        "I need help with a complex issue",
    ]

    for i, message in enumerate(test_messages, 1):
        print(f"\n{i}. Testing message: '{message}'")
        print("-" * 60)

        initial_state = {
            "messages": [HumanMessage(content=message)],
            "session_id": f"test_session_{i}",
            "context": {},
        }

        config = {"configurable": {"thread_id": f"test_thread_{i}"}}

        try:
            result = await workflow.ainvoke(initial_state, config=config)

            print(f"Intent: {result.get('intent')}")
            print(f"Confidence: {result.get('intent_confidence')}")
            print(f"Response: {result.get('final_response')}")
            print("✅ Test passed")

        except Exception as e:
            print(f"❌ Test failed: {e}")

    print("\n" + "=" * 60)
    print("Testing Complete")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_chat_workflow())
