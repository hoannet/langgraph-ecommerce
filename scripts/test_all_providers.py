#!/usr/bin/env python3
"""Test script for all LLM providers."""

import asyncio
import sys
from src.services.llm_service import LLMService
from src.core.logging import setup_logging

setup_logging()


async def test_provider(provider_name: str):
    """Test a specific provider."""
    print(f"\n{'='*60}")
    print(f"Testing {provider_name.upper()}")
    print('='*60)
    
    try:
        # Create service
        print(f"\n1. Creating {provider_name} LLM Service...")
        llm_service = LLMService(provider=provider_name)
        print(f"   ✅ Provider: {llm_service.provider}")
        print(f"   ✅ Model: {llm_service.model_name}")
        print(f"   ✅ Temperature: {llm_service.temperature}")
        
        # Test connection
        print(f"\n2. Testing Connection...")
        is_connected = await llm_service.test_connection()
        if not is_connected:
            print(f"   ❌ Connection failed")
            return False
        print(f"   ✅ Connection successful")
        
        # Simple query
        print(f"\n3. Simple Query...")
        response = await llm_service.llm.ainvoke("What is 2+2? Answer with just the number.")
        print(f"   Query: What is 2+2?")
        print(f"   Response: {response.content}")
        
        # Intent classification
        print(f"\n4. Intent Classification Test...")
        from langchain_core.messages import HumanMessage, SystemMessage
        
        messages = [
            SystemMessage(content="Classify intent as: payment, faq, general, or escalation. Respond with just the intent."),
            HumanMessage(content="I want to make a payment of 100 USD"),
        ]
        response = await llm_service.llm.ainvoke(messages)
        print(f"   Message: I want to make a payment of 100 USD")
        print(f"   Classification: {response.content}")
        
        print(f"\n✅ All {provider_name} tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False


async def compare_all_providers():
    """Compare all providers."""
    print("\n" + "="*60)
    print("COMPARING ALL PROVIDERS")
    print("="*60)
    
    providers = {
        "lm_studio": "LM Studio (Local)",
        "gemini": "Google Gemini",
        "openai": "OpenAI"
    }
    
    results = {}
    
    for provider, name in providers.items():
        print(f"\nTesting {name}...")
        try:
            llm = LLMService(provider=provider)
            success = await llm.test_connection()
            results[provider] = "✅ Available" if success else "❌ Failed"
        except Exception as e:
            results[provider] = f"❌ Error: {str(e)[:50]}"
    
    print("\n" + "="*60)
    print("RESULTS SUMMARY")
    print("="*60)
    for provider, name in providers.items():
        print(f"{name:25} {results[provider]}")
    print("="*60)


async def main():
    """Main test function."""
    print("\n🚀 LLM Provider Testing Suite\n")
    
    # Test each provider
    providers_to_test = []
    
    # Check which providers to test
    import sys
    if len(sys.argv) > 1:
        # Test specific provider
        providers_to_test = [sys.argv[1]]
    else:
        # Test all
        providers_to_test = ["lm_studio", "gemini", "openai"]
    
    for provider in providers_to_test:
        await test_provider(provider)
    
    # Compare all
    if len(providers_to_test) > 1:
        await compare_all_providers()
    
    print("\n✨ Testing complete!\n")


if __name__ == "__main__":
    print("""
Usage:
  python scripts/test_all_providers.py           # Test all providers
  python scripts/test_all_providers.py openai    # Test OpenAI only
  python scripts/test_all_providers.py gemini    # Test Gemini only
  python scripts/test_all_providers.py lm_studio # Test LM Studio only
    """)
    
    asyncio.run(main())
