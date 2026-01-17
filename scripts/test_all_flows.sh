#!/bin/bash

# Test All Workflow Routes
# Make sure server is running: make run

BASE_URL="http://localhost:8000"

echo "=========================================="
echo "Testing All Workflow Routes"
echo "=========================================="
echo ""

# Test 1: GENERAL → conversation
echo "1️⃣  Testing GENERAL Intent → ConversationAgent"
echo "Message: 'Hello, how are you?'"
echo "----------------------------------------"
curl -s -X POST "$BASE_URL/chat/" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, how are you?"}' | jq '{intent: .intent, confidence: .metadata.intent_confidence, message: .message}'
echo -e "\n"
sleep 2

# Test 2: PAYMENT → payment
echo "2️⃣  Testing PAYMENT Intent → PaymentAgent"
echo "Message: 'I want to make a payment of 100 USD'"
echo "----------------------------------------"
curl -s -X POST "$BASE_URL/chat/" \
  -H "Content-Type: application/json" \
  -d '{"message": "I want to make a payment of 100 USD"}' | jq '{intent: .intent, confidence: .metadata.intent_confidence, message: .message}'
echo -e "\n"
sleep 2

# Test 3: FAQ → faq
echo "3️⃣  Testing FAQ Intent → FAQAgent"
echo "Message: 'What are your business hours?'"
echo "----------------------------------------"
curl -s -X POST "$BASE_URL/chat/" \
  -H "Content-Type: application/json" \
  -d '{"message": "What are your business hours?"}' | jq '{intent: .intent, confidence: .metadata.intent_confidence, message: .message}'
echo -e "\n"
sleep 2

# Test 4: ESCALATION → escalation
echo "4️⃣  Testing ESCALATION Intent → EscalationAgent"
echo "Message: 'I need to speak with a manager'"
echo "----------------------------------------"
curl -s -X POST "$BASE_URL/chat/" \
  -H "Content-Type: application/json" \
  -d '{"message": "I need to speak with a manager"}' | jq '{intent: .intent, confidence: .metadata.intent_confidence, message: .message}'
echo -e "\n"
sleep 2

# Test 5: Vietnamese GENERAL
echo "5️⃣  Testing Vietnamese GENERAL"
echo "Message: 'Bạn khoẻ không?'"
echo "----------------------------------------"
curl -s -X POST "$BASE_URL/chat/" \
  -H "Content-Type: application/json" \
  -d '{"message": "Bạn khoẻ không?"}' | jq '{intent: .intent, confidence: .metadata.intent_confidence, message: .message}'
echo -e "\n"
sleep 2

# Test 6: Vietnamese PAYMENT
echo "6️⃣  Testing Vietnamese PAYMENT"
echo "Message: 'Tôi muốn thanh toán 50000 VNĐ'"
echo "----------------------------------------"
curl -s -X POST "$BASE_URL/chat/" \
  -H "Content-Type: application/json" \
  -d '{"message": "Tôi muốn thanh toán 50000 VNĐ"}' | jq '{intent: .intent, confidence: .metadata.intent_confidence, message: .message}'
echo -e "\n"

echo "=========================================="
echo "✅ All workflow routes tested!"
echo "=========================================="
echo ""
echo "Check logs for detailed routing:"
echo "  tail -f data/logs/chatbot.log | grep -E 'Routing|Processing'"
