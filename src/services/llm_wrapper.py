"""LLM wrapper to automatically track calls."""

from typing import Any
import time


class TrackedLLMWrapper:
    """Wrapper that automatically tracks all LLM calls."""
    
    def __init__(self, llm, llm_service):
        self._llm = llm
        self._service = llm_service
    
    def __getattr__(self, name):
        """Delegate all other attributes to wrapped LLM."""
        return getattr(self._llm, name)
    
    async def ainvoke(self, *args, **kwargs):
        """Tracked async invoke."""
        from src.services.llm_service import _llm_call_count, _llm_total_tokens
        import src.services.llm_service as llm_module
        
        start_time = time.time()
        self._service.call_count += 1
        llm_module._llm_call_count += 1
        
        try:
            response = await self._llm.ainvoke(*args, **kwargs)
            
            # Track tokens
            if hasattr(response, 'response_metadata'):
                usage = response.response_metadata.get('token_usage', {})
                tokens = usage.get('total_tokens', 0)
                if tokens:
                    self._service.total_tokens += tokens
                    llm_module._llm_total_tokens += tokens
            
            elapsed = time.time() - start_time
            
            from src.core.logging import get_logger
            logger = get_logger(__name__)
            
            logger.info(
                f"🔥 LLM Call #{self._service.call_count} (Global: #{llm_module._llm_call_count}) | "
                f"Provider: {self._service.provider} | Model: {self._service.model_name} | "
                f"Time: {elapsed:.2f}s"
            )
            
            if hasattr(response, 'response_metadata'):
                usage = response.response_metadata.get('token_usage', {})
                if usage:
                    logger.info(
                        f"📊 Tokens - Prompt: {usage.get('prompt_tokens', 0)}, "
                        f"Completion: {usage.get('completion_tokens', 0)}, "
                        f"Total: {usage.get('total_tokens', 0)}"
                    )
            
            return response
            
        except Exception as e:
            from src.core.logging import get_logger
            logger = get_logger(__name__)
            logger.error(f"❌ LLM call failed: {e}")
            raise
    
    def invoke(self, *args, **kwargs):
        """Tracked sync invoke."""
        from src.services.llm_service import _llm_call_count, _llm_total_tokens
        import src.services.llm_service as llm_module
        
        start_time = time.time()
        self._service.call_count += 1
        llm_module._llm_call_count += 1
        
        try:
            response = self._llm.invoke(*args, **kwargs)
            
            # Track tokens
            if hasattr(response, 'response_metadata'):
                usage = response.response_metadata.get('token_usage', {})
                tokens = usage.get('total_tokens', 0)
                if tokens:
                    self._service.total_tokens += tokens
                    llm_module._llm_total_tokens += tokens
            
            elapsed = time.time() - start_time
            
            from src.core.logging import get_logger
            logger = get_logger(__name__)
            
            logger.info(
                f"🔥 LLM Call #{self._service.call_count} (Global: #{llm_module._llm_call_count}) | "
                f"Provider: {self._service.provider} | Model: {self._service.model_name} | "
                f"Time: {elapsed:.2f}s"
            )
            
            return response
            
        except Exception as e:
            from src.core.logging import get_logger
            logger = get_logger(__name__)
            logger.error(f"❌ LLM call failed: {e}")
            raise
