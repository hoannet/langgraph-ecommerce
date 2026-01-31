"""Retriever tool for RAG."""

from typing import List, Optional
from langchain_core.tools import Tool
from langchain_core.documents import Document

from src.services.document_service import DocumentService
from src.core.logging import get_logger

logger = get_logger(__name__)


def create_retriever_tool(
    document_service: Optional[DocumentService] = None,
    k: int = 4,
) -> Tool:
    """
    Create retriever tool for RAG.

    Args:
        document_service: Document service instance
        k: Number of documents to retrieve

    Returns:
        Retriever tool
    """
    doc_service = document_service or DocumentService()

    async def retrieve_documents(query: str) -> str:
        """
        Retrieve relevant documents from knowledge base.

        Args:
            query: Search query

        Returns:
            Formatted document content
        """
        try:
            # Search for relevant documents
            documents = await doc_service.search_documents(query=query, k=k)

            if not documents:
                return "No relevant documents found in the knowledge base."

            # Format documents
            formatted_docs = []
            scores = []
            for i, doc in enumerate(documents, 1):
                source = doc.metadata.get("source", "Unknown")
                score = doc.metadata.get("score", 0.0)
                scores.append(score)
                content = doc.page_content.strip()

                formatted_docs.append(
                    f"[Document {i}] (Source: {source}, Relevance: {score:.3f})\n{content}"
                )

            result = "\n\n---\n\n".join(formatted_docs)
            
            # Enhanced logging with scores
            avg_score = sum(scores) / len(scores) if scores else 0
            logger.info(
                f"📚 Retrieved {len(documents)} docs | "
                f"Query: '{query[:40]}...' | "
                f"Avg score: {avg_score:.3f}"
            )
            return result

        except Exception as e:
            logger.error(f"Failed to retrieve documents: {e}")
            return f"Error retrieving documents: {str(e)}"

    return Tool(
        name="retrieve_documents",
        description=(
            "Search the knowledge base for relevant information. "
            "Use this when you need to find specific information from documents. "
            "Input should be a clear search query."
        ),
        func=retrieve_documents,
    )


def get_retriever_tool(k: int = 4) -> Tool:
    """
    Get retriever tool instance.

    Args:
        k: Number of documents to retrieve

    Returns:
        Retriever tool
    """
    return create_retriever_tool(k=k)
