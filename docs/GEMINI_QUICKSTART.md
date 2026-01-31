# Quick Start: Using Gemini

## 🚀 Setup (2 minutes)

### 1. Get API Key
Visit: https://makersuite.google.com/app/apikey

### 2. Configure
```bash
# Edit .env file
LLM_PROVIDER=gemini
GEMINI_API_KEY=your-api-key-here
GEMINI_MODEL_NAME=gemini-pro
```

### 3. Test
```bash
python scripts/test_gemini.py
```

## 💡 Usage

### In Code
```python
from src.services.llm_service import LLMService

# Use Gemini
llm_service = LLMService(provider="gemini")
response = await llm_service.llm.ainvoke("Hello!")
```

### Switch Back to LM Studio
```bash
# In .env
LLM_PROVIDER=lm_studio
```

## 📚 Full Documentation
- [Complete Guide](file:///Users/springhoan/DataWork/springme/projects/agentic-ai/langgraph-test/docs/gemini_integration.md)
- [Test Script](file:///Users/springhoan/DataWork/springme/projects/agentic-ai/langgraph-test/scripts/test_gemini.py)
- [Walkthrough](file:///Users/springhoan/.gemini/antigravity/brain/e0b10a3a-46be-4301-902c-ba743ccc09fc/walkthrough.md)
