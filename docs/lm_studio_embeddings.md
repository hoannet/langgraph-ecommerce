# LM Studio Embedding Setup Guide

## 🎯 Overview

Sử dụng **LM Studio** với model **google/embedding-gemma-300m** để tạo embeddings local, miễn phí và private cho RAG system.

## 📊 Model Comparison

| Provider | Model | Dimensions | Cost | Privacy | Speed |
|----------|-------|------------|------|---------|-------|
| **LM Studio** | embedding-gemma-300m | 768 | Free | 100% Local | Fast |
| OpenAI | text-embedding-ada-002 | 1536 | $0.0001/1K tokens | Cloud | Fast |
| Gemini | models/embedding-001 | 768 | Free tier | Cloud | Fast |

## 🚀 Setup LM Studio for Embeddings

### **Step 1: Download LM Studio**

1. Visit https://lmstudio.ai/
2. Download for your OS
3. Install and open

### **Step 2: Download Embedding Model**

1. Open LM Studio
2. Go to **Search** tab
3. Search: `google/embedding-gemma-300m`
4. Download the model (GGUF format)
5. Wait for download to complete

### **Step 3: Start Local Server**

1. Go to **Local Server** tab
2. Select model: `google/embedding-gemma-300m`
3. Click **Start Server**
4. Server runs on: `http://localhost:1234`

### **Step 4: Configure Application**

```bash
# .env
EMBEDDING_PROVIDER=lm_studio
LM_STUDIO_BASE_URL=http://localhost:1234/v1
LM_STUDIO_EMBEDDING_MODEL=google/embedding-gemma-300m
LM_STUDIO_API_KEY=not-needed

# TiDB Vector
TIDB_EMBEDDING_DIMENSION=768  # Important: gemma-300m uses 768
```

---

## 🧪 Testing

### **Test Embedding Generation**

```python
from src.services.vector_store import TiDBVectorStore

# Initialize with LM Studio
vector_store = TiDBVectorStore(embedding_provider="lm_studio")

# Test embedding
from langchain_core.documents import Document

docs = [Document(page_content="This is a test document")]
await vector_store.add_documents(docs)

print("✅ LM Studio embeddings working!")
```

### **Test via API**

```bash
# Upload document (will use LM Studio embeddings)
curl -X POST "http://localhost:8000/rag/upload" \
  -F "file=@test.txt"

# Query (will use LM Studio embeddings)
curl -X POST "http://localhost:8000/rag/query" \
  -d '{"query": "test query"}'
```

---

## 🔧 Configuration Options

### **Switch Between Providers**

```bash
# Use LM Studio (local, free)
EMBEDDING_PROVIDER=lm_studio

# Use OpenAI (cloud, paid)
EMBEDDING_PROVIDER=openai

# Use Gemini (cloud, free tier)
EMBEDDING_PROVIDER=gemini
```

### **Embedding Dimensions**

**Important**: Different models have different dimensions!

```bash
# LM Studio (gemma-300m)
TIDB_EMBEDDING_DIMENSION=768

# OpenAI (ada-002)
TIDB_EMBEDDING_DIMENSION=1536

# Gemini (embedding-001)
TIDB_EMBEDDING_DIMENSION=768
```

---

## 💡 Why Use LM Studio Embeddings?

### **Advantages** ✅

1. **100% Free** - No API costs
2. **100% Private** - Data never leaves your machine
3. **Offline** - Works without internet
4. **No Rate Limits** - Unlimited usage
5. **Fast** - Local processing

### **Disadvantages** ❌

1. **Requires GPU** - For good performance
2. **Lower Quality** - Compared to OpenAI ada-002
3. **Setup Required** - Need to download model
4. **Resource Usage** - Uses local RAM/VRAM

---

## 🎯 Use Cases

### **Best for LM Studio:**
- Development and testing
- Privacy-sensitive data
- High-volume processing
- Offline environments
- Cost-conscious projects

### **Best for OpenAI:**
- Production deployments
- Highest quality needed
- Low-volume usage
- No local GPU available

### **Best for Gemini:**
- Cost-effective cloud solution
- Good quality at low cost
- Integration with Google ecosystem

---

## 📊 Performance Comparison

### **Embedding Generation Speed**

| Provider | 100 Documents | 1000 Documents |
|----------|---------------|----------------|
| LM Studio (GPU) | ~2-3 sec | ~20-30 sec |
| LM Studio (CPU) | ~10-15 sec | ~100-150 sec |
| OpenAI | ~1-2 sec | ~10-20 sec |
| Gemini | ~1-2 sec | ~10-20 sec |

