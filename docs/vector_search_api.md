# Vector Search API Documentation

## Overview

Direct vector database search API - tìm kiếm documents dựa trên similarity scores **mà không qua RAG workflow**.

---

## Endpoints

### 1. POST `/rag/search` - Vector Search

**Tìm kiếm trực tiếp trong vector database**

#### Request

```json
{
  "query": "Tiêu chí đánh giá rủi ro",
  "k": 5,
  "threshold": 0.6
}
```

**Parameters**:
- `query` (string, required): Search query
- `k` (int, optional): Number of results (default: 4)
- `threshold` (float, optional): Minimum similarity score (0.0-1.0, default: 0.0)

#### Response

```json
{
  "query": "Tiêu chí đánh giá rủi ro",
  "count": 3,
  "results": [
    {
      "content": "Document content...",
      "score": 0.89,
      "source": "document.pdf",
      "metadata": {
        "page": 5,
        "chunk_id": "abc123"
      }
    },
    {
      "content": "Another document...",
      "score": 0.75,
      "source": "guide.pdf",
      "metadata": {}
    }
  ]
}
```

**Response Fields**:
- `query`: Original search query
- `count`: Number of results returned
- `results`: Array of matching documents
  - `content`: Document text content
  - `score`: Similarity score (0.0-1.0, higher = more similar)
  - `source`: Source filename
  - `metadata`: Additional metadata

---

## Comparison: `/search` vs `/query`

### `/rag/search` (Vector Search)
- ✅ **Direct vector search**
- ✅ **Fast** - no LLM calls
- ✅ **Raw results** with scores
- ✅ **Filterable** by threshold
- ❌ No answer generation
- **Use case**: Find similar documents, debug retrieval

### `/rag/query` (RAG)
- ✅ **Full RAG workflow**
- ✅ **Generated answer** from LLM
- ✅ **Document grading** & rewriting
- ✅ **Formatted response**
- ⏱️ Slower (LLM calls)
- **Use case**: Get answers to questions

---

## Usage Examples

### Example 1: Basic Search

```bash
curl -X POST "http://localhost:8000/rag/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "payment methods",
    "k": 5
  }'
```

**Response**:
```json
{
  "query": "payment methods",
  "count": 5,
  "results": [
    {
      "content": "We accept credit cards, PayPal, and bank transfers...",
      "score": 0.92,
      "source": "payment_guide.pdf",
      "metadata": {"page": 3}
    }
  ]
}
```

---

### Example 2: Filter by Threshold

```bash
curl -X POST "http://localhost:8000/rag/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "refund policy",
    "k": 10,
    "threshold": 0.7
  }'
```

**Returns**: Only results with score >= 0.7

---

### Example 3: Python Client

```python
import requests

def search_vectors(query: str, k: int = 5, threshold: float = 0.0):
    """Search vector database."""
    response = requests.post(
        "http://localhost:8000/rag/search",
        json={
            "query": query,
            "k": k,
            "threshold": threshold
        }
    )
    return response.json()

# Usage
results = search_vectors("shipping policy", k=5, threshold=0.6)
print(f"Found {results['count']} results")

for result in results['results']:
    print(f"Score: {result['score']:.3f} - {result['source']}")
    print(f"Content: {result['content'][:100]}...")
```

---

### Example 4: JavaScript/TypeScript

```typescript
interface VectorSearchRequest {
  query: string;
  k?: number;
  threshold?: number;
}

interface VectorSearchResponse {
  query: string;
  count: number;
  results: Array<{
    content: string;
    score: number;
    source: string;
    metadata: Record<string, any>;
  }>;
}

async function searchVectors(
  request: VectorSearchRequest
): Promise<VectorSearchResponse> {
  const response = await fetch('http://localhost:8000/rag/search', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request)
  });
  return response.json();
}

// Usage
const results = await searchVectors({
  query: 'return policy',
  k: 5,
  threshold: 0.6
});

console.log(`Found ${results.count} results`);
```

---

## Use Cases

### 1. Debug Retrieval Quality
```bash
# Check what documents are being retrieved
curl -X POST "http://localhost:8000/rag/search" \
  -d '{"query": "test query", "k": 10}'
```

**Look for**:
- Low similarity scores → embeddings issue
- Wrong documents → indexing issue
- No results → vector store issue

---

### 2. Find Similar Documents
```bash
# Find documents similar to a query
curl -X POST "http://localhost:8000/rag/search" \
  -d '{"query": "customer complaints", "k": 20, "threshold": 0.5}'
```

---

### 3. Quality Threshold Testing
```bash
# Test different thresholds
for threshold in 0.5 0.6 0.7 0.8; do
  echo "Threshold: $threshold"
  curl -X POST "http://localhost:8000/rag/search" \
    -d "{\"query\": \"test\", \"threshold\": $threshold}" | jq '.count'
done
```

---

## Response Interpretation

### Similarity Scores

| Score Range | Meaning |
|-------------|---------|
| 0.9 - 1.0   | Excellent match ✅ |
| 0.7 - 0.9   | Good match ✅ |
| 0.5 - 0.7   | Moderate match ⚠️ |
| 0.3 - 0.5   | Weak match ⚠️ |
| 0.0 - 0.3   | Poor match ❌ |

### Recommended Thresholds

- **High precision**: `threshold=0.7` (fewer, better results)
- **Balanced**: `threshold=0.6` (default for RAG)
- **High recall**: `threshold=0.4` (more results, some noise)

---

## Error Handling

### No Results
```json
{
  "query": "xyz",
  "count": 0,
  "results": []
}
```

**Possible causes**:
- No documents indexed
- Query too specific
- Threshold too high

### Error Response
```json
{
  "detail": "Search failed: connection error"
}
```

**HTTP Status**: 500

---

## Performance

### Typical Response Times

- **Vector search**: 50-200ms
- **RAG query**: 1-3s (includes LLM)

### Optimization Tips

1. **Limit k**: Don't retrieve more than needed
2. **Use threshold**: Filter early
3. **Cache results**: For repeated queries
4. **Index optimization**: Proper chunking

---

## Monitoring

### Log Output

```
Vector search: query='payment methods', k=5, threshold=0.6
Found 3 results (filtered by threshold=0.6)
```

### Metrics to Track

- Average similarity scores
- Number of results per query
- Response times
- Threshold effectiveness

---

## Best Practices

1. **Start with low threshold** (0.0) to see all results
2. **Tune threshold** based on score distribution
3. **Use appropriate k** - balance recall vs performance
4. **Monitor scores** - low scores indicate indexing issues
5. **Compare with RAG** - validate retrieval quality

---

## Related Endpoints

- `POST /rag/query` - Full RAG with answer generation
- `POST /rag/upload` - Upload and index documents
- `GET /rag/documents` - List indexed documents
- `DELETE /rag/documents/{filename}` - Delete document
