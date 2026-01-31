"""Agentic RAG workflow with LangGraph."""

from typing import Literal, TypedDict, Annotated
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.graph.message import add_messages

from src.core.logging import get_logger
from src.services.llm_service import LLMService
from src.tools.retriever import get_retriever_tool
from src.agents.rag import RAGAgent

logger = get_logger(__name__)


class MessagesState(TypedDict):
    """State for RAG workflow."""
    messages: Annotated[list[BaseMessage], add_messages]
    retry_count: int  # Track number of question rewrites


def create_rag_workflow():
    """
    Create agentic RAG workflow with LangGraph.

    Workflow:
    1. Generate query or respond directly
    2. If tool call needed, retrieve documents
    3. Grade documents for relevance
    4. If not relevant, rewrite question and retry (max 3 times)
    5. If relevant, generate final answer

    Returns:
        Compiled LangGraph workflow
    """
    # Initialize components
    llm_service = LLMService()
    llm = llm_service.llm
    rag_agent = RAGAgent(llm_service=llm_service)
    retriever_tool = get_retriever_tool()
    
    # Log provider configuration
    from src.core.config import get_settings
    settings = get_settings()
    logger.info(
        f"🔧 RAG Workflow initialized: "
        f"LLM={settings.llm_provider} ({settings.llm_provider}), "
        f"Embeddings={settings.embedding_provider}, "
        f"Top-K={settings.tidb_search_top_k}"
    )

    # Bind tools to LLM
    llm_with_tools = llm.bind_tools([retriever_tool])
    
    # Max retry attempts
    MAX_RETRIES = 3

    # Node: Generate query or respond
    async def generate_query_or_respond(state: MessagesState):
        """Generate search query or respond directly."""
        messages = state["messages"]
        response = await llm_with_tools.ainvoke(messages)
        logger.info(f"Generated query/response: {response}")
        return {"messages": [response]}

    # Node: Grade documents
    async def grade_documents(state: MessagesState) -> Literal["generate_answer", "rewrite_question", "no_answer"]:
        """Grade if retrieved documents are relevant."""
        messages = state["messages"]
        retry_count = state.get("retry_count", 0)
        
        # Get tool messages
        tool_messages = [m for m in messages if isinstance(m, ToolMessage)]
        
        # Check if no documents retrieved
        if not tool_messages:
            logger.warning("❌ No tool messages found, cannot answer")
            return "no_answer"
        
        retrieved_docs = tool_messages[-1].content
        
        # Check if retrieval failed or no documents found
        if "No relevant documents found" in retrieved_docs or "Error" in retrieved_docs:
            logger.warning("❌ No documents found in retrieval")
            return "no_answer"
        
        # Check max retries
        if retry_count >= MAX_RETRIES:
            logger.warning(f"❌ Max retries ({MAX_RETRIES}) reached, cannot answer")
            return "no_answer"
        
        # Get original query
        human_messages = [m for m in messages if isinstance(m, HumanMessage)]
        if not human_messages:
            return "no_answer"
        
        query = human_messages[-1].content
        
        # Grade documents
        is_relevant = await rag_agent.grade_documents(query, retrieved_docs)
        
        if is_relevant:
            logger.info("✅ Documents relevant, generating answer")
            return "generate_answer"
        else:
            logger.info(f"⚠️  Documents not relevant (retry {retry_count + 1}/{MAX_RETRIES})")
            return "rewrite_question"

    # Node: Rewrite question
    async def rewrite_question(state: MessagesState):
        """Rewrite question for better retrieval."""
        messages = state["messages"]
        retry_count = state.get("retry_count", 0)

        # Get original query
        human_messages = [m for m in messages if isinstance(m, HumanMessage)]
        if not human_messages:
            return {"messages": [], "retry_count": retry_count}

        original_query = human_messages[-1].content

        # Rewrite
        rewritten_query = await rag_agent.rewrite_question(original_query)

        logger.info(f"Rewritten question (attempt {retry_count + 1}): {rewritten_query}")

        # Replace last human message with rewritten query
        new_messages = messages[:-1] + [HumanMessage(content=rewritten_query)]
        
        # Increment retry count
        return {"messages": new_messages, "retry_count": retry_count + 1}

    # Node: No answer available
    async def no_answer_available(state: MessagesState):
        """Return message when cannot answer based on documents."""
        messages = state["messages"]
        retry_count = state.get("retry_count", 0)
        
        # Get original query
        human_messages = [m for m in messages if isinstance(m, HumanMessage)]
        query = human_messages[-1].content if human_messages else "câu hỏi này"
        
        # Check reason
        tool_messages = [m for m in messages if isinstance(m, ToolMessage)]
        
        if not tool_messages or "No relevant documents found" in tool_messages[-1].content:
            # No documents found at all
            message = (
                f"❌ Xin lỗi, tôi không tìm thấy thông tin về **'{query}'** "
                "trong knowledge base.\n\n"
                "**Có thể**:\n"
                "- Thông tin chưa được thêm vào hệ thống\n"
                "- Thử diễn đạt câu hỏi khác\n"
                "- Liên hệ support để được hỗ trợ"
            )
        elif retry_count >= MAX_RETRIES:
            # Documents found but not relevant after retries
            message = (
                f"❌ Xin lỗi, tôi không tìm thấy thông tin **relevant** về '{query}' "
                f"sau {MAX_RETRIES} lần thử.\n\n"
                "**Gợi ý**:\n"
                "- Thử câu hỏi cụ thể hơn\n"
                "- Sử dụng từ khóa khác\n"
                "- Liên hệ support"
            )
        else:
            # Generic no answer
            message = (
                f"❌ Xin lỗi, tôi không thể trả lời câu hỏi '{query}' "
                "dựa trên knowledge base hiện tại."
            )
        
        logger.warning(f"No answer available: {query} (retry_count={retry_count})")
        return {"messages": [AIMessage(content=message)]}
    
    # Node: Generate answer
    async def generate_answer(state: MessagesState):
        """Generate final answer using retrieved context."""
        messages = state["messages"]

        # Generate answer with context
        response = await llm.ainvoke(messages)
        logger.info("✅ Generated final answer with context")
        return {"messages": [response]}

    # Build workflow graph
    workflow = StateGraph(MessagesState)

    # Add nodes
    workflow.add_node("generate_query_or_respond", generate_query_or_respond)
    workflow.add_node("retrieve", ToolNode([retriever_tool]))
    workflow.add_node("rewrite_question", rewrite_question)
    workflow.add_node("no_answer_available", no_answer_available)
    workflow.add_node("generate_answer", generate_answer)

    # Add edges
    workflow.add_edge(START, "generate_query_or_respond")

    # Conditional edge: decide whether to retrieve or respond
    workflow.add_conditional_edges(
        "generate_query_or_respond",
        tools_condition,
        {
            "tools": "retrieve",
            END: END,
        },
    )

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

    # Edge: after rewriting, try again
    workflow.add_edge("rewrite_question", "generate_query_or_respond")

    # Compile
    graph = workflow.compile()
    logger.info("Compiled agentic RAG workflow with retry limit")

    return graph


def get_rag_workflow():
    """Get compiled RAG workflow."""
    return create_rag_workflow()
