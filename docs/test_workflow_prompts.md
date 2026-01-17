# Test Prompts for Chat Workflow

## 🎯 Workflow Overview

```
START → classify_intent → route_by_intent → [Agent] → END
                              ↓
              ┌───────────────┼──────────────┬──────────┐
              │               │              │          │
        conversation       payment         faq     escalation
```

---

## 📝 Test Cases by Intent

### 1. **GENERAL Intent** → ConversationAgent

**Prompts để test**:

```bash
# Greeting (English)
curl -X POST "http://localhost:8000/chat/" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, how are you?"}'

# Greeting (Vietnamese)
curl -X POST "http://localhost:8000/chat/" \
  -H "Content-Type: application/json" \
  -d '{"message": "Xin chào, bạn khoẻ không?"}'

# Casual conversation
curl -X POST "http://localhost:8000/chat/" \
  -H "Content-Type: application/json" \
  -d '{"message": "Tell me about yourself"}'

# Thank you
curl -X POST "http://localhost:8000/chat/" \
  -H "Content-Type: application/json" \
  -d '{"message": "Thank you for your help"}'

# Follow-up question
curl -X POST "http://localhost:8000/chat/" \
  -H "Content-Type: application/json" \
  -d '{"message": "Can you tell me more?"}'
```

**Expected**:
- Intent: `general`
- Route: → `conversation` node
- Response: Friendly conversation from ConversationAgent

---

### 2. **PAYMENT Intent** → PaymentAgent

**Prompts để test**:

```bash
# Simple payment request (English)
curl -X POST "http://localhost:8000/chat/" \
  -H "Content-Type: application/json" \
  -d '{"message": "I want to make a payment of 100 USD"}'

# Payment request (Vietnamese)
curl -X POST "http://localhost:8000/chat/" \
  -H "Content-Type: application/json" \
  -d '{"message": "Tôi muốn thanh toán 50000 VNĐ"}'

# Payment for company
curl -X POST "http://localhost:8000/chat/" \
  -H "Content-Type: application/json" \
  -d '{"message": "Create payment for company ABC, amount 200 USD"}'

# Payment with invoice
curl -X POST "http://localhost:8000/chat/" \
  -H "Content-Type: application/json" \
  -d '{"message": "Process payment for invoice #12345"}'

# Check transaction
curl -X POST "http://localhost:8000/chat/" \
  -H "Content-Type: application/json" \
  -d '{"message": "Check my payment transaction status"}'

# Payment with metadata
curl -X POST "http://localhost:8000/chat/" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I need to pay 150 EUR for order #789",
    "metadata": {
      "payment_data": {
        "amount": 150.0,
        "currency": "EUR",
        "description": "Order #789"
      }
    }
  }'
```

**Expected**:
- Intent: `payment`
- Route: → `payment` node
- Response: Payment processing from PaymentAgent
- Note: Nếu không có `payment_data` trong context, agent sẽ yêu cầu thêm thông tin

---

### 3. **FAQ Intent** → FAQAgent

**Prompts để test**:

```bash
# Business hours
curl -X POST "http://localhost:8000/chat/" \
  -H "Content-Type: application/json" \
  -d '{"message": "What are your business hours?"}'

# Service information
curl -X POST "http://localhost:8000/chat/" \
  -H "Content-Type: application/json" \
  -d '{"message": "How does your service work?"}'

# Pricing question
curl -X POST "http://localhost:8000/chat/" \
  -H "Content-Type: application/json" \
  -d '{"message": "What are your pricing plans?"}'

# Payment methods
curl -X POST "http://localhost:8000/chat/" \
  -H "Content-Type: application/json" \
  -d '{"message": "What payment methods do you accept?"}'

# Account question
curl -X POST "http://localhost:8000/chat/" \
  -H "Content-Type: application/json" \
  -d '{"message": "How do I create an account?"}'

# Vietnamese FAQ
curl -X POST "http://localhost:8000/chat/" \
  -H "Content-Type: application/json" \
  -d '{"message": "Dịch vụ của bạn là gì?"}'
```

**Expected**:
- Intent: `faq`
- Route: → `faq` node
- Response: Informative answer from FAQAgent

---

### 4. **ESCALATION Intent** → EscalationAgent

**Prompts để test**:

```bash
# Request human support
curl -X POST "http://localhost:8000/chat/" \
  -H "Content-Type: application/json" \
  -d '{"message": "I need to speak with a manager"}'

# Urgent issue
curl -X POST "http://localhost:8000/chat/" \
  -H "Content-Type: application/json" \
  -d '{"message": "This is urgent, I need help immediately"}'

# Complaint
curl -X POST "http://localhost:8000/chat/" \
  -H "Content-Type: application/json" \
  -d '{"message": "I am not satisfied with your service"}'

# Complex issue
curl -X POST "http://localhost:8000/chat/" \
  -H "Content-Type: application/json" \
  -d '{"message": "I have a complex problem that needs special attention"}'

# Request supervisor
curl -X POST "http://localhost:8000/chat/" \
  -H "Content-Type: application/json" \
  -d '{"message": "Can I talk to your supervisor?"}'
```

