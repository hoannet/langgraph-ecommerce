# RAG System with TiDB Vector - Complete Guide

## 🎯 Overview

Hệ thống RAG (Retrieval-Augmented Generation) hoàn chỉnh với:
- **TiDB Serverless** - Vector database
- **LangChain** - Document processing
- **LangGraph** - Agentic workflow
- **Multi-format support** - PDF, TXT, MD, DOCX

## 🏗️ Architecture

```mermaid
graph TB
    User[User Query] --> Workflow[RAG Workflow]
    Workflow --> Generate[Generate Query]
    Generate --> Retrieve[Retrieve Documents]
    Retrieve --> Grade[Grade Relevance]
    Grade -->|Relevant| Answer[Generate Answer]
    Grade -->|Not Relevant| Rewrite[Rewrite Question]
    Rewrite --> Generate
    Answer --> Response[Return Answer]
    
    Upload[Upload Document] --> Load[Load & Split]
    Load --> Embed[Generate Embeddings]
    Embed --> TiDB[(TiDB Vector)]
    Retrieve --> TiDB
```

## 🚀 Quick Start

### **1. Setup TiDB Serverless**

1. Visit https://tidbcloud.com/
2. Create free account
3. Create Serverless cluster
4. Get connection string

### **2. Configure Environment**

```bash
# .env
TIDB_CONNECTION_STRING=mysql+pymysql://user:password@gateway.tidbcloud.com:4000/database
TIDB_TABLE_NAME=documents
TIDB_EMBEDDING_DIMENSION=1536
TIDB_DISTANCE_STRATEGY=cosine
```

### **3. Install Dependencies**

```bash
pip install tidb-vector langchain-text-splitters langchain-community pypdf python-docx unstructured
```

### **4. Upload Documents**

```bash
curl -X POST "http://localhost:8000/rag/upload" \
  -F "file=@document.pdf" \
  -F 'metadata={"category": "product", "version": "1.0"}'
```

### **5. Query Knowledge Base**

```bash
curl -X POST "http://localhost:8000/rag/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the refund policy?"}'
```

---

## 📚 Components

### **1. Vector Store** - `vector_store.py`

```python
from src.services.vector_store import TiDBVectorStore

# Initialize
vector_store = TiDBVectorStore(embedding_provider="openai")

# Add documents
await vector_store.add_documents(documents)

# Search
results = await vector_store.similarity_search("query", k=4)
```

**Features:**
- TiDB vector client integration
- OpenAI & Gemini embeddings
- Similarity search (cosine, L2, inner product)
- Document CRUD operations

---

### **2. Document Service** - `document_service.py`

```python
from src.services.document_service import DocumentService

doc_service = DocumentService()

# Index document
result = await doc_service.index_document(
    file_path="document.pdf",
    metadata={"category": "faq"}
)

# Search
docs = await doc_service.search_documents("query", k=4)
```

**Supported Formats:**
- PDF (`.pdf`)
- Text (`.txt`)
- Markdown (`.md`)
- Word (`.docx`, `.doc`)

---

### **3. RAG Agent** - `rag.py`

```python
from src.agents.rag import RAGAgent

agent = RAGAgent()

# Process query
response = await agent.process(messages)

# Grade documents
is_relevant = await agent.grade_documents(query, docs)

# Rewrite question
new_query = await agent.rewrite_question(query)
```

**Capabilities:**
- Document retrieval
- Answer generation
- Document grading
- Question rewriting

---

### **4. Agentic Workflow** - `rag_workflow.py`

```python
from src.graphs.rag_workflow import get_rag_workflow
from langchain_core.messages import HumanMessage

workflow = get_rag_workflow()

result = await workflow.ainvoke({
    "messages": [HumanMessage(content="What are shipping options?")]
})
```

**Workflow Steps:**
1. **Generate Query** - Decide to retrieve or respond
2. **Retrieve** - Search knowledge base
3. **Grade** - Check document relevance
4. **Rewrite** - Improve question if not relevant
5. **Answer** - Generate final response

---

## 🔌 API Endpoints

### **Upload Document**

```bash
POST /rag/upload
Content-Type: multipart/form-data

file: document.pdf
metadata: {"category": "product"}
```

**Response:**
```json
{
  "status": "success",
  "file_name": "document.pdf",
  "num_pages": 10,
  "num_chunks": 45,
  "doc_ids": ["doc_1_...", "doc_2_..."]
}
```

---

### **Query Knowledge Base**

```bash
POST /rag/query
Content-Type: application/json

{
  "query": "What is the refund policy?",
  "k": 4
}
```

**Response:**
```json
{
  "answer": "Based on our refund policy...",
  "sources": ["refund_policy.pdf", "terms.pdf"]
}
```

---

### **List Documents**

```bash
GET /rag/documents
```

**Response:**
```json
{
  "documents": [
    {
      "filename": "policy.pdf",
      "size": 102400,
      "uploaded_at": 1706345678.0
    }
  ]
}
```

---

### **Delete Document**

```bash
DELETE /rag/documents/policy.pdf
```

---

## 🧪 Testing

### **1. Upload Test Document**

```bash
# Create test document
echo "Our refund policy allows returns within 30 days." > refund_policy.txt

# Upload
curl -X POST "http://localhost:8000/rag/upload" \
  -F "file=@refund_policy.txt"
```

