# Intent Classification Errors - Troubleshooting Guide

## ❌ Lỗi Phổ Biến: Misclassification

### Ví Dụ Từ Logs

```
User Message: "Bạn khoẻ không?" (How are you?)
Expected Intent: general
Actual Intent: payment ✗
Confidence: 0.95
Reasoning: "The message explicitly asks about payment" ← HALLUCINATION!
```

---

## 🔍 Nguyên Nhân

### 1. **Small Language Model Limitations**

Model hiện tại: `google/gemma-3-1b` (1 billion parameters)

**Vấn đề**:
- ❌ **Limited understanding** - Model nhỏ khó hiểu context phức tạp
- ❌ **Hallucination** - Tạo ra reasoning không đúng sự thật
- ❌ **Overconfidence** - Confidence cao (0.95) dù classify sai
- ❌ **Language confusion** - Khó với tiếng Việt và mixed languages

### 2. **Prompt Không Đủ Rõ Ràng**

**Trước khi fix**:
```
Intent categories:
- PAYMENT: User wants to make a payment...
- GENERAL: General conversation, greetings...
```

**Vấn đề**: Không có examples cụ thể → model dễ nhầm lẫn

---

## ✅ Giải Pháp

### **Solution 1: Cải Thiện Prompt** ⭐ (IMPLEMENTED)

