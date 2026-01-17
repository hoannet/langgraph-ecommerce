#!/bin/bash

# LangGraph Chatbot API - cURL Examples
# Make sure the API server is running: make run

BASE_URL="http://localhost:8000"

echo "=========================================="
echo "LangGraph Chatbot API - cURL Examples"
echo "=========================================="
echo ""

# 1. Health Check
echo "1. Health Check"
echo "Command:"
echo "curl -X GET \"$BASE_URL/health\""
echo ""
curl -X GET "$BASE_URL/health"
echo -e "\n"

# 2. Simple Chat Message
echo "=========================================="
echo "2. Simple Chat Message (General)"
echo "Command:"
echo "curl -X POST \"$BASE_URL/chat/\" \\"
echo "  -H \"Content-Type: application/json\" \\"
echo "  -d '{\"message\": \"Hello, how are you?\"}'"
echo ""
curl -X POST "$BASE_URL/chat/" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, how are you?"}'
echo -e "\n"

# 3. Payment Intent Message
echo "=========================================="
echo "3. Payment Intent Message"
echo "Command:"
echo "curl -X POST \"$BASE_URL/chat/\" \\"
echo "  -H \"Content-Type: application/json\" \\"
echo "  -d '{\"message\": \"I want to make a payment of 100 USD\"}'"
echo ""
curl -X POST "$BASE_URL/chat/" \
  -H "Content-Type: application/json" \
  -d '{"message": "I want to make a payment of 100 USD"}'
echo -e "\n"

# 4. FAQ Intent Message
echo "=========================================="
echo "4. FAQ Intent Message"
echo "Command:"
echo "curl -X POST \"$BASE_URL/chat/\" \\"
echo "  -H \"Content-Type: application/json\" \\"
echo "  -d '{\"message\": \"What are your business hours?\"}'"
echo ""
curl -X POST "$BASE_URL/chat/" \
  -H "Content-Type: application/json" \
  -d '{"message": "What are your business hours?"}'
echo -e "\n"

# 5. Chat with Session ID
echo "=========================================="
echo "5. Chat with Session ID (for conversation continuity)"
echo "Command:"
echo "curl -X POST \"$BASE_URL/chat/\" \\"
echo "  -H \"Content-Type: application/json\" \\"
echo "  -d '{\"message\": \"Tell me more\", \"session_id\": \"session_123\"}'"
echo ""
curl -X POST "$BASE_URL/chat/" \
  -H "Content-Type: application/json" \
  -d '{"message": "Tell me more", "session_id": "session_123"}'
echo -e "\n"

# 6. Chat with Metadata
echo "=========================================="
echo "6. Chat with Metadata"
echo "Command:"
echo "curl -X POST \"$BASE_URL/chat/\" \\"
echo "  -H \"Content-Type: application/json\" \\"
echo "  -d '{\"message\": \"I need help\", \"metadata\": {\"user_id\": \"user123\", \"priority\": \"high\"}}'"
echo ""
curl -X POST "$BASE_URL/chat/" \
  -H "Content-Type: application/json" \
  -d '{"message": "I need help", "metadata": {"user_id": "user123", "priority": "high"}}'
echo -e "\n"

# 7. Process Payment
echo "=========================================="
echo "7. Process Payment"
echo "Command:"
echo "curl -X POST \"$BASE_URL/payment/process\" \\"
echo "  -H \"Content-Type: application/json\" \\"
echo "  -d '{\"amount\": 100.0, \"currency\": \"USD\", \"description\": \"Test payment\"}'"
echo ""
curl -X POST "$BASE_URL/payment/process" \
  -H "Content-Type: application/json" \
  -d '{"amount": 100.0, "currency": "USD", "description": "Test payment"}'
echo -e "\n"

# 8. Get Chat History
echo "=========================================="
echo "8. Get Chat History (replace session_123 with actual session_id)"
echo "Command:"
echo "curl -X GET \"$BASE_URL/chat/session_123/history\""
echo ""
echo "Note: Use the session_id from a previous chat response"
echo -e "\n"

# 9. Clear Chat History
echo "=========================================="
echo "9. Clear Chat History"
echo "Command:"
echo "curl -X POST \"$BASE_URL/chat/session_123/clear\""
echo ""
echo "Note: Use the session_id from a previous chat response"
echo -e "\n"

echo "=========================================="
echo "Examples completed!"
echo "=========================================="
