#!/usr/bin/env python3
"""Test script for payment workflow."""

import asyncio
from src.graphs.payment_workflow import get_payment_workflow
from src.models.enums import PaymentStatus
from src.core.logging import setup_logging

# Setup logging
setup_logging()


async def test_payment_workflow():
    """Test payment workflow with various scenarios."""
    print("=" * 60)
    print("Testing Payment Workflow")
    print("=" * 60)
    print()

    # Get workflow
    workflow = get_payment_workflow()

    # Test Case 1: Valid payment
    print("Test 1: Valid Payment")
    print("-" * 60)
    initial_state = {
        "transaction_id": "txn_test_001",
        "amount": 100.0,
        "currency": "USD",
        "description": "Test payment",
        "status": PaymentStatus.PENDING,
        "validation_errors": [],
    }

    try:
        result = await workflow.ainvoke(initial_state)
        print(f"✅ Transaction ID: {result.get('transaction_id')}")
        print(f"✅ Status: {result.get('status')}")
        print(f"✅ Amount: {result.get('amount')} {result.get('currency')}")
        print(f"✅ Errors: {result.get('validation_errors', [])}")
    except Exception as e:
        print(f"❌ Error: {e}")
    print()

    # Test Case 2: Invalid amount (negative)
    print("Test 2: Invalid Amount (Negative)")
    print("-" * 60)
    initial_state = {
        "transaction_id": "txn_test_002",
        "amount": -50.0,
        "currency": "USD",
        "description": "Invalid payment",
        "status": PaymentStatus.PENDING,
        "validation_errors": [],
    }

    try:
        result = await workflow.ainvoke(initial_state)
        print(f"Status: {result.get('status')}")
        print(f"Errors: {result.get('validation_errors', [])}")
        if result.get('status') == PaymentStatus.FAILED:
            print("✅ Correctly rejected invalid amount")
        else:
            print("❌ Should have rejected invalid amount")
    except Exception as e:
        print(f"❌ Error: {e}")
    print()

    # Test Case 3: Invalid amount (zero)
    print("Test 3: Invalid Amount (Zero)")
    print("-" * 60)
    initial_state = {
        "transaction_id": "txn_test_003",
        "amount": 0.0,
        "currency": "USD",
        "description": "Zero payment",
        "status": PaymentStatus.PENDING,
        "validation_errors": [],
    }

    try:
        result = await workflow.ainvoke(initial_state)
        print(f"Status: {result.get('status')}")
        print(f"Errors: {result.get('validation_errors', [])}")
        if result.get('status') == PaymentStatus.FAILED:
            print("✅ Correctly rejected zero amount")
        else:
            print("❌ Should have rejected zero amount")
    except Exception as e:
        print(f"❌ Error: {e}")
    print()

    # Test Case 4: Large amount
    print("Test 4: Large Amount")
    print("-" * 60)
    initial_state = {
        "transaction_id": "txn_test_004",
        "amount": 999999.99,
        "currency": "EUR",
        "description": "Large payment",
        "status": PaymentStatus.PENDING,
        "validation_errors": [],
    }

    try:
        result = await workflow.ainvoke(initial_state)
        print(f"✅ Transaction ID: {result.get('transaction_id')}")
        print(f"✅ Status: {result.get('status')}")
        print(f"✅ Amount: {result.get('amount')} {result.get('currency')}")
    except Exception as e:
        print(f"❌ Error: {e}")
    print()

    # Test Case 5: Different currencies
    print("Test 5: Different Currencies")
    print("-" * 60)
    currencies = ["USD", "EUR", "GBP", "JPY", "VND"]
    for currency in currencies:
        initial_state = {
            "transaction_id": f"txn_test_{currency}",
            "amount": 100.0,
            "currency": currency,
            "description": f"Payment in {currency}",
            "status": PaymentStatus.PENDING,
            "validation_errors": [],
        }

        try:
            result = await workflow.ainvoke(initial_state)
            print(f"✅ {currency}: {result.get('status')}")
        except Exception as e:
            print(f"❌ {currency}: {e}")
    print()

    print("=" * 60)
    print("Testing Complete")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_payment_workflow())
