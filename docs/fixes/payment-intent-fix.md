# Intent Classification Fix - Payment Recognition

## ❌ Vấn đề
"Pay now" bị classify thành `general` 50% thay vì `payment`

## ✅ Đã sửa

### Thay đổi trong `src/prompts/agent_prompts.py`:

**Trước:**
```python
Available intents:
1. product_search - ...
2. order - ...
3. payment - User wants to pay ("I want to pay $50", "Process payment")
...
CRITICAL RULES:
- Only use "payment" if explicitly mentions paying money
```

**Sau:**
```python
Available intents (in priority order):

1. payment - User wants to make a payment or pay money
   Keywords: "pay", "payment", "pay now", "I want to pay", "charge", "process payment"
   Examples: "Pay now", "I want to pay", "Process payment", "I want to pay $50"

2. product_search - ...
3. order - ...
...
CRITICAL RULES:
- "Pay", "Pay now", "I want to pay" = payment (HIGHEST PRIORITY!)
- When in doubt between payment and general, choose payment if ANY payment keyword exists
```

## 🔑 Key Changes

1. **Payment ở vị trí #1** (highest priority)
2. **Explicit keywords**: "pay", "pay now", "I want to pay"
3. **Clear examples**: "Pay now", "I want to pay"
4. **Priority rule**: Khi có bất kỳ payment keyword nào → chọn payment

## ✅ Test Cases

| Input | Expected | Confidence |
|-------|----------|------------|
| "Pay now" | payment | >90% |
| "I want to pay" | payment | >90% |
| "Process payment" | payment | >90% |
| "Show me laptops" | product_search | >90% |
| "I want product prod_001" | order | >90% |

## 🚀 Restart Backend

```bash
# Ctrl+C backend hiện tại
make run
```

Sau khi restart, "Pay now" sẽ được classify đúng thành `payment`!
