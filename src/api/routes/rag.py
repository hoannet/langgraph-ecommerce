"""RAG (Retrieval-Augmented Generation) API routes."""

import os
from typing import List, Optional
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from pydantic import BaseModel

from src.core.logging import get_logger
from src.core.config import get_settings
from src.services.document_service import DocumentService
from src.graphs.rag_workflow import get_rag_workflow
from langchain_core.messages import HumanMessage, AIMessage

logger = get_logger(__name__)

router = APIRouter(prefix="/rag", tags=["rag"])


class QueryRequest(BaseModel):
    """RAG query request."""
    query: str
    k: Optional[int] = 4


class VectorSearchRequest(BaseModel):
    """Vector search request."""
    query: str
    k: Optional[int] = 4
    threshold: Optional[float] = 0.0


class VectorSearchResponse(BaseModel):
    """Vector search response."""
    query: str
    results: List[dict]
    count: int


class QueryResponse(BaseModel):
    """RAG query response."""
    answer: str
    sources: List[str] = []


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    metadata: Optional[str] = Form(None),
):
    """
    Upload and index a document.

    Args:
        file: Document file (PDF, TXT, MD, DOCX)
        metadata: Optional JSON metadata

    Returns:
        Indexing result
    """
    logger.info(f"Uploading document: {file.filename}")

    try:
        # Validate file type
        allowed_extensions = {".pdf", ".txt", ".md", ".docx", ".doc"}
        file_ext = Path(file.filename).suffix.lower()

        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: {file_ext}. Allowed: {allowed_extensions}"
            )

        # Save uploaded file
        upload_dir = Path("data/uploads")
        upload_dir.mkdir(parents=True, exist_ok=True)

        file_path = upload_dir / file.filename
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        # Parse metadata
        import json
        meta_dict = {}
        if metadata:
            try:
                meta_dict = json.loads(metadata)
            except json.JSONDecodeError:
                logger.warning(f"Invalid metadata JSON: {metadata}")

        # Index document
        doc_service = DocumentService()
        result = await doc_service.index_document(
            file_path=str(file_path),
            metadata=meta_dict,
        )

        return {
            "status": "success",
            "message": f"Document '{file.filename}' indexed successfully",
            **result,
        }

    except Exception as e:
        logger.error(f"Failed to upload document: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.post("/query", response_model=QueryResponse)
async def query_knowledge_base(request: QueryRequest):
    """
    Query the knowledge base using RAG.
    
    Automatically detects LLM provider and routes to:
    - Agentic RAG (with function calling) for OpenAI/Gemini
    - Manual RAG (without function calling) for LM Studio

    Args:
        request: Query request

    Returns:
        Answer with sources
    """
    try:
        logger.info(f"RAG query: {request.query}")
        
        # Detect provider
        settings = get_settings()
        llm_provider = settings.llm_provider
        
        # Choose workflow based on provider
        if llm_provider in ["openai", "gemini"]:
            logger.info(f"🔧 Using agentic RAG workflow (provider={llm_provider})")
            from src.graphs.rag_workflow import get_rag_workflow
            workflow = get_rag_workflow()
        else:
            logger.info(f"🔧 Using manual RAG workflow (provider={llm_provider})")
            from src.graphs.manual_rag_workflow import get_manual_rag_workflow
            workflow = get_manual_rag_workflow()

        # Create initial state
        initial_state = {
            "messages": [HumanMessage(content=request.query)],
            "retry_count": 0,
        }

        # Run workflow
        result = await workflow.ainvoke(initial_state)

        # Extract answer
        messages = result.get("messages", [])
        if not messages:
            raise HTTPException(status_code=500, detail="No response from RAG workflow")

        # Get last AI message
        ai_messages = [m for m in messages if isinstance(m, AIMessage)]
        if not ai_messages:
            raise HTTPException(status_code=500, detail="No AI response in workflow")

        answer = ai_messages[-1].content

        # Extract sources from tool messages
        from langchain_core.messages import ToolMessage
        tool_messages = [m for m in messages if isinstance(m, ToolMessage)]
        sources = []
        if tool_messages:
            # Parse sources from tool message content
            content = tool_messages[-1].content
            # Simple extraction - you can improve this
            sources = ["Knowledge Base"]

        return QueryResponse(
            query=request.query,
            answer=answer,
            sources=sources,
        )

    except Exception as e:
        logger.error(f"RAG query failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")


@router.get("/documents")
async def list_documents():
    """
    List uploaded documents.

    Returns:
        List of documents
    """
    try:
        upload_dir = Path("data/uploads")
        if not upload_dir.exists():
            return {"documents": []}

        documents = []
        for file_path in upload_dir.iterdir():
            if file_path.is_file():
                documents.append({
                    "filename": file_path.name,
                    "size": file_path.stat().st_size,
                    "uploaded_at": file_path.stat().st_mtime,
                })

        return {"documents": documents}

    except Exception as e:
        logger.error(f"Failed to list documents: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list documents: {str(e)}")


@router.delete("/documents/{filename}")
async def delete_document(filename: str):
    """
    Delete a document.

    Args:
        filename: Document filename

    Returns:
        Deletion result
    """
    try:
        upload_dir = Path("data/uploads")
        file_path = upload_dir / filename

        if not file_path.exists():
            raise HTTPException(status_code=404, detail=f"Document not found: {filename}")

        # Delete file
        file_path.unlink()

        # TODO: Delete from vector store
        # This requires tracking document IDs

        return {
            "status": "success",
            "message": f"Document '{filename}' deleted successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete document: {e}")
        raise HTTPException(status_code=500, detail=f"Deletion failed: {str(e)}")


@router.post("/search", response_model=VectorSearchResponse)
async def search_vectors(request: VectorSearchRequest):
    """
    Search vector database directly (without RAG workflow).
    
    Args:
        request: Vector search request with query, k, and threshold
        
    Returns:
        Search results with similarity scores
    """
    logger.info(f"Vector search: query='{request.query}', k={request.k}, threshold={request.threshold}")
    
    try:
        # Search documents
        doc_service = DocumentService()
        documents = await doc_service.search_documents(
            query=request.query,
            k=request.k
        )
        
        # Format results
        results = []
        for doc in documents:
            score = doc.metadata.get("score", 0.0)
            
            # Filter by threshold
            if score < request.threshold:
                continue
                
            results.append({
                "content": doc.page_content,
                "score": score,
                "source": doc.metadata.get("source", "Unknown"),
                "metadata": {
                    k: v for k, v in doc.metadata.items() 
                    if k not in ["score", "source"]
                }
            })
        
        logger.info(f"Found {len(results)} results (filtered by threshold={request.threshold})")
        
        return VectorSearchResponse(
            query=request.query,
            results=results,
            count=len(results)
        )
        
    except Exception as e:
        logger.error(f"Vector search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")
