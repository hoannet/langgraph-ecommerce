# Multi-Provider LLM Guide

## 🎯 Overview

Hệ thống hỗ trợ **3 LLM providers**:
1. **LM Studio** - Local LLM (privacy, free, offline)
2. **Google Gemini** - Cloud API (powerful, affordable)
3. **OpenAI** - Cloud API (GPT-4, GPT-3.5, industry standard)

## 🔧 Quick Setup

### **1. LM Studio** (Default - Local)

```bash
# .env
LLM_PROVIDER=lm_studio
LM_STUDIO_BASE_URL=http://localhost:1234/v1
LM_STUDIO_MODEL_NAME=local-model
```

**Pros**: Free, private, offline
**Cons**: Requires local GPU, model download

---

### **2. Google Gemini** (Cloud)

```bash
# Get API key: https://makersuite.google.com/app/apikey

# .env
LLM_PROVIDER=gemini
GEMINI_API_KEY=your-api-key-here
GEMINI_MODEL_NAME=gemini-pro
```

**Pros**: Powerful, affordable, fast
**Cons**: Requires internet, Google account

---

### **3. OpenAI** (Cloud)

```bash
# Get API key: https://platform.openai.com/api-keys

# .env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_MODEL_NAME=gpt-4o-mini
```

**Pros**: Industry standard, very powerful, reliable
**Cons**: More expensive, requires internet

---

## 📊 Model Comparison

### **OpenAI Models**

| Model | Cost (Input/Output) | Best For | Speed |
|-------|---------------------|----------|-------|
| `gpt-4o` | $2.50 / $10.00 per 1M tokens | Complex reasoning, latest | Fast |
| `gpt-4o-mini` | $0.15 / $0.60 per 1M tokens | General tasks, cost-effective | Very Fast |
| `gpt-4-turbo` | $10.00 / $30.00 per 1M tokens | Advanced tasks | Medium |
| `gpt-3.5-turbo` | $0.50 / $1.50 per 1M tokens | Simple tasks, fastest | Fastest |

**Recommended**: `gpt-4o-mini` (best balance of cost/performance)

### **Gemini Models**

| Model | Cost | Best For |
|-------|------|----------|
| `gemini-pro` | Free tier available | General tasks |
| `gemini-1.5-pro` | $0.00125 / $0.005 per 1K chars | Complex reasoning |
| `gemini-1.5-flash` | $0.000125 / $0.0005 per 1K chars | Fast responses |

### **LM Studio**

| Model | Cost | Best For |
|-------|------|----------|
| Any local model | Free | Privacy, offline, unlimited |

---

## 🚀 Usage Examples

### **Switch Provider**

```bash
# Edit .env
LLM_PROVIDER=openai  # or gemini, or lm_studio
```

### **Use Different Models**

```bash
# OpenAI
OPENAI_MODEL_NAME=gpt-4o          # Most capable
OPENAI_MODEL_NAME=gpt-4o-mini     # Cost-effective
OPENAI_MODEL_NAME=gpt-3.5-turbo   # Fastest/cheapest

# Gemini
GEMINI_MODEL_NAME=gemini-pro
GEMINI_MODEL_NAME=gemini-1.5-pro
GEMINI_MODEL_NAME=gemini-1.5-flash

# LM Studio
LM_STUDIO_MODEL_NAME=llama-3.1-8b
LM_STUDIO_MODEL_NAME=mistral-7b
```

### **Runtime Override**

```python
from src.services.llm_service import LLMService

# Force specific provider
llm_openai = LLMService(provider="openai", model_name="gpt-4o-mini")
llm_gemini = LLMService(provider="gemini", model_name="gemini-pro")
llm_local = LLMService(provider="lm_studio")
```

---

## 💰 Cost Comparison

### **Example: 1 Million Tokens**

**Input + Output (50/50 split)**:

| Provider | Model | Cost |
|----------|-------|------|
| LM Studio | Any | $0 |
| Gemini | gemini-1.5-flash | ~$0.31 |
| Gemini | gemini-1.5-pro | ~$3.13 |
| OpenAI | gpt-3.5-turbo | $1.00 |
| OpenAI | gpt-4o-mini | $0.38 |
| OpenAI | gpt-4o | $6.25 |
| OpenAI | gpt-4-turbo | $20.00 |

**Recommendation for Production**:
- **Budget**: `gpt-4o-mini` or `gemini-1.5-flash`
- **Quality**: `gpt-4o` or `gemini-1.5-pro`
- **Free**: LM Studio (local)

---

## 🧪 Testing

### **Test All Providers**

```python
# scripts/test_all_providers.py
import asyncio
from src.services.llm_service import LLMService

async def test_all():
    providers = ["lm_studio", "gemini", "openai"]
    
    for provider in providers:
        try:
            llm = LLMService(provider=provider)
            success = await llm.test_connection()
            print(f"{provider}: {'✅' if success else '❌'}")
        except Exception as e:
            print(f"{provider}: ❌ {e}")

asyncio.run(test_all())
```

### **Compare Response Quality**

