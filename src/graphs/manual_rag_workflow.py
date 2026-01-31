"""Manual RAG workflow for providers without function calling support (e.g., LM Studio)."""

from typing import Literal, TypedDict, Annotated, List
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_core.documents import Document
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

from src.core.logging import get_logger
from src.services.llm_service import LLMService
from src.services.document_service import DocumentService
from src.agents.rag import RAGAgent

logger = get_logger(__name__)


class ManualRAGState(TypedDict):
    """State for manual RAG workflow."""
    messages: Annotated[list[BaseMessage], add_messages]
    retry_count: int
    documents: List[Document]


def format_documents(documents: List[Document]) -> str:
    """
    Format documents for context injection.
    
    Args:
        documents: List of retrieved documents
        
    Returns:
        Formatted context string
    """
    if not documents:
        return "No relevant documents found."
    
    formatted = []
    for i, doc in enumerate(documents, 1):
        score = doc.metadata.get("score", 0)
        source = doc.metadata.get("source", "Unknown")
        formatted.append(
            f"[Document {i}] (Source: {source}, Relevance: {score:.3f})\n"
            f"{doc.page_content}\n"
        )
    return "\n".join(formatted)


async def grade_documents_by_score(documents: List[Document], threshold: float = 0.6) -> bool:
    """
    Grade documents using similarity scores.
    
    Args:
        documents: List of documents to grade
        threshold: Minimum average score threshold
        
    Returns:
        True if documents are relevant
    """
    if not documents:
        return False
    
    scores = [doc.metadata.get("score", 0) for doc in documents]
    avg_score = sum(scores) / len(scores)
    
    logger.info(f"📊 Document grading: avg_score={avg_score:.3f}, threshold={threshold}, relevant={avg_score >= threshold}")
    return avg_score >= threshold