### **2. Query**

```bash
curl -X POST "http://localhost:8000/rag/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "How long do I have to return items?"}'
```

**Expected Response:**
```json
{
  "answer": "You have 30 days to return items according to our refund policy.",
  "sources": ["refund_policy.txt"]
}
```

### **3. Integration with Chat**

```bash
# Via chat endpoint (if integrated)
curl -X POST "http://localhost:8000/chat/" \
  -d '{"message": "What is your refund policy?"}'
```

---

## 🎨 Integration with Existing Chat

### **Option 1: Add RAG Intent**

```python
# src/models/enums.py
class IntentType(str, Enum):
    FAQ = "faq"  # Use for RAG queries
    PAYMENT = "payment"
    GENERAL = "general"
```

### **Option 2: Route to RAG Agent**

```python
# src/graphs/nodes.py
async def route_to_agent(state: ChatState) -> str:
    intent = state.get("intent")
    
    if intent == IntentType.FAQ:
        return "rag_agent"  # Route to RAG
    elif intent == IntentType.PAYMENT:
        return "payment_agent"
    # ...
```

---

## 📊 TiDB Vector Schema

```sql
CREATE TABLE documents (
    id VARCHAR(255) PRIMARY KEY,
    content TEXT,
    metadata JSON,
    embedding VECTOR(1536),  -- OpenAI ada-002
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    VECTOR INDEX idx_embedding (embedding)
);
```

**Indexes:**
```sql
-- Vector index for similarity search
CREATE VECTOR INDEX idx_embedding ON documents(embedding);

-- Metadata index
CREATE INDEX idx_metadata ON documents((CAST(metadata->'$.category' AS CHAR(50))));
```

---

## 🔧 Configuration

### **Embedding Models**

**OpenAI (Default):**
```python
# .env
# Uses text-embedding-ada-002 (1536 dimensions)
```

**Gemini:**
```python
vector_store = TiDBVectorStore(embedding_provider="gemini")
# Uses models/embedding-001
```

### **Chunking Strategy**

```python
doc_service = DocumentService(
    chunk_size=1000,      # Characters per chunk
    chunk_overlap=200,    # Overlap between chunks
)
```

### **Search Parameters**

```python
# Number of results
TIDB_SEARCH_TOP_K=4

# Distance strategy
TIDB_DISTANCE_STRATEGY=cosine  # or l2, inner_product
```

---

## 🚨 Troubleshooting

### **TiDB Connection Error**

```bash
# Check connection string format
TIDB_CONNECTION_STRING=mysql+pymysql://user:password@host:4000/db?ssl_ca=/path/to/ca.pem

# Test connection
python -c "from src.services.vector_store import TiDBVectorStore; TiDBVectorStore()"
```

### **Embedding Error**

```bash
# Check API keys
echo $OPENAI_API_KEY
echo $GEMINI_API_KEY

# Test embeddings
python -c "from langchain_openai import OpenAIEmbeddings; OpenAIEmbeddings().embed_query('test')"
```

### **Document Upload Fails**

```bash
# Check file permissions
ls -la data/uploads/

# Create directory
mkdir -p data/uploads

# Check file size limits
# Default: No limit, but can configure in FastAPI
```

---

## 💡 Best Practices

### **1. Document Preparation**

- Clean text before upload
- Add meaningful metadata
- Use consistent naming
- Organize by category

### **2. Chunking**

- Adjust chunk_size based on content
- Use overlap for context preservation
- Test different strategies

### **3. Metadata**

```python
metadata = {
    "category": "product",
    "version": "1.0",
    "language": "en",
    "last_updated": "2026-01-27"
}
```

### **4. Query Optimization**

- Use specific questions
- Include context in queries
- Leverage metadata filters

---

## 📈 Performance

### **Indexing Speed**

- PDF (10 pages): ~5-10 seconds
- Text (1000 lines): ~2-3 seconds
- Depends on: file size, chunk size, embedding API

### **Query Speed**

- Vector search: ~100-200ms
- LLM generation: ~1-3 seconds
- Total: ~1.5-4 seconds

### **Optimization Tips**

1. **Batch Processing**
   ```python
   # Index multiple documents
   for file in files:
       await doc_service.index_document(file)
   ```

2. **Caching**
   - Cache frequent queries
   - Cache embeddings

3. **Async Processing**
   - Already implemented with async/await

---

## 🔐 Security

### **1. File Upload Validation**

```python
# Whitelist file types
allowed_extensions = {".pdf", ".txt", ".md", ".docx"}

# Size limits
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
```

### **2. Access Control**

```python
# Add user-based filtering
await vector_store.similarity_search(
    query="...",
    filter={"user_id": current_user.id}
)
```

### **3. API Key Security**

- Never commit .env
- Use environment variables
- Rotate keys regularly

---

## 🎯 Next Steps

1. **Advanced Features**
   - Hybrid search (vector + keyword)
   - Re-ranking
   - Multi-modal RAG

2. **Integration**
   - Add to chat workflow
   - Auto-detect FAQ intent
   - Fallback to RAG

3. **Monitoring**
   - Query analytics
   - Relevance metrics
   - Performance tracking

4. **UI Enhancement**
   - Document management UI
   - Query interface
   - Source highlighting
