# RAG Mixed Provider Optimization Guide

## Configuration

**Current Setup** (Optimized):
```env
LLM_PROVIDER=openai
EMBEDDING_PROVIDER=lm_studio
TIDB_SEARCH_TOP_K=6  # Increased from 4
```

## Why This Works ✅

- **Cost-effective**: LM Studio embeddings are free (local)
- **High-quality**: OpenAI GPT-4o-mini for responses
- **Independent**: Embeddings and LLM work separately

## Optimizations Applied

### 1. Increased Top-K Retrieval
```env
TIDB_SEARCH_TOP_K=6  # Was: 4
```
**Benefit**: Retrieve more documents → better recall

### 2. Enhanced Logging
```python
# Provider info on startup
ℹ️  Mixed provider setup: LLM=openai, Embedding=lm_studio. Retrieval top_k=6

# Retrieval metrics
📚 Retrieved 6 docs | Query: 'Tiêu chí đánh giá rủi ro...' | Avg score: 0.842
```

### 3. Similarity Score Tracking
- Logs average relevance score
- Helps identify retrieval quality issues

## Monitoring

### Check Logs For:

**Good Retrieval**:
```
📚 Retrieved 6 docs | Avg score: 0.85  ✅ High relevance
```

**Poor Retrieval**:
```
📚 Retrieved 6 docs | Avg score: 0.45  ⚠️ Low relevance
```

### Actions:

- **If avg score < 0.5**: Consider better embedding model
- **If no docs found**: Check document indexing
- **If too many rewrites**: Increase top-k further

## Performance Tuning

### Increase Quality
```env
TIDB_SEARCH_TOP_K=8  # More documents
```

### Reduce Latency
```env
TIDB_SEARCH_TOP_K=4  # Fewer documents
```

### Try Better Embeddings
```env
# Download in LM Studio first
LM_STUDIO_EMBEDDING_MODEL=nomic-ai/nomic-embed-text-v1.5
```
**Note**: Requires re-indexing all documents!

## Best Practices

1. **Monitor logs** - Watch similarity scores
2. **Test queries** - Verify retrieval quality
3. **Tune top-k** - Balance quality vs speed
4. **Keep embeddings** - Don't change model often

## Troubleshooting

### Poor Answer Quality
- Check similarity scores in logs
- Increase `TIDB_SEARCH_TOP_K`
- Try better embedding model

### Slow Responses
- Decrease `TIDB_SEARCH_TOP_K`
- Check LM Studio performance
- Optimize document chunking

### No Documents Retrieved
- Verify documents are indexed
- Check embedding model is running
- Test vector store connection
