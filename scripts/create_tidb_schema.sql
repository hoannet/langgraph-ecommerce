-- TiDB Vector Database Schema for RAG Documents

-- Create documents table with vector support
CREATE TABLE IF NOT EXISTS documents (
    id VARCHAR(255) PRIMARY KEY,
    document TEXT NOT NULL,
    embedding VECTOR(768) NOT NULL COMMENT 'Vector embedding (768 dimensions for Gemma-300m)',
    meta JSON DEFAULT NULL COMMENT 'Document metadata',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Vector index for similarity search
    VECTOR INDEX idx_embedding (embedding)
) COMMENT='RAG documents with vector embeddings';

-- Optional: Create metadata indexes for filtering
CREATE INDEX idx_created_at ON documents(created_at);

-- Optional: Create index on metadata fields (if you use specific metadata keys)
-- Example: CREATE INDEX idx_category ON documents((CAST(meta->>'$.category' AS CHAR(50))));

-- View table structure
DESCRIBE documents;

-- Check vector index
SHOW INDEX FROM documents;
