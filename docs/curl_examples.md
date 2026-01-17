# cURL Examples for LangGraph Chatbot API

## Quick Reference

### 1. Simple Chat
```bash
curl -X POST "http://localhost:8000/chat/" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, how are you?"}'
```

### 2. Chat with Payment Intent
```bash
curl -X POST "http://localhost:8000/chat/" \
  -H "Content-Type: application/json" \
  -d '{"message": "I want to make a payment of 100 USD"}'
```

### 3. Chat with Session ID (for continuity)
```bash
curl -X POST "http://localhost:8000/chat/" \
  -H "Content-Type: application/json" \
  -d '{"message": "Tell me more", "session_id": "session_123"}'
```

### 4. Vietnamese Message Example
```bash
curl -X POST "http://localhost:8000/chat/" \
  -H "Content-Type: application/json" \
  -d '{"message": "Tôi muốn tạo đơn thanh toán cho công ty CP ARS"}'
```

### 5. FAQ Question
```bash
curl -X POST "http://localhost:8000/chat/" \
  -H "Content-Type: application/json" \
  -d '{"message": "What are your business hours?"}'
```

### 6. Process Payment Directly
```bash
curl -X POST "http://localhost:8000/payment/process" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 100.0,
    "currency": "USD",
    "description": "Test payment"
  }'
```

### 7. Get Chat History
```bash
# Replace session_xxx with actual session_id from chat response
curl -X GET "http://localhost:8000/chat/session_xxx/history"
```

### 8. Clear Chat History
```bash
curl -X POST "http://localhost:8000/chat/session_xxx/clear"
```

### 9. Health Check
```bash
curl -X GET "http://localhost:8000/health"
```

## Using the Script

Run all examples at once:
```bash
./scripts/curl_examples.sh
```

## Expected Response Format

### Chat Response
```json
{
  "message": "Response from the chatbot",
  "session_id": "session_a4029c76-a8cb-461b-a148-179071b9f285",
  "intent": "GENERAL",
  "timestamp": "2026-01-16T13:45:00",
  "metadata": {
    "intent_confidence": 0.95
  }
}
```

### Payment Response
```json
{
  "transaction_id": "txn_12345678-1234-1234-1234-123456789abc",
  "status": "completed",
  "amount": 100.0,
  "currency": "USD",
  "message": "Payment of 100.0 USD processed successfully...",
  "timestamp": "2026-01-16T13:45:00"
}
```

## Troubleshooting

### Issue: Connection refused
**Solution**: Make sure the API server is running
```bash
make run
# or
uvicorn src.api.main:app --reload
```

### Issue: LM Studio not responding
**Solution**: 
1. Check LM Studio is running
2. Verify model is loaded
3. Check the base URL in `.env` file
4. Test connection: `python scripts/test_workflow.py`

### Issue: Intent classification errors (FIXED)
**Solution**: Updated `intent_classifier.py` to handle markdown code blocks from LLM responses

## Pretty Print JSON Response

Add `| jq` to format JSON output:
```bash
curl -X POST "http://localhost:8000/chat/" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello"}' | jq
```

## Save Response to File
```bash
curl -X POST "http://localhost:8000/chat/" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello"}' > response.json
```
