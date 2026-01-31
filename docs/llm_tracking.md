# LLM Call Tracking Guide

## 🎯 Overview

Hệ thống tracking tự động đếm và log mọi LLM API call để monitor usage và cost.

## 📊 Features

- ✅ **Global Counter** - Đếm tất cả calls across all instances
- ✅ **Instance Counter** - Đếm calls per LLM service instance  
- ✅ **Token Tracking** - Track prompt, completion, và total tokens
- ✅ **Time Tracking** - Measure response time cho mỗi call
- ✅ **Detailed Logging** - Log provider, model, tokens, time

## 🔧 Usage

### 1. Use Tracked Methods

```python
from src.services.llm_service import LLMService

llm_service = LLMService()

# Use ainvoke_tracked instead of llm.ainvoke
response = await llm_service.ainvoke_tracked("Your prompt here")
```

### 2. Get Statistics

```python
from src.services.llm_service import get_llm_stats

# Get global stats
stats = get_llm_stats()
print(f"Total calls: {stats['total_calls']}")
print(f"Total tokens: {stats['total_tokens']}")

# Get instance stats
instance_stats = llm_service.get_stats()
print(f"Instance calls: {instance_stats['call_count']}")
```

### 3. Reset Stats

```python
from src.services.llm_service import reset_llm_stats

# Reset global counters
reset_llm_stats()
```

## 📝 Log Output Example

```
INFO - LLM Call #1 (Global: #1) | Provider: gemini | Model: gemini-pro | Time: 1.23s
INFO - Tokens - Prompt: 45, Completion: 120, Total: 165
INFO - LLM Call #2 (Global: #2) | Provider: gemini | Model: gemini-pro | Time: 0.89s
INFO - Tokens - Prompt: 32, Completion: 98, Total: 130
```

## 🧪 Testing

```bash
# Run test script
python scripts/test_llm_tracking.py
```

## 🔄 Migration Guide

### Before (Direct LLM call):
```python
response = await self.llm.ainvoke(prompt)
```

### After (Tracked call):
```python
response = await self.llm_service.ainvoke_tracked(prompt)
```

## 📊 Monitoring Dashboard

Bạn có thể tạo endpoint để xem stats:

```python
# In src/api/routes/admin.py
@router.get("/llm-stats")
async def get_llm_statistics():
    from src.services.llm_service import get_llm_stats
    return get_llm_stats()
```

## 💡 Best Practices

1. **Always use tracked methods** khi gọi LLM
2. **Reset stats** khi bắt đầu session mới
3. **Monitor logs** để detect unusual patterns
4. **Track costs** based on token usage

## 🎯 Next Steps

- [ ] Add cost calculation based on provider pricing
- [ ] Create monitoring dashboard
- [ ] Add alerts for high usage
- [ ] Export stats to metrics system
