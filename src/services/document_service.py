"""Document processing service for RAG."""

import os
from typing import List, Optional
from pathlib import Path

from langchain_core.documents import Document
from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    UnstructuredMarkdownLoader,
    Docx2txtLoader,
)
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.core.logging import get_logger
from src.core.exceptions import LLMError
from src.services.vector_store import TiDBVectorStore

logger = get_logger(__name__)


class DocumentService:
    """Service for document processing and indexing."""

    def __init__(
        self,
        vector_store: Optional[TiDBVectorStore] = None,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
    ) -> None:
        """
        Initialize document service.

        Args:
            vector_store: TiDB vector store instance
            chunk_size: Size of text chunks
            chunk_overlap: Overlap between chunks
        """
        self.vector_store = vector_store or TiDBVectorStore()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""],
        )
        logger.info(f"Initialized DocumentService with chunk_size={chunk_size}")

    async def load_document(self, file_path: str) -> List[Document]:
        """
        Load document from file.

        Args:
            file_path: Path to document file

        Returns:
            List of loaded documents

        Raises:
            LLMError: If file type not supported or loading fails
        """
        try:
            file_ext = Path(file_path).suffix.lower()

            # Select appropriate loader
            if file_ext == ".pdf":
                loader = PyPDFLoader(file_path)
            elif file_ext == ".txt":
                loader = TextLoader(file_path)
            elif file_ext == ".md":
                loader = UnstructuredMarkdownLoader(file_path)
            elif file_ext in [".docx", ".doc"]:
                loader = Docx2txtLoader(file_path)
            else:
                raise LLMError(f"Unsupported file type: {file_ext}")

            # Load documents
            documents = loader.load()
            logger.info(f"Loaded {len(documents)} pages from {file_path}")
            return documents

        except Exception as e:
            logger.error(f"Failed to load document {file_path}: {e}")
            raise LLMError(f"Failed to load document: {e}")

    async def split_documents(self, documents: List[Document]) -> List[Document]:
        """
        Split documents into chunks.

        Args:
            documents: List of documents to split

        Returns:
            List of document chunks
        """
        try:
            chunks = self.text_splitter.split_documents(documents)
            logger.info(f"Split {len(documents)} documents into {len(chunks)} chunks")
            return chunks

        except Exception as e:
            logger.error(f"Failed to split documents: {e}")
            raise LLMError(f"Failed to split documents: {e}")

    async def index_document(
        self,
        file_path: str,
        metadata: Optional[dict] = None,
    ) -> dict:
        """
        Load, split, and index a document.

        Args:
            file_path: Path to document file
            metadata: Additional metadata to attach

        Returns:
            Indexing result with document IDs and stats
        """
        try:
            # Load document
            documents = await self.load_document(file_path)

            # Add metadata
            if metadata:
                for doc in documents:
                    doc.metadata.update(metadata)

            # Add file info to metadata
            file_name = Path(file_path).name
            for doc in documents:
                doc.metadata.update({
                    "source": file_name,
                    "file_path": file_path,
                })

            # Split into chunks
            chunks = await self.split_documents(documents)

            # Index in vector store
            doc_ids = await self.vector_store.add_documents(chunks)

            result = {
                "file_name": file_name,
                "num_pages": len(documents),
                "num_chunks": len(chunks),
                "doc_ids": doc_ids,
                "status": "success",
            }

            logger.info(f"Indexed document: {file_name} ({len(chunks)} chunks)")
            return result

        except Exception as e:
            logger.error(f"Failed to index document {file_path}: {e}")
            raise LLMError(f"Failed to index document: {e}")

    async def search_documents(
        self,
        query: str,
        k: int = 4,
        filter: Optional[dict] = None,
    ) -> List[Document]:
        """
        Search for relevant documents.

        Args:
            query: Search query
            k: Number of results
            filter: Metadata filter

        Returns:
            List of relevant documents
        """
        try:
            documents = await self.vector_store.similarity_search(
                query=query,
                k=k,
                filter=filter,
            )
            logger.info(f"Found {len(documents)} documents for query: {query[:50]}...")
            return documents

        except Exception as e:
            logger.error(f"Failed to search documents: {e}")
            raise LLMError(f"Failed to search documents: {e}")

    async def delete_document(self, doc_ids: List[str]) -> bool:
        """
        Delete documents by IDs.

        Args:
            doc_ids: List of document IDs

        Returns:
            True if successful
        """
        try:
            success = await self.vector_store.delete_documents(doc_ids)
            if success:
                logger.info(f"Deleted {len(doc_ids)} documents")
            return success

        except Exception as e:
            logger.error(f"Failed to delete documents: {e}")
            return False


def get_document_service() -> DocumentService:
    """Get document service instance."""
    return DocumentService()
