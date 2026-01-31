# Google Gemini Integration Guide

## 🎯 Overview

Bạn có thể chọn giữa **2 LLM providers**:
1. **LM Studio** - Local LLM (privacy, free)
2. **Google Gemini** - Cloud API (powerful, requires API key)

## 🔧 Setup Gemini

### **Step 1: Get Gemini API Key**

1. Truy cập: https://makersuite.google.com/app/apikey
2. Đăng nhập với Google account
3. Click "Create API Key"
4. Copy API key

### **Step 2: Configure .env**

```bash
# Edit .env file
nano .env

# Add/Update these lines:
LLM_PROVIDER=gemini
GEMINI_API_KEY=your-actual-api-key-here
GEMINI_MODEL_NAME=gemini-pro
```

### **Step 3: Install Dependencies**

```bash
pip install langchain-google-genai
```

### **Step 4: Restart Server**

```bash
# Server will auto-reload if using --reload
# Or manually restart:
make run
```

---

## 📝 Configuration Options

### **Use LM Studio** (Default)

```bash
# .env
LLM_PROVIDER=lm_studio
LM_STUDIO_BASE_URL=http://localhost:1234/v1
LM_STUDIO_MODEL_NAME=local-model
```

### **Use Gemini**

```bash
# .env
LLM_PROVIDER=gemini
GEMINI_API_KEY=AIzaSy...your-key
GEMINI_MODEL_NAME=gemini-pro
```

---

## 🤖 Available Gemini Models

| Model | Description | Best For |
|-------|-------------|----------|
| `gemini-pro` | Standard model | General tasks, chat |
| `gemini-1.5-pro` | Latest, most capable | Complex reasoning |
| `gemini-1.5-flash` | Faster, cheaper | Quick responses |

**Update model**:
```bash
# .env
GEMINI_MODEL_NAME=gemini-1.5-pro
```

---

## 🧪 Testing

### **Test Connection**

```python
# scripts/test_gemini.py
import asyncio
from src.services.llm_service import LLMService

async def test():
    # Test Gemini
    llm = LLMService(provider="gemini")
    success = await llm.test_connection()
    print(f"Gemini: {'✅' if success else '❌'}")

asyncio.run(test())
```

### **Test via API**

```bash
# Make sure LLM_PROVIDER=gemini in .env
curl -X POST "http://localhost:8000/chat/" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, are you using Gemini?"}'
```

---

## 🔄 Switching Providers

### **Method 1: Environment Variable** (Recommended)

```bash
# Edit .env
LLM_PROVIDER=gemini  # or lm_studio
```

### **Method 2: Runtime Override**

```python
# In code
from src.services.llm_service import LLMService

# Force Gemini
llm_gemini = LLMService(provider="gemini")

# Force LM Studio
llm_local = LLMService(provider="lm_studio")
```

---

## 💰 Pricing (Gemini)

**Gemini Pro** (Free tier):
- 60 requests per minute
- 1,500 requests per day
- Free for development

**Gemini 1.5 Pro**:
- Input: $0.00125 / 1K characters
- Output: $0.005 / 1K characters

**Gemini 1.5 Flash**:
- Input: $0.000125 / 1K characters
- Output: $0.0005 / 1K characters

---

## 🔍 Comparison

| Feature | LM Studio | Gemini |
|---------|-----------|--------|
| **Cost** | Free | Free tier + paid |
| **Privacy** | 100% local | Cloud (Google) |
| **Speed** | Depends on hardware | Fast (cloud) |
| **Quality** | Depends on model | Very high |
| **Setup** | Download model | API key only |
| **Internet** | Not required | Required |

---

## 🎯 Use Cases

### **Use LM Studio when**:
- ✅ Privacy is critical
- ✅ No internet connection
- ✅ Free unlimited usage
- ✅ Custom/fine-tuned models

### **Use Gemini when**:
- ✅ Need best quality
- ✅ Fast responses required
- ✅ No local GPU
- ✅ Production deployment

---

## 🐛 Troubleshooting

### **Error: "Gemini API key not configured"**

**Solution**:
```bash
# Check .env file
cat .env | grep GEMINI_API_KEY

# Should show:
GEMINI_API_KEY=AIzaSy...

# If empty, add your key
echo "GEMINI_API_KEY=your-key-here" >> .env
```

### **Error: "Failed to initialize gemini LLM"**

**Possible causes**:
1. Invalid API key
2. Missing dependency

**Solution**:
```bash
# Install dependency
pip install langchain-google-genai

# Verify API key
# Visit: https://makersuite.google.com/app/apikey
```

### **Error: Rate limit exceeded**

**Solution**:
- Free tier: 60 requests/min
- Wait or upgrade to paid tier

---

## 📊 Monitoring

### **Check Current Provider**

```bash
# View logs
tail -f data/logs/chatbot.log | grep "Initialized LLM"

# Should show:
# Initialized LLM service with provider=gemini, model=gemini-pro
```

### **Test Both Providers**

```python
import asyncio
from src.services.llm_service import LLMService

async def compare():
    # Test LM Studio
    llm_local = LLMService(provider="lm_studio")
    local_ok = await llm_local.test_connection()
    
    # Test Gemini
    llm_gemini = LLMService(provider="gemini")
    gemini_ok = await llm_gemini.test_connection()
    
    print(f"LM Studio: {'✅' if local_ok else '❌'}")
    print(f"Gemini: {'✅' if gemini_ok else '❌'}")

asyncio.run(compare())
```

---

## 🚀 Quick Start

```bash
# 1. Get API key
# Visit: https://makersuite.google.com/app/apikey

# 2. Configure
echo "LLM_PROVIDER=gemini" >> .env
echo "GEMINI_API_KEY=your-key" >> .env

# 3. Install
pip install langchain-google-genai

# 4. Test
curl -X POST "http://localhost:8000/chat/" \
  -d '{"message": "Hello from Gemini!"}'
```

---

## 💡 Best Practices

1. **Development**: Use LM Studio (free, unlimited)
2. **Production**: Use Gemini (reliable, scalable)
3. **Hybrid**: LM Studio for dev, Gemini for prod
4. **API Key Security**: Never commit .env to git
5. **Cost Control**: Monitor usage in Google Cloud Console

---

## 📚 Resources

- **Gemini API Docs**: https://ai.google.dev/docs
- **Get API Key**: https://makersuite.google.com/app/apikey
- **Pricing**: https://ai.google.dev/pricing
- **LangChain Gemini**: https://python.langchain.com/docs/integrations/chat/google_generative_ai
