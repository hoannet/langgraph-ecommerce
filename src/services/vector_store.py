"""TiDB Vector Store for RAG."""

from typing import List, Optional, Dict, Any
from datetime import datetime

from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from src.core.config import get_settings
from src.core.logging import get_logger
from src.core.exceptions import LLMError
from src.database.tidb import TiDBVector

logger = get_logger(__name__)


class TiDBVectorStore:
    """Vector store using TiDB Serverless with shared client."""

    def __init__(
        self,
        embedding_provider: Optional[str] = None,
    ) -> None:
        """
        Initialize TiDB vector store.

        Args:
            embedding_provider: 'openai', 'gemini', or 'lm_studio'
        """
        settings = get_settings()

        self.embedding_provider = embedding_provider or settings.embedding_provider
        self.top_k = settings.tidb_search_top_k

        # Initialize embeddings based on provider
        if self.embedding_provider == "lm_studio":
            # Use custom LM Studio embeddings (default)
            from src.services.lm_studio_embeddings import LMStudioEmbeddings
            self.embeddings = LMStudioEmbeddings(
                model=settings.lm_studio_embedding_model,
                base_url=settings.lm_studio_base_url,
                api_key=settings.lm_studio_api_key,
            )
            logger.info(f"Using LM Studio embeddings: {settings.lm_studio_embedding_model} (768 dimensions)")
        elif self.embedding_provider == "openai":
            self.embeddings = OpenAIEmbeddings(
                model="text-embedding-ada-002"
            )
            logger.info("Using OpenAI embeddings (1536 dimensions)")
        elif self.embedding_provider == "gemini":
            self.embeddings = GoogleGenerativeAIEmbeddings(
                model="models/embedding-001"
            )
            logger.info("Using Gemini embeddings (768 dimensions)")
        else:
            # Fallback to LM Studio if unknown provider
            logger.warning(f"Unknown embedding provider '{self.embedding_provider}', falling back to LM Studio")
            from src.services.lm_studio_embeddings import LMStudioEmbeddings
            self.embeddings = LMStudioEmbeddings(
                model=settings.lm_studio_embedding_model,
                base_url=settings.lm_studio_base_url,
                api_key=settings.lm_studio_api_key,
            )

        # Get shared TiDB client
        try:
            self.client = TiDBVector.get_client()
            logger.info(f"Using shared TiDB client: provider={self.embedding_provider}")
        except RuntimeError:
            # Client not initialized, connect now
            logger.warning("TiDB client not initialized, connecting now...")
            TiDBVector.connect()
            self.client = TiDBVector.get_client()

    async def add_documents(
        self,
        documents: List[Document],
        ids: Optional[List[str]] = None,
    ) -> List[str]:
        """
        Add documents to vector store.

        Args:
            documents: List of documents to add
            ids: Optional list of document IDs

        Returns:
            List of document IDs
        """
        try:
            # Generate embeddings
            texts = [doc.page_content for doc in documents]
            
            # Filter out empty texts
            if not texts or all(not t.strip() for t in texts):
                raise LLMError("No valid text content to embed")
            
            logger.info(f"Generating embeddings for {len(texts)} documents...")
            
            # Generate embeddings - handle both sync and async
            try:
                embeddings = await self.embeddings.aembed_documents(texts)
            except Exception as e:
                logger.warning(f"Async embedding failed: {e}, trying sync method...")
                # Fallback to sync method
                import asyncio
                embeddings = await asyncio.to_thread(self.embeddings.embed_documents, texts)

            logger.info(f"Generated {len(embeddings)} embeddings")

            # Prepare documents with metadata
            doc_ids = ids or [f"doc_{i}_{datetime.now().timestamp()}" for i in range(len(documents))]

            # Add to TiDB using batch insert
            metadatas = [doc.metadata for doc in documents]
            
            self.client.insert(
                texts=texts,
                embeddings=embeddings,
                metadatas=metadatas,
                ids=doc_ids,
            )

            logger.info(f"Added {len(documents)} documents to TiDB vector store")
            return doc_ids

        except Exception as e:
            logger.error(f"Failed to add documents: {e}")
            raise LLMError(f"Failed to add documents: {e}")

    async def similarity_search(
        self,
        query: str,
        k: Optional[int] = None,
        filter: Optional[Dict[str, Any]] = None,
    ) -> List[Document]:
        """
        Search for similar documents.

        Args:
            query: Query text
            k: Number of results to return
            filter: Metadata filter

        Returns:
            List of similar documents
        """
        try:
            k = k or self.top_k
            
            logger.info(f"🔍 Starting vector search: query='{query[:50]}...', k={k}, filter={filter}")

            # Generate query embedding
            logger.info(f"📝 Generating embedding for query using {self.embedding_provider}")
            query_embedding = await self.embeddings.aembed_query(query)
            logger.info(f"✅ Generated embedding vector (dim={len(query_embedding)})")

            # Query TiDB with retry logic
            max_retries = 3
            retry_delay = 1  # seconds
            
            for attempt in range(max_retries):
                try:
                    logger.info(f"🗄️  Querying TiDB vector store (attempt {attempt + 1}/{max_retries})...")
                    results = self.client.query(
                        query_vector=query_embedding,
                        k=k,
                        filter=filter,
                    )
                    logger.info(f"✅ TiDB returned {len(results)} results")
                    break  # Success, exit retry loop
                    
                except Exception as e:
                    if attempt < max_retries - 1:
                        logger.warning(f"⚠️  TiDB query failed (attempt {attempt + 1}): {e}. Retrying in {retry_delay}s...")
                        import asyncio
                        await asyncio.sleep(retry_delay)
                        retry_delay *= 2  # Exponential backoff
                    else:
                        logger.error(f"❌ TiDB query failed after {max_retries} attempts")
                        raise

            # Convert to Document objects
            documents = []
            for i, result in enumerate(results):
                # QueryResult is an object, not a dict
                # TiDB returns 'distance' (lower is better, cosine distance)
                # Convert to similarity score (higher is better): 1 - distance
                distance = result.distance if hasattr(result, 'distance') else 0.0
                similarity_score = 1.0 - distance  # Convert distance to similarity
                
                doc = Document(
                    page_content=result.document if hasattr(result, 'document') else str(result),
                    metadata={
                        "score": similarity_score,  # Use similarity score
                        "distance": distance,  # Keep original distance
                        "id": result.id if hasattr(result, 'id') else "",
                    }
                )
                # Add any metadata if available
                if hasattr(result, 'metadata') and result.metadata:
                    doc.metadata.update(result.metadata)
                
                logger.debug(f"  Result {i+1}: distance={distance:.3f}, similarity={similarity_score:.3f}, id={doc.metadata.get('id', 'N/A')}")
                documents.append(doc)

            logger.info(f"📚 Found {len(documents)} similar documents for query: {query[:50]}...")
            return documents

        except Exception as e:
            logger.error(f"❌ Failed to search documents: {e}", exc_info=True)
            raise LLMError(f"Failed to search documents: {e}")

    async def delete_documents(self, ids: List[str]) -> bool:
        """
        Delete documents by IDs.

        Args:
            ids: List of document IDs to delete

        Returns:
            True if successful
        """
        try:
            for doc_id in ids:
                self.client.delete(id=doc_id)

            logger.info(f"Deleted {len(ids)} documents from TiDB vector store")
            return True

        except Exception as e:
            logger.error(f"Failed to delete documents: {e}")
            return False

    async def get_document(self, doc_id: str) -> Optional[Document]:
        """
        Get document by ID.

        Args:
            doc_id: Document ID

        Returns:
            Document or None
        """
        try:
            result = self.client.get(id=doc_id)
            if result:
                return Document(
                    page_content=result.get("text", ""),
                    metadata=result.get("metadata", {})
                )
            return None

        except Exception as e:
            logger.error(f"Failed to get document: {e}")
            return None


def get_vector_store(embedding_provider: Optional[str] = None) -> TiDBVectorStore:
    """
    Get TiDB vector store instance.

    Args:
        embedding_provider: 'openai', 'gemini', or 'lm_studio' (default: from config)

    Returns:
        TiDBVectorStore instance
    """
    return TiDBVectorStore(embedding_provider=embedding_provider)