**Expected**:
- Intent: `escalation`
- Route: → `escalation` node
- Response: Empathetic response from EscalationAgent, setting expectations

---

## 🧪 Complete Test Script

**File**: [`scripts/test_all_flows.sh`](file:///Users/springhoan/DataWork/springme/projects/agentic-ai/langgraph-test/scripts/test_all_flows.sh)

```bash
#!/bin/bash

BASE_URL="http://localhost:8000"

echo "=========================================="
echo "Testing All Workflow Routes"
echo "=========================================="
echo ""

# Test 1: GENERAL → conversation
echo "1. Testing GENERAL Intent (Conversation)"
echo "----------------------------------------"
curl -X POST "$BASE_URL/chat/" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, how are you?"}' | jq
echo -e "\n"

# Test 2: PAYMENT → payment
echo "2. Testing PAYMENT Intent"
echo "----------------------------------------"
curl -X POST "$BASE_URL/chat/" \
  -H "Content-Type: application/json" \
  -d '{"message": "I want to make a payment of 100 USD"}' | jq
echo -e "\n"

# Test 3: FAQ → faq
echo "3. Testing FAQ Intent"
echo "----------------------------------------"
curl -X POST "$BASE_URL/chat/" \
  -H "Content-Type: application/json" \
  -d '{"message": "What are your business hours?"}' | jq
echo -e "\n"

# Test 4: ESCALATION → escalation
echo "4. Testing ESCALATION Intent"
echo "----------------------------------------"
curl -X POST "$BASE_URL/chat/" \
  -H "Content-Type: application/json" \
  -d '{"message": "I need to speak with a manager"}' | jq
echo -e "\n"

echo "=========================================="
echo "All tests completed!"
echo "=========================================="
```

---

## 📊 Monitor Workflow Execution

### Watch Logs in Real-time

```bash
# Terminal 1: Run server
make run

# Terminal 2: Watch logs
tail -f data/logs/chatbot.log | grep -E "Classifying intent|Routing based on intent|Processing"
```

**Expected log flow**:
```
INFO - Classifying intent...
INFO - Intent classification result: {"intent": "payment", ...}
INFO - Routing based on intent: IntentType.PAYMENT
INFO - Processing payment...
```

---

## 🎯 Verify Each Route

### Check Intent Classification

```bash
# Send message
curl -X POST "http://localhost:8000/chat/" \
  -H "Content-Type: application/json" \
  -d '{"message": "YOUR_TEST_MESSAGE"}' | jq '.intent'

# Should return: "general", "payment", "faq", or "escalation"
```

### Check Response Metadata

```bash
curl -X POST "http://localhost:8000/chat/" \
  -H "Content-Type: application/json" \
  -d '{"message": "I want to pay 100 USD"}' | jq '{
    intent: .intent,
    confidence: .metadata.intent_confidence,
    session_id: .session_id
  }'
```

---

## 🔍 Debug Specific Routes

### Test Payment Route with Context

```bash
curl -X POST "http://localhost:8000/chat/" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Process my payment",
    "metadata": {
      "payment_data": {
        "amount": 250.0,
        "currency": "USD",
        "description": "Test payment with context"
      }
    }
  }'
```

### Test Conversation with Session

```bash
# Message 1
curl -X POST "http://localhost:8000/chat/" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello"}' > response1.json

# Extract session_id
SESSION_ID=$(jq -r '.session_id' response1.json)

# Message 2 (same session)
curl -X POST "http://localhost:8000/chat/" \
  -H "Content-Type: application/json" \
  -d "{\"message\": \"Tell me more\", \"session_id\": \"$SESSION_ID\"}"
```

---

## 📈 Expected Results by Route

| Intent | Route | Agent | Expected Response |
|--------|-------|-------|-------------------|
| `general` | conversation | ConversationAgent | Friendly chat response |
| `payment` | payment | PaymentAgent | Payment processing or request for details |
| `faq` | faq | FAQAgent | Informative answer |
| `escalation` | escalation | EscalationAgent | Empathetic escalation message |

---

## 💡 Tips for Testing

1. **Start Simple**: Test one route at a time
2. **Check Logs**: Always monitor logs to see routing
3. **Verify Intent**: Check response metadata for intent classification
4. **Test Edge Cases**: Try ambiguous messages
5. **Use Session IDs**: Test conversation continuity

---

## 🚨 Common Issues

### Issue: All messages route to GENERAL
**Cause**: Model misclassifying intents
**Fix**: Use better model or improve prompts

### Issue: Payment route but no processing
**Cause**: Missing `payment_data` in context
**Fix**: Include payment details in metadata

### Issue: Different routes for same message
**Cause**: Model inconsistency
**Fix**: Use larger model with better consistency

---

## 🎬 Quick Start

```bash
# Make script executable
chmod +x scripts/test_all_flows.sh

# Run all tests
./scripts/test_all_flows.sh

# Or test individual routes
curl -X POST "http://localhost:8000/chat/" \
  -H "Content-Type: application/json" \
  -d '{"message": "YOUR_MESSAGE_HERE"}'
```
