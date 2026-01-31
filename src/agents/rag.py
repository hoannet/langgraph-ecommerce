"""RAG Agent for knowledge base queries."""

from typing import List, Optional, Dict, Any

from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage

from src.agents.base import BaseAgent
from src.core.exceptions import AgentError
from src.core.logging import get_logger
from src.models.enums import AgentType
from src.services.llm_service import LLMService
from src.tools.retriever import create_retriever_tool
from src.services.document_service import DocumentService

logger = get_logger(__name__)


class RAGAgent(BaseAgent):
    """Agent for RAG (Retrieval-Augmented Generation) queries."""

    def __init__(
        self,
        llm_service: Optional[LLMService] = None,
        document_service: Optional[DocumentService] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Initialize RAG agent.

        Args:
            llm_service: LLM service instance
            document_service: Document service instance
            config: Agent configuration
        """
        super().__init__(
            agent_type=AgentType.FAQ,  # Use FAQ type for now
            llm_service=llm_service,
            config=config,
        )
        self.document_service = document_service or DocumentService()
        self.retriever_tool = create_retriever_tool(self.document_service)
        
        # Detect provider for optimizations
        self.provider = self.llm_service.provider
        
        # Provider-specific settings
        if self.provider == "lm_studio":
            logger.info("🔧 RAG Agent: Using LM Studio optimizations")
            self.use_llm_grading = False
            self.use_llm_rewriting = False
            self.similarity_threshold = 0.6
        else:
            logger.info(f"🔧 RAG Agent: Using {self.provider} with full features")
            self.use_llm_grading = False  # Use similarity for all providers (faster)
            self.use_llm_rewriting = True
            self.similarity_threshold = 0.6

        # Simplified system prompt (works better for all providers)
        self.system_prompt = """Answer questions using the provided context.
Be concise and accurate.
If context doesn't have the answer, say so."""

    async def process(
        self,
        messages: List[BaseMessage],
        context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Process RAG query.

        Args:
            messages: Conversation messages
            context: Additional context

        Returns:
            Response with retrieved information
        """
        if not messages:
            raise AgentError("No messages provided for RAG processing")

        user_message = messages[-1].content
        logger.info(f"Processing RAG query: {user_message[:100]}...")

        try:
            # Step 1: Retrieve relevant documents
            retrieved_docs = await self.retriever_tool.func(user_message)

            # Step 2: Generate answer using retrieved context
            if "No relevant documents found" in retrieved_docs or "Error" in retrieved_docs:
                # No relevant documents found
                response = await self._generate_fallback_response(user_message)
            else:
                # Generate answer with context
                response = await self._generate_answer_with_context(
                    query=user_message,
                    context=retrieved_docs,
                )

            return response

        except Exception as e:
            logger.error(f"RAG processing failed: {e}")
            return f"I encountered an error while searching the knowledge base: {str(e)}"

    async def _generate_answer_with_context(
        self,
        query: str,
        context: str,
    ) -> str:
        """
        Generate answer using retrieved context.

        Args:
            query: User query
            context: Retrieved document context

        Returns:
            Generated answer
        """
        prompt_messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=f"""Based on the following context from the knowledge base, answer the question.

Context:
{context}

Question: {query}

Answer based on the context above. If the context doesn't contain enough information, say so."""),
        ]

        response = await self.llm.ainvoke(prompt_messages)
        return response.content

    async def _generate_fallback_response(self, query: str) -> str:
        """
        Generate fallback response when no documents found.

        Args:
            query: User query

        Returns:
            Fallback response
        """
        return (
            f"I couldn't find relevant information in the knowledge base for: '{query}'\n\n"
            "This might mean:\n"
            "- The information hasn't been added to the knowledge base yet\n"
            "- Try rephrasing your question\n"
            "- Contact support for more specific assistance"
        )

    def _extract_scores(self, documents: str) -> List[float]:
        """
        Extract similarity scores from formatted documents.
        
        Args:
            documents: Formatted document string
            
        Returns:
            List of similarity scores
        """
        import re
        scores = []
        # Parse "[Document N] (Source: X, Relevance: 0.XXX)"
        pattern = r'Relevance:\s*([\d.]+)'
        matches = re.findall(pattern, documents)
        scores = [float(m) for m in matches]
        return scores

    async def grade_documents(
        self,
        query: str,
        documents: str,
    ) -> bool:
        """
        Grade documents using similarity scores (provider-agnostic).

        Args:
            query: User query
            documents: Retrieved documents

        Returns:
            True if relevant, False otherwise
        """
        try:
            # Extract similarity scores from documents
            scores = self._extract_scores(documents)
            
            if not scores:
                logger.warning("No scores found in documents, defaulting to relevant")
                return True
            
            # Calculate average similarity
            avg_score = sum(scores) / len(scores)
            
            # Threshold-based decision
            is_relevant = avg_score >= self.similarity_threshold
            
            logger.info(
                f"📊 Document grading: avg_score={avg_score:.3f}, "
                f"threshold={self.similarity_threshold}, relevant={is_relevant}, "
                f"scores={[f'{s:.3f}' for s in scores]}"
            )
            return is_relevant

        except Exception as e:
            logger.error(f"Similarity-based grading failed: {e}")
            return True  # Default to relevant on error

    async def rewrite_question(self, query: str) -> str:
        """
        Rewrite question for better retrieval (provider-aware).

        Args:
            query: Original query

        Returns:
            Rewritten query
        """
        # Skip rewriting for LM Studio (not reliable)
        if not self.use_llm_rewriting:
            logger.info(f"⏭️  Skipping question rewrite for {self.provider}")
            return query
        
        try:
            # Simplified prompt for better results
            prompt_messages = [
                SystemMessage(content="Rephrase questions for better search."),
                HumanMessage(content=f"Rephrase for search: {query}\nBetter version:"),
            ]

            response = await self.llm.ainvoke(prompt_messages)
            rewritten = response.content.strip()

            logger.info(f"✏️  Rewritten question: '{query}' -> '{rewritten}'")
            return rewritten

        except Exception as e:
            logger.error(f"Question rewriting failed: {e}")
            return query  # Return original on error


def get_rag_agent() -> RAGAgent:
    """Get RAG agent instance."""
    return RAGAgent()