**Đã fix trong**: [`src/prompts/system_prompts.py`](file:///projects/agentic-ai/langgraph-test/src/prompts/system_prompts.py)

**Thay đổi**:
1. ✅ Thêm **concrete examples** cho mỗi intent
2. ✅ Thêm **IMPORTANT RULES** section
3. ✅ Explicit instruction: "Only classify as PAYMENT if explicitly mentions payment"
4. ✅ Include Vietnamese examples: "Bạn khoẻ không?" → GENERAL

**New Prompt**:
```python
Intent categories with examples:

1. PAYMENT - User wants to make a payment...
   Examples:
   - "I want to make a payment of $100"
   - "Tôi muốn thanh toán 50000 VNĐ"
   
3. GENERAL - General conversation, greetings...
   Examples:
   - "Hello, how are you?"
   - "Bạn khoẻ không?"  ← Explicit example!

IMPORTANT RULES:
- Only classify as PAYMENT if explicitly mentions payment
- Greetings should be GENERAL, not PAYMENT
- Be conservative - when in doubt, choose GENERAL
```

**Expected Improvement**: 60-80% better accuracy

---

### **Solution 2: Use Larger Model** 🚀 (RECOMMENDED)

**Current**: `google/gemma-3-1b` (1B params)

**Better Options**:

#### Option A: Gemma 2 (7B-9B)
```bash
# In LM Studio, load:
- google/gemma-2-9b-it
- google/gemma-2-7b-it
```

**Pros**:
- ✅ Much better understanding
- ✅ Less hallucination
- ✅ Better multilingual support

**Cons**:
- ⚠️ Requires more RAM (8-16GB)
- ⚠️ Slower inference

#### Option B: Llama 3.1 (8B)
```bash
# In LM Studio, load:
- meta-llama/Llama-3.1-8B-Instruct
```

**Pros**:
- ✅ Excellent instruction following
- ✅ Very good at classification tasks
- ✅ Strong reasoning

#### Option C: Qwen 2.5 (7B)
```bash
# In LM Studio, load:
- Qwen/Qwen2.5-7B-Instruct
```

**Pros**:
- ✅ Great multilingual (English + Vietnamese)
- ✅ Fast inference
- ✅ Good at structured output

**Cách đổi model**:
```bash
# 1. Load model mới trong LM Studio
# 2. Update .env
LM_STUDIO_MODEL_NAME=Qwen/Qwen2.5-7B-Instruct

# 3. Restart server (auto-reload sẽ pick up changes)
```

---

### **Solution 3: Add Fallback Logic** 🛡️

Thêm validation layer để catch obvious mistakes:

```python
# src/agents/intent_classifier.py

def _validate_classification(
    self, 
    message: str, 
    intent: IntentType, 
    confidence: float
) -> tuple[IntentType, float]:
    """Validate and correct obvious misclassifications."""
    
    # Greetings should be GENERAL
    greetings = [
        "hello", "hi", "hey", "good morning", "good afternoon",
        "xin chào", "chào", "bạn khoẻ không", "how are you"
    ]
    
    message_lower = message.lower()
    
    # If classified as PAYMENT but is a greeting
    if intent == IntentType.PAYMENT:
        for greeting in greetings:
            if greeting in message_lower:
                logger.warning(
                    f"Correcting misclassification: '{message}' "
                    f"from PAYMENT to GENERAL (greeting detected)"
                )
                return IntentType.GENERAL, 0.6
    
    # If PAYMENT but no payment keywords
    payment_keywords = [
        "payment", "pay", "transaction", "thanh toán", 
        "đơn", "invoice", "bill", "charge"
    ]
    
    if intent == IntentType.PAYMENT:
        has_payment_keyword = any(
            keyword in message_lower 
            for keyword in payment_keywords
        )
        if not has_payment_keyword:
            logger.warning(
                f"Correcting misclassification: '{message}' "
                f"from PAYMENT to GENERAL (no payment keywords)"
            )
            return IntentType.GENERAL, 0.5
    
    return intent, confidence
```

**Usage**:
```python
async def classify(self, messages, context):
    # ... existing code ...
    result_dict = json.loads(cleaned_json)
    
    # Validate classification
    intent, confidence = self._validate_classification(
        messages[-1].content,
        IntentType(result_dict["intent"]),
        result_dict["confidence"]
    )
    
    return IntentClassification(
        intent=intent,
        confidence=confidence,
        reasoning=result_dict.get("reasoning")
    )
```

---

### **Solution 4: Few-Shot Examples in Prompt**

Thêm examples trực tiếp vào prompt:

```python
# src/prompts/agent_prompts.py

INTENT_CLASSIFICATION_PROMPT = ChatPromptTemplate.from_messages([
    ("system", "{system_prompt}"),
    # Add few-shot examples
    ("human", "I want to make a payment of $100"),
    ("assistant", '{"intent": "payment", "confidence": 0.95, "reasoning": "Explicit payment request"}'),
    ("human", "Bạn khoẻ không?"),
    ("assistant", '{"intent": "general", "confidence": 0.95, "reasoning": "Greeting in Vietnamese"}'),
    ("human", "What are your business hours?"),
    ("assistant", '{"intent": "faq", "confidence": 0.90, "reasoning": "Question about service"}'),
    # Actual user message
    MessagesPlaceholder(variable_name="chat_history", optional=True),
    ("human", "Analyze this: {user_message}"),
])
```

---

## 📊 Testing After Fixes

### Test Cases

```bash
# 1. Greeting (should be GENERAL)
curl -X POST "http://localhost:8000/chat/" \
  -H "Content-Type: application/json" \
  -d '{"message": "Bạn khoẻ không?"}'

# Expected: intent="general"

# 2. Payment (should be PAYMENT)
curl -X POST "http://localhost:8000/chat/" \
  -H "Content-Type: application/json" \
  -d '{"message": "Tôi muốn thanh toán 100 USD"}'

# Expected: intent="payment"

# 3. FAQ (should be FAQ)
curl -X POST "http://localhost:8000/chat/" \
  -H "Content-Type: application/json" \
  -d '{"message": "What are your business hours?"}'

# Expected: intent="faq"

# 4. Ambiguous (should be GENERAL with lower confidence)
curl -X POST "http://localhost:8000/chat/" \
  -H "Content-Type: application/json" \
  -d '{"message": "Tell me more"}'

# Expected: intent="general", confidence < 0.7
```

### Monitor Logs

```bash
# Watch classification results
tail -f data/logs/chatbot.log | grep "Intent classification result"

# Check for corrections
tail -f data/logs/chatbot.log | grep "Correcting misclassification"
```

---

## 🎯 Recommended Action Plan

### Immediate (Now)
1. ✅ **Improved prompt** (already done)
2. 🔄 **Test with current model** - see if prompt helps
3. 📊 **Monitor accuracy** - check logs

### Short-term (Today/Tomorrow)
1. 🚀 **Upgrade to 7B model** (Qwen 2.5 or Gemma 2)
   - Better accuracy
   - Still reasonable speed
2. 🛡️ **Add fallback validation** (Solution 3)
   - Catch obvious mistakes
   - Log corrections for analysis

### Long-term (Production)
1. 📈 **Collect misclassification data**
2. 🎓 **Fine-tune model** on your specific use cases
3. 🔍 **Add confidence thresholds**
   - If confidence < 0.7 → ask user to clarify
4. 📊 **A/B testing** different models and prompts

---

## 🔧 Quick Fix Commands

```bash
# 1. Test current fix (improved prompt)
curl -X POST "http://localhost:8000/chat/" \
  -H "Content-Type: application/json" \
  -d '{"message": "Bạn khoẻ không?"}'

# 2. Change to better model in LM Studio
# Load: Qwen/Qwen2.5-7B-Instruct

# 3. Update .env
echo "LM_STUDIO_MODEL_NAME=Qwen/Qwen2.5-7B-Instruct" >> .env

# 4. Server auto-reloads, test again
curl -X POST "http://localhost:8000/chat/" \
  -H "Content-Type: application/json" \
  -d '{"message": "Bạn khoẻ không?"}'
```

---

## 📈 Expected Results

### With Improved Prompt (Current)
- Accuracy: 70-80% (up from ~50%)
- Still some errors with small model

### With 7B Model + Improved Prompt
- Accuracy: 90-95%
- Rare misclassifications
- Better confidence calibration

### With Fallback Validation
- Accuracy: 95-98%
- Catches most obvious mistakes
- More robust system

---

## 💡 Key Takeaways

1. **Small models struggle** - 1B params not enough for reliable classification
2. **Prompts matter** - Good examples and rules help significantly
3. **Validation helps** - Rule-based fallback catches obvious errors
4. **Model size vs speed** - Trade-off between accuracy and latency
5. **Monitor and iterate** - Collect data, improve over time