```python
async def compare_quality():
    question = "Explain quantum computing in simple terms."
    
    for provider in ["lm_studio", "gemini", "openai"]:
        llm = LLMService(provider=provider)
        response = await llm.llm.ainvoke(question)
        print(f"\n{provider}:\n{response.content}\n")
```

---

## 🎯 Use Case Recommendations

### **Use LM Studio when**:
- ✅ Privacy is critical (medical, legal, financial data)
- ✅ No internet connection available
- ✅ Unlimited free usage needed
- ✅ Custom/fine-tuned models required
- ✅ Development/testing

### **Use Gemini when**:
- ✅ Cost-effective cloud solution needed
- ✅ Good quality at low price
- ✅ Multimodal capabilities (future)
- ✅ Google ecosystem integration

### **Use OpenAI when**:
- ✅ Best quality required
- ✅ Production-grade reliability needed
- ✅ Industry standard compliance
- ✅ Advanced reasoning tasks
- ✅ Well-documented API

---

## 🔒 Security Best Practices

### **API Key Management**

```bash
# ❌ NEVER commit .env to git
echo ".env" >> .gitignore

# ✅ Use environment variables
export OPENAI_API_KEY=sk-...
export GEMINI_API_KEY=...

# ✅ Use secrets manager in production
# AWS Secrets Manager, Google Secret Manager, etc.
```

### **Rate Limiting**

```python
# Add rate limiting for production
from ratelimit import limits, sleep_and_retry

@sleep_and_retry
@limits(calls=60, period=60)  # 60 calls per minute
async def call_llm(llm_service, message):
    return await llm_service.llm.ainvoke(message)
```

---

## 🐛 Troubleshooting

### **OpenAI: "Invalid API key"**

```bash
# Check API key format
echo $OPENAI_API_KEY
# Should start with: sk-proj-... or sk-...

# Verify at: https://platform.openai.com/api-keys
```

### **OpenAI: "Rate limit exceeded"**

**Free tier limits**:
- 3 requests/min
- 200 requests/day

**Solution**: Upgrade to paid tier or add delays

### **OpenAI: "Insufficient quota"**

**Solution**: Add payment method at https://platform.openai.com/account/billing

### **All Providers: "Connection timeout"**

```bash
# Increase timeout in .env
LLM_REQUEST_TIMEOUT=120  # seconds
```

---

## 📊 Monitoring

### **Track Usage**

```python
# Add logging
import logging

logger = logging.getLogger(__name__)

async def track_usage(provider, model, tokens_used):
    logger.info(f"Provider: {provider}, Model: {model}, Tokens: {tokens_used}")
```

### **Cost Tracking**

```python
# Estimate costs
def estimate_cost(provider, model, input_tokens, output_tokens):
    costs = {
        "openai": {
            "gpt-4o-mini": (0.15, 0.60),  # per 1M tokens
            "gpt-4o": (2.50, 10.00),
        },
        "gemini": {
            "gemini-1.5-flash": (0.125, 0.50),  # per 1M chars
        }
    }
    # Calculate...
```

---

## 🚀 Quick Start Commands

```bash
# 1. Install (if not already)
pip install langchain-google-genai  # For Gemini
# OpenAI already included in langchain-openai

# 2. Get API keys
# OpenAI: https://platform.openai.com/api-keys
# Gemini: https://makersuite.google.com/app/apikey

# 3. Configure
echo "LLM_PROVIDER=openai" >> .env
echo "OPENAI_API_KEY=sk-your-key" >> .env
echo "OPENAI_MODEL_NAME=gpt-4o-mini" >> .env

# 4. Test
curl -X POST "http://localhost:8000/chat/" \
  -d '{"message": "Hello from OpenAI!"}'
```

---

## 📚 Resources

### **OpenAI**
- API Keys: https://platform.openai.com/api-keys
- Pricing: https://openai.com/api/pricing/
- Docs: https://platform.openai.com/docs/
- Models: https://platform.openai.com/docs/models

### **Gemini**
- API Keys: https://makersuite.google.com/app/apikey
- Pricing: https://ai.google.dev/pricing
- Docs: https://ai.google.dev/docs

### **LM Studio**
- Download: https://lmstudio.ai/
- Models: https://huggingface.co/models

---

## 💡 Pro Tips

1. **Development**: Use LM Studio (free, unlimited)
2. **Production**: Use OpenAI `gpt-4o-mini` (best value)
3. **Budget**: Use Gemini `gemini-1.5-flash` (cheapest cloud)
4. **Quality**: Use OpenAI `gpt-4o` (best performance)
5. **Hybrid**: LM Studio for dev, OpenAI for prod
6. **Fallback**: Configure multiple providers for reliability

```python
# Fallback example
async def get_response_with_fallback(message):
    providers = ["openai", "gemini", "lm_studio"]
    
    for provider in providers:
        try:
            llm = LLMService(provider=provider)
            return await llm.llm.ainvoke(message)
        except Exception as e:
            logger.warning(f"{provider} failed: {e}")
            continue
    
    raise Exception("All providers failed")
```