### **Quality (Retrieval Accuracy)**

| Provider | Accuracy | Notes |
|----------|----------|-------|
| OpenAI ada-002 | ⭐⭐⭐⭐⭐ | Best quality |
| Gemini embedding-001 | ⭐⭐⭐⭐ | Very good |
| LM Studio gemma-300m | ⭐⭐⭐ | Good for most cases |

---

## 🔄 Migration Between Providers

### **From OpenAI to LM Studio**

```bash
# 1. Update config
EMBEDDING_PROVIDER=lm_studio
TIDB_EMBEDDING_DIMENSION=768  # Change from 1536

# 2. Re-index all documents
# Documents need to be re-embedded with new model
```

### **Important Notes**

- **Cannot mix embeddings** from different models in same vector store
- **Must re-index** all documents when changing providers
- **Dimension must match** the model's output dimension

---

## 🐛 Troubleshooting

### **LM Studio Server Not Running**

```bash
# Check if server is running
curl http://localhost:1234/v1/models

# Expected response:
{
  "data": [
    {
      "id": "google/embedding-gemma-300m",
      ...
    }
  ]
}
```

### **Dimension Mismatch Error**

```
Error: Vector dimension mismatch
```

**Solution:**
```bash
# Make sure dimension matches model
TIDB_EMBEDDING_DIMENSION=768  # For gemma-300m
```

### **Slow Embedding Generation**

**Solutions:**
1. Use GPU instead of CPU in LM Studio
2. Reduce chunk size
3. Process in batches
4. Switch to cloud provider (OpenAI/Gemini)

---

## 🎨 Example: Complete Workflow

```python
# 1. Initialize with LM Studio
from src.services.document_service import DocumentService
from src.services.vector_store import TiDBVectorStore

vector_store = TiDBVectorStore(embedding_provider="lm_studio")
doc_service = DocumentService(vector_store=vector_store)

# 2. Index document
result = await doc_service.index_document("document.pdf")
print(f"Indexed {result['num_chunks']} chunks")

# 3. Search
docs = await doc_service.search_documents("query", k=4)
for doc in docs:
    print(f"Score: {doc.metadata['score']:.3f}")
    print(f"Content: {doc.page_content[:100]}...")
```

---

## 📈 Optimization Tips

### **1. Batch Processing**

```python
# Process multiple documents in batch
for file in files:
    await doc_service.index_document(file)
    # LM Studio handles batching internally
```

### **2. GPU Acceleration**

In LM Studio:
1. Settings → Hardware
2. Enable GPU acceleration
3. Allocate more VRAM if available

### **3. Caching**

```python
# Cache frequently used embeddings
from functools import lru_cache

@lru_cache(maxsize=1000)
def get_cached_embedding(text: str):
    return embeddings.embed_query(text)
```

---

## 🔐 Security & Privacy

### **Advantages of Local Embeddings**

1. **Data Privacy** - Documents never sent to cloud
2. **Compliance** - Meets strict data regulations
3. **No Logging** - No external tracking
4. **Full Control** - Complete ownership of process

### **Use Cases for Privacy**

- Medical records
- Legal documents
- Financial data
- Proprietary information
- Personal data (GDPR compliance)

---

## 🚀 Production Deployment

### **Hybrid Approach**

```python
# Use LM Studio for dev, OpenAI for prod
import os

if os.getenv("ENV") == "production":
    embedding_provider = "openai"
else:
    embedding_provider = "lm_studio"

vector_store = TiDBVectorStore(embedding_provider=embedding_provider)
```

### **Load Balancing**

```python
# Distribute load across multiple LM Studio instances
providers = ["lm_studio_1", "lm_studio_2", "lm_studio_3"]
provider = providers[hash(document_id) % len(providers)]
```

---

## 📚 Resources

- **LM Studio**: https://lmstudio.ai/
- **Gemma Models**: https://huggingface.co/google/gemma-300m
- **TiDB Vector**: https://docs.pingcap.com/tidbcloud/vector-search-overview
- **LangChain Embeddings**: https://python.langchain.com/docs/modules/data_connection/text_embedding/

---

## 💡 Pro Tips

1. **Start with LM Studio** for development
2. **Switch to OpenAI** for production if quality matters
3. **Use Gemini** for cost-effective cloud solution
4. **Monitor performance** and adjust based on needs
5. **Keep embeddings consistent** - don't mix providers
