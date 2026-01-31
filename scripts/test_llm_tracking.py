#!/usr/bin/env python3
"""Test script for LLM call tracking."""

import asyncio
from src.services.llm_service import LLMService, get_llm_stats, reset_llm_stats
from src.core.logging import setup_logging

setup_logging()


async def test_llm_tracking():
    """Test LLM call tracking."""
    print("🧪 Testing LLM Call Tracking\n")
    print("=" * 60)
    
    # Reset stats
    reset_llm_stats()
    
    # Test 1: Create LLM service
    print("\n📝 Test 1: Creating LLM Service")
    print("-" * 60)
    llm_service = LLMService()
    print(f"✅ Provider: {llm_service.provider}")
    print(f"✅ Model: {llm_service.model_name}")
    
    # Test 2: Make tracked calls
    print("\n📝 Test 2: Making Tracked LLM Calls")
    print("-" * 60)
    
    for i in range(3):
        print(f"\nCall {i+1}:")
        response = await llm_service.ainvoke_tracked("Say hello in 5 words")
        print(f"Response: {response.content[:50]}...")
    
    # Test 3: Check instance stats
    print("\n📝 Test 3: Instance Statistics")
    print("-" * 60)
    stats = llm_service.get_stats()
    print(f"Provider: {stats['provider']}")
    print(f"Model: {stats['model']}")
    print(f"Calls: {stats['call_count']}")
    print(f"Tokens: {stats['total_tokens']}")
    
    # Test 4: Check global stats
    print("\n📝 Test 4: Global Statistics")
    print("-" * 60)
    global_stats = get_llm_stats()
    print(f"Total Calls: {global_stats['total_calls']}")
    print(f"Total Tokens: {global_stats['total_tokens']}")
    
    # Test 5: Multiple instances
    print("\n📝 Test 5: Multiple LLM Instances")
    print("-" * 60)
    llm_service2 = LLMService()
    await llm_service2.ainvoke_tracked("Count to 3")
    
    print(f"\nInstance 1 calls: {llm_service.call_count}")
    print(f"Instance 2 calls: {llm_service2.call_count}")
    print(f"Global calls: {get_llm_stats()['total_calls']}")
    
    print("\n" + "=" * 60)
    print("✅ All tests completed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_llm_tracking())