def create_manual_rag_workflow():
    """
    Create manual RAG workflow without function calling.
    
    This workflow is designed for LLM providers that don't support
    function calling (e.g., LM Studio). It manually retrieves documents
    and injects them as context into the prompt.
    
    Returns:
        Compiled LangGraph workflow
    """
    # Initialize components
    llm_service = LLMService()
    llm = llm_service.llm
    rag_agent = RAGAgent(llm_service=llm_service)
    
    # Configuration
    from src.core.config import get_settings
    settings = get_settings()
    MAX_RETRIES = 3
    SIMILARITY_THRESHOLD = settings.rag_similarity_threshold
    
    logger.info(
        f"🔧 Manual RAG Workflow initialized: "
        f"LLM={settings.llm_provider}, "
        f"Embeddings={settings.embedding_provider}, "
        f"Top-K={settings.tidb_search_top_k}, "
        f"Threshold={SIMILARITY_THRESHOLD}"
    )
    
    # Node: Retrieve documents
    async def retrieve_documents(state: ManualRAGState):
        """Retrieve documents from knowledge base."""
        messages = state["messages"]
        query = messages[-1].content
        
        logger.info(f"🔍 Retrieving documents for query: {query[:50]}...")
        
        # Retrieve
        doc_service = DocumentService()
        documents = await doc_service.search_documents(
            query=query,
            k=settings.tidb_search_top_k
        )
        
        logger.info(f"📚 Retrieved {len(documents)} documents")
        return {"documents": documents}
    
    # Node: Grade documents
    async def grade_documents(state: ManualRAGState) -> Literal["generate_answer", "rewrite_question", "no_answer"]:
        """Grade retrieved documents."""
        documents = state.get("documents", [])
        retry_count = state.get("retry_count", 0)
        
        # Check if no documents
        if not documents:
            logger.warning("❌ No documents retrieved")
            return "no_answer"
        
        # Check max retries
        if retry_count >= MAX_RETRIES:
            logger.warning(f"❌ Max retries ({MAX_RETRIES}) reached")
            return "no_answer"
        
        # Grade by similarity scores
        is_relevant = await grade_documents_by_score(documents, SIMILARITY_THRESHOLD)
        
        if is_relevant:
            logger.info("✅ Documents relevant, generating answer")
            return "generate_answer"
        else:
            logger.info(f"⚠️  Documents not relevant (retry {retry_count + 1}/{MAX_RETRIES})")
            return "rewrite_question"
    
    # Node: Rewrite question
    async def rewrite_question(state: ManualRAGState):
        """Rewrite question for better retrieval."""
        messages = state["messages"]
        retry_count = state.get("retry_count", 0)
        
        # Get original query
        query = messages[-1].content
        
        # Rewrite
        rewritten_query = await rag_agent.rewrite_question(query)
        logger.info(f"✏️  Rewritten question (attempt {retry_count + 1}): {rewritten_query}")
        
        # Replace last message
        new_messages = messages[:-1] + [HumanMessage(content=rewritten_query)]
        
        return {"messages": new_messages, "retry_count": retry_count + 1}
    
    # Node: No answer available
    async def no_answer_available(state: ManualRAGState):
        """Return message when cannot answer."""
        messages = state["messages"]
        retry_count = state.get("retry_count", 0)
        documents = state.get("documents", [])
        
        query = messages[-1].content if messages else "câu hỏi này"
        
        if not documents:
            message = (
                f"❌ Xin lỗi, tôi không tìm thấy thông tin về **'{query}'** "
                "trong knowledge base.\n\n"
                "**Có thể**:\n"
                "- Thông tin chưa được thêm vào hệ thống\n"
                "- Thử diễn đạt câu hỏi khác\n"
                "- Liên hệ support để được hỗ trợ"
            )
        elif retry_count >= MAX_RETRIES:
            message = (
                f"❌ Xin lỗi, tôi không tìm thấy thông tin **relevant** về '{query}' "
                f"sau {MAX_RETRIES} lần thử.\n\n"
                "**Gợi ý**:\n"
                "- Thử câu hỏi cụ thể hơn\n"
                "- Sử dụng từ khóa khác\n"
                "- Liên hệ support"
            )
        else:
            message = (
                f"❌ Xin lỗi, tôi không thể trả lời câu hỏi '{query}' "
                "dựa trên knowledge base hiện tại."
            )
        
        logger.warning(f"No answer available: {query} (retry_count={retry_count})")
        return {"messages": [AIMessage(content=message)]}
    
    # Node: Generate answer
    async def generate_answer(state: ManualRAGState):
        """Generate answer with context injection."""
        messages = state["messages"]
        documents = state.get("documents", [])
        
        query = messages[-1].content
        
        # Format context
        context = format_documents(documents)
        
        # Create prompt with context
        prompt = f"""Dựa trên thông tin từ knowledge base dưới đây, hãy trả lời câu hỏi.

{context}

Câu hỏi: {query}

Hãy trả lời dựa trên context trên. Nếu context không có thông tin liên quan, hãy nói rõ."""
        
        # Generate answer
        logger.info("🤖 Generating answer with injected context...")
        response = await llm.ainvoke([HumanMessage(content=prompt)])
        
        logger.info("✅ Generated answer")
        return {"messages": [response]}
    
    # Build workflow graph
    workflow = StateGraph(ManualRAGState)
    
    # Add nodes
    workflow.add_node("retrieve", retrieve_documents)
    workflow.add_node("rewrite_question", rewrite_question)
    workflow.add_node("no_answer_available", no_answer_available)
    workflow.add_node("generate_answer", generate_answer)
    
    # Add edges
    workflow.add_edge(START, "retrieve")
    
    # Conditional edge: grade documents
    workflow.add_conditional_edges(
        "retrieve",
        grade_documents,
        {
            "generate_answer": "generate_answer",
            "rewrite_question": "rewrite_question",
            "no_answer": "no_answer_available",
        },
    )
    
    # Edge: after generating answer, end
    workflow.add_edge("generate_answer", END)
    
    # Edge: after no answer, end
    workflow.add_edge("no_answer_available", END)
    
    # Edge: after rewriting, retrieve again
    workflow.add_edge("rewrite_question", "retrieve")
    
    # Compile
    graph = workflow.compile()
    logger.info("✅ Compiled manual RAG workflow")
    
    return graph


def get_manual_rag_workflow():
    """Get compiled manual RAG workflow."""
    return create_manual_rag_workflow()
