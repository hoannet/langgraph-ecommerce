# Nội Dung Chat Được Lưu Ở Đâu?

## 📍 3 Nơi Lưu Trữ Chat

### 1. **Memory (Runtime) - Trong RAM**

**Vị trí**: `SessionMemoryManager` trong code
**File**: [`src/memory/conversation.py`](file:///springme/projects/agentic-ai/langgraph-test/src/memory/conversation.py)

```python
# Lưu trong RAM, theo session_id
sessions = {
    "session_xxx": ConversationMemory(
        messages=[HumanMessage, AIMessage, ...]
    )
}
```

**Đặc điểm**:
- ✅ Nhanh, real-time
- ✅ Sliding window: max 20 messages (config: `MAX_CONVERSATION_HISTORY`)
- ❌ **Mất khi restart server**
- ✅ Theo `session_id`

**Xem chat history**:
```bash
curl -X GET "http://localhost:8000/chat/{session_id}/history"
```

---

### 2. **Checkpoints (Persistent) - File JSON**

**Vị trí**: [`data/checkpoints/`](file:///springme/projects/agentic-ai/langgraph-test/data/checkpoints/)

**Format file**: `{thread_id}_{checkpoint_id}.json`

```json
{
  "config": {
    "configurable": {
      "thread_id": "session_xxx"
    }
  },
  "checkpoint": {
    "messages": [
      {"type": "human", "content": "Hello"},
      {"type": "ai", "content": "Hi there!"}
    ],
    "intent": "general",
    "intent_confidence": 0.95,
    "session_id": "session_xxx",
    "context": {},
    "final_response": "Hi there!"
  },
  "metadata": {}
}
```

**Đặc điểm**:
- ✅ **Persistent** - không mất khi restart
- ✅ Lưu toàn bộ state của workflow
- ✅ Có thể resume conversation
- ⚠️ Hiện tại dùng `MemorySaver` (in-memory), chưa lưu file

**Để enable file checkpoints**, sửa trong [`src/graphs/chat_workflow.py`](file:///springme/projects/agentic-ai/langgraph-test/src/graphs/chat_workflow.py):

```python
from src.memory.checkpoints import FileCheckpointSaver

def get_chat_workflow(checkpointer=None):
    workflow = create_chat_workflow()
    
    # Thay vì MemorySaver
    if checkpointer is None:
        checkpointer = FileCheckpointSaver()  # ← Lưu vào file
    
    return workflow.compile(checkpointer=checkpointer)
```

---

### 3. **Logs - File Text**

**Vị trí**: [`data/logs/chatbot.log`](file:///springme/projects/agentic-ai/langgraph-test/data/logs/chatbot.log)

**Format**:
```
2026-01-16 14:04:42 - INFO - Received chat request: session_id=session_xxx
2026-01-16 14:04:42 - INFO - Intent classification result: {"intent": "payment", ...}
2026-01-16 14:04:42 - INFO - Routing based on intent: IntentType.PAYMENT
2026-01-16 14:04:42 - INFO - Processing payment...
```

**Đặc điểm**:
- ✅ Persistent - không mất
- ✅ Chi tiết workflow execution
- ✅ Debug-friendly
- ❌ Không structured, khó query

**Xem logs**:
```bash
# Xem real-time
tail -f data/logs/chatbot.log

# Tìm theo session
grep "session_xxx" data/logs/chatbot.log

# Xem intent classification
grep "Intent classification result" data/logs/chatbot.log
```

---

## 🔍 Cách Xem Chat History

### Qua API

```bash
# 1. Chat và lấy session_id
curl -X POST "http://localhost:8000/chat/" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello"}'

# Response:
# {
#   "session_id": "session_a4029c76-a8cb-461b-a148-179071b9f285",
#   ...
# }

# 2. Xem history của session đó
curl -X GET "http://localhost:8000/chat/session_a4029c76-a8cb-461b-a148-179071b9f285/history"

# Response:
# {
#   "session_id": "session_xxx",
#   "message_count": 5,
#   "messages": [
#     {"role": "human", "content": "Hello"},
#     {"role": "ai", "content": "Hi there!"},
#     ...
#   ]
# }
```

### Qua Code

```python
from src.memory.conversation import SessionMemoryManager

# Get session manager
manager = SessionMemoryManager()

# Get conversation memory for a session
memory = manager.get_session("session_xxx")

# Get messages
messages = memory.get_messages()
for msg in messages:
    print(f"{msg.type}: {msg.content}")

# Get summary
summary = memory.get_context_summary()
print(summary)
```

### Qua Logs

```bash
# Xem tất cả chat của một session
grep "session_0d4a8e0-017a-41a6-9617-91b942d9d667" data/logs/chatbot.log

# Xem intent classification
grep -A 5 "Intent classification result" data/logs/chatbot.log

# Xem payment processing
grep "Processing payment" data/logs/chatbot.log
```

---

## 📊 Ví Dụ Từ Logs Của Bạn

Từ logs, tôi thấy bạn đã test:

### Chat 1: Payment Intent (Tiếng Việt)
```
Message: "Tôi muốn tạo đơn thanh toán cho công ty CP ARS 50000 VNĐ"
Intent: payment (confidence: 0.95)
Routing: → PaymentAgent
```

### Chat 2: Payment Intent (English)
```
Message: "I want to make a payment of 100 USD"
Intent: payment (confidence: 0.95)
Routing: → PaymentAgent
```

### Chat 3: Misclassified
```
Message: "Bạn khoẻ không?" (How are you?)
Intent: payment (confidence: 0.95) ← WRONG!
Routing: → PaymentAgent ← Should be ConversationAgent
```

⚠️ **Vấn đề**: LLM đang classify sai "Bạn khoẻ không?" thành payment intent!

---

## 🔧 Config Chat Storage

### Trong `.env`:

```bash
# Memory settings
MAX_CONVERSATION_HISTORY=20          # Max messages to keep
CONVERSATION_SUMMARY_THRESHOLD=15    # When to summarize

# Paths
CHECKPOINT_DIR=./data/checkpoints
LOG_DIR=./data/logs
```

### Thay đổi storage:

**1. Enable File Checkpoints**:
```python
# src/graphs/chat_workflow.py
from src.memory.checkpoints import FileCheckpointSaver

checkpointer = FileCheckpointSaver()  # Lưu vào file
```

**2. Tăng history limit**:
```bash
# .env
MAX_CONVERSATION_HISTORY=50  # Giữ 50 messages thay vì 20
```

**3. Clear session**:
```bash
curl -X POST "http://localhost:8000/chat/{session_id}/clear"
```

---

## 💡 Best Practices

### 1. **Development**
- Dùng `MemorySaver` (in-memory) cho nhanh
- Check logs để debug: `tail -f data/logs/chatbot.log`

### 2. **Production**
- Dùng `FileCheckpointSaver` hoặc database
- Implement session cleanup (xóa old sessions)
- Add monitoring cho chat history size

### 3. **Testing**
- Dùng unique session_id cho mỗi test
- Clear session sau mỗi test
- Check logs để verify workflow

---

## 🎯 Quick Commands

```bash
# Xem logs real-time
tail -f data/logs/chatbot.log

# Tìm session
grep "session_xxx" data/logs/chatbot.log

# Xem checkpoints
ls -la data/checkpoints/

# Get chat history
curl http://localhost:8000/chat/{session_id}/history | jq

# Clear session
curl -X POST http://localhost:8000/chat/{session_id}/clear
```
