# Metadata trong Chat Workflow - Hướng Dẫn Chi Tiết

## 📦 Metadata Là Gì?

`metadata` là một **dictionary tùy chọn** (`Dict[str, Any]`) cho phép bạn truyền **thông tin bổ sung** vào workflow mà không phải là phần của message chính.

### Định nghĩa trong Schema

```python
# src/models/schemas.py

class ChatRequest(BaseModel):
    message: str                                    # ← Message chính
    session_id: Optional[str] = None               # ← Session ID
    metadata: Dict[str, Any] = Field(default_factory=dict)  # ← Extra context
```

---

## 🔄 Metadata Flow trong Workflow

### 1. **Client gửi request**
```bash
curl -X POST "http://localhost:8000/chat/" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I need help",
    "metadata": {
      "user_id": "user123",
      "priority": "high",
      "department": "sales"
    }
  }'
```

### 2. **API nhận và chuyển vào context**
```python
# src/api/routes/chat.py (line 44)

initial_state = {
    "messages": [HumanMessage(content=request.message)],
    "session_id": session_id,
    "context": request.metadata,  # ← metadata → context
}
```

### 3. **Workflow sử dụng context**
```python
# src/state/graph_state.py

class ChatState(TypedDict, total=False):
    messages: List[BaseMessage]
    intent: Optional[IntentType]
    context: Dict[str, Any]  # ← metadata được lưu ở đây
    payment_data: Optional[Dict[str, Any]]
    session_id: str
```

### 4. **Agents truy cập context**
```python
# Trong agent.process()
async def process(
    self,
    messages: List[BaseMessage],
    context: Optional[Dict[str, Any]] = None,  # ← Nhận context
) -> str:
    # Access metadata
    user_id = context.get("user_id") if context else None
    priority = context.get("priority") if context else "normal"
    
    # Use in processing...
```

---

## 💡 Use Cases Thực Tế

### **1. User Information**
Truyền thông tin user để personalize response:

```bash
curl -X POST "http://localhost:8000/chat/" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello",
    "metadata": {
      "user_id": "user123",
      "user_name": "John Doe",
      "user_tier": "premium",
      "language": "vi"
    }
  }'
```

**Agent có thể**:
- Personalize greeting: "Xin chào John Doe"
- Provide premium features
- Respond in Vietnamese

---

### **2. Priority & Routing**
Đánh dấu urgent requests:

```bash
curl -X POST "http://localhost:8000/chat/" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I have an issue",
    "metadata": {
      "priority": "urgent",
      "department": "support",
      "ticket_id": "TKT-12345"
    }
  }'
```

**Agent có thể**:
- Route urgent requests to EscalationAgent
- Include ticket_id in response
- Notify support team

---

### **3. Payment Data** ⭐ (Quan trọng!)
Truyền payment details để PaymentAgent xử lý:

```bash
curl -X POST "http://localhost:8000/chat/" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Process my payment",
    "metadata": {
      "payment_data": {
        "amount": 150.0,
        "currency": "USD",
        "description": "Invoice #12345",
        "customer_id": "CUST-789"
      }
    }
  }'
```

**PaymentAgent sử dụng**:
```python
# src/agents/payment.py (line 45-50)

payment_data = (context or {}).get("payment_data", {})

if not payment_data:
    return "I need more information to process the payment..."

# Process with payment_data
payment_request = PaymentRequest(**payment_data)
```

---

### **4. Context & History**
Truyền conversation context:

```bash
curl -X POST "http://localhost:8000/chat/" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Tell me more",
    "metadata": {
      "previous_topic": "pricing",
      "page_url": "/pricing",
      "referrer": "google"
    }
  }'
```

**Agent có thể**:
- Continue conversation about pricing
- Provide relevant information based on page
- Track user journey

---

### **5. A/B Testing & Analytics**
Track experiments và user behavior:

```bash
curl -X POST "http://localhost:8000/chat/" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello",
    "metadata": {
      "experiment_id": "exp_123",
      "variant": "B",
      "session_start": "2026-01-16T14:00:00",
      "device": "mobile"
    }
  }'
```

---

## 🎯 Ví Dụ Thực Tế: Payment Flow

### **Scenario**: User muốn thanh toán nhưng không nói rõ số tiền

#### **Request 1**: Vague payment request
```bash
curl -X POST "http://localhost:8000/chat/" \
  -H "Content-Type: application/json" \
  -d '{"message": "I want to pay for my order"}'
```

**Response**: 
```json
{
  "message": "I need more information to process the payment. Please provide the amount and currency.",
  "intent": "payment"
}
```

