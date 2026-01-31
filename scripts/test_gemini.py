#!/usr/bin/env python3
"""Test script for Gemini integration."""

import asyncio
import sys
from src.services.llm_service import LLMService
from src.core.logging import setup_logging

setup_logging()


async def test_gemini():
    """Test Gemini API integration."""
    print("=" * 60)
    print("Testing Gemini Integration")
    print("=" * 60)
    print()

    try:
        # Test 1: Create Gemini service
        print("Test 1: Creating Gemini LLM Service")
        print("-" * 60)
        llm_service = LLMService(provider="gemini")
        print(f"✅ Provider: {llm_service.provider}")
        print(f"✅ Model: {llm_service.model_name}")
        print(f"✅ Temperature: {llm_service.temperature}")
        print()

        # Test 2: Test connection
        print("Test 2: Testing Connection")
        print("-" * 60)
        is_connected = await llm_service.test_connection()
        if is_connected:
            print("✅ Gemini connection successful")
        else:
            print("❌ Gemini connection failed")
            return
        print()

        # Test 3: Simple query
        print("Test 3: Simple Query")
        print("-" * 60)
        response = await llm_service.llm.ainvoke("What is 2+2? Answer briefly.")
        print(f"Query: What is 2+2?")
        print(f"Response: {response.content}")
        print()

        # Test 4: Chat-style interaction
        print("Test 4: Chat Interaction")
        print("-" * 60)
        from langchain_core.messages import HumanMessage, SystemMessage

        messages = [
            SystemMessage(content="You are a helpful assistant."),
            HumanMessage(content="Tell me a very short joke about programming."),
        ]
        response = await llm_service.llm.ainvoke(messages)
        print(f"Response: {response.content}")
        print()

        # Test 5: Intent classification (real use case)
        print("Test 5: Intent Classification")
        print("-" * 60)
        messages = [
            SystemMessage(content="Classify the intent as: payment, faq, general, or escalation"),
            HumanMessage(content="I want to make a payment of 100 USD"),
        ]
        response = await llm_service.llm.ainvoke(messages)
        print(f"Message: I want to make a payment of 100 USD")
        print(f"Classification: {response.content}")
        print()

        print("=" * 60)
        print("✅ All Gemini tests passed!")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Check GEMINI_API_KEY in .env file")
        print("2. Verify API key at: https://makersuite.google.com/app/apikey")
        print("3. Install: pip install langchain-google-genai")
        sys.exit(1)


async def compare_providers():
    """Compare LM Studio and Gemini."""
    print("\n" + "=" * 60)
    print("Comparing LM Studio vs Gemini")
    print("=" * 60)
    print()

    # Test LM Studio
    print("Testing LM Studio...")
    try:
        llm_local = LLMService(provider="lm_studio")
        local_ok = await llm_local.test_connection()
        print(f"LM Studio: {'✅ Connected' if local_ok else '❌ Not available'}")
    except Exception as e:
        print(f"LM Studio: ❌ Error - {e}")

    # Test Gemini
    print("\nTesting Gemini...")
    try:
        llm_gemini = LLMService(provider="gemini")
        gemini_ok = await llm_gemini.test_connection()
        print(f"Gemini: {'✅ Connected' if gemini_ok else '❌ Not available'}")
    except Exception as e:
        print(f"Gemini: ❌ Error - {e}")

    print()


if __name__ == "__main__":
    print("\n🚀 Starting Gemini Integration Tests\n")
    
    # Run main tests
    asyncio.run(test_gemini())
    
    # Compare providers
    asyncio.run(compare_providers())
    
    print("\n✨ Testing complete!\n")