#### **Request 2**: With payment_data in metadata
```bash
curl -X POST "http://localhost:8000/chat/" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Process payment for order #789",
    "metadata": {
      "payment_data": {
        "amount": 250.0,
        "currency": "USD",
        "description": "Order #789"
      }
    }
  }'
```

**Response**:
```json
{
  "message": "Payment of 250.0 USD processed successfully.\n\nStatus: completed\nTransaction ID: txn_xxx",
  "intent": "payment"
}
```

---

## 🔧 Implement Custom Metadata Handling

### **Example**: Priority-based routing

```python
# src/graphs/nodes.py

def route_by_intent(state: ChatState) -> str:
    """Route based on intent AND priority."""
    intent = state.get("intent", IntentType.GENERAL)
    context = state.get("context", {})
    priority = context.get("priority", "normal")
    
    # Urgent requests always go to escalation
    if priority == "urgent":
        logger.info("Routing to escalation due to urgent priority")
        return "escalation"
    
    # Normal routing
    if intent == IntentType.PAYMENT:
        return "payment"
    elif intent == IntentType.FAQ:
        return "faq"
    # ...
```

### **Example**: User-specific responses

```python
# src/agents/conversation.py

async def process(self, messages, context):
    user_name = context.get("user_name") if context else None
    language = context.get("language", "en") if context else "en"
    
    # Personalize prompt
    if user_name and language == "vi":
        greeting = f"Xin chào {user_name}!"
    elif user_name:
        greeting = f"Hello {user_name}!"
    else:
        greeting = "Hello!"
    
    # Include in response...
```

---

## 📊 Metadata vs Message

| Aspect | Message | Metadata |
|--------|---------|----------|
| **Purpose** | User's actual question/request | Extra context & data |
| **Visible to LLM** | ✅ Yes (in prompt) | ⚠️ Depends on implementation |
| **Required** | ✅ Yes | ❌ No (optional) |
| **Examples** | "I want to pay 100 USD" | `{"user_id": "123", "priority": "high"}` |
| **Use case** | Natural language input | Structured data, IDs, flags |

---

## 🎨 Best Practices

### ✅ **DO**
1. **Use for structured data**
   ```json
   {"payment_data": {"amount": 100, "currency": "USD"}}
   ```

2. **Use for IDs and references**
   ```json
   {"user_id": "123", "order_id": "ORD-456"}
   ```

3. **Use for flags and settings**
   ```json
   {"priority": "urgent", "language": "vi"}
   ```

4. **Keep it flat and simple**
   ```json
   {"user_id": "123", "tier": "premium"}
   ```

### ❌ **DON'T**
1. **Don't put natural language in metadata**
   ```json
   // BAD
   {"metadata": {"question": "What are your hours?"}}
   // Use message field instead
   ```

2. **Don't duplicate message content**
   ```json
   // BAD
   {"message": "Hello", "metadata": {"greeting": "Hello"}}
   ```

3. **Don't use for large data**
   ```json
   // BAD
   {"metadata": {"full_history": [...]}}  // Too large
   ```

---

## 🧪 Testing Metadata

```bash
# Test 1: Without metadata
curl -X POST "http://localhost:8000/chat/" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello"}'

# Test 2: With user metadata
curl -X POST "http://localhost:8000/chat/" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello",
    "metadata": {"user_id": "user123", "user_name": "John"}
  }'

# Test 3: With payment metadata
curl -X POST "http://localhost:8000/chat/" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Process payment",
    "metadata": {
      "payment_data": {
        "amount": 100.0,
        "currency": "USD"
      }
    }
  }'

# Check logs to see context usage
tail -f data/logs/chatbot.log | grep "context"
```

---

## 💡 Key Takeaways

1. **Metadata = Extra Context** - Không phải message, là data bổ sung
2. **Optional but Powerful** - Không bắt buộc nhưng rất hữu ích
3. **Flows to Context** - `metadata` → `context` trong state
4. **Agents Access It** - Tất cả agents có thể dùng context
5. **Use for Structured Data** - IDs, flags, payment data, user info
6. **Not for Natural Language** - Dùng message field cho text

---

## 🔗 Related Files

- Schema definition: [`src/models/schemas.py`](file:///springme/projects/agentic-ai/langgraph-test/src/models/schemas.py#L48-L53)
- API handling: [`src/api/routes/chat.py`](file:///springme/projects/agentic-ai/langgraph-test/src/api/routes/chat.py#L40-L45)
- State definition: [`src/state/graph_state.py`](file:///springme/projects/agentic-ai/langgraph-test/src/state/graph_state.py)
- Payment agent usage: [`src/agents/payment.py`](file:///springme/projects/agentic-ai/langgraph-test/src/agents/payment.py#L45-L50)
