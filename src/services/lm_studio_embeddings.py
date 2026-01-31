"""Custom embeddings for LM Studio."""

from typing import List
import httpx
from langchain_core.embeddings import Embeddings

from src.core.config import get_settings
from src.core.logging import get_logger

logger = get_logger(__name__)


class LMStudioEmbeddings(Embeddings):
    """LM Studio embeddings using OpenAI-compatible API."""

    def __init__(
        self,
        model: str,
        base_url: str,
        api_key: str = "not-needed",
    ):
        """
        Initialize LM Studio embeddings.

        Args:
            model: Model name
            base_url: LM Studio base URL
            api_key: API key (not needed for local LM Studio)
        """
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.embeddings_url = f"{self.base_url}/embeddings"

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Embed documents.

        Args:
            texts: List of texts to embed

        Returns:
            List of embeddings
        """
        embeddings = []
        
        # Process each text individually to avoid batch issues
        for text in texts:
            embedding = self._embed_single(text)
            embeddings.append(embedding)
        
        return embeddings

    def embed_query(self, text: str) -> List[float]:
        """
        Embed query.

        Args:
            text: Query text

        Returns:
            Embedding vector
        """
        return self._embed_single(text)

    def _embed_single(self, text: str) -> List[float]:
        """
        Embed single text.

        Args:
            text: Text to embed

        Returns:
            Embedding vector
        """
        try:
            # Make request to LM Studio
            response = httpx.post(
                self.embeddings_url,
                json={
                    "model": self.model,
                    "input": text,  # Single string, not array
                },
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                timeout=30.0,
            )
            
            response.raise_for_status()
            data = response.json()
            
            # Extract embedding from response
            if "data" in data and len(data["data"]) > 0:
                return data["data"][0]["embedding"]
            else:
                raise ValueError(f"Invalid response format: {data}")
                
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            raise

    async def aembed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Async embed documents.

        Args:
            texts: List of texts to embed

        Returns:
            List of embeddings
        """
        embeddings = []
        
        # Process each text individually
        for text in texts:
            embedding = await self._aembed_single(text)
            embeddings.append(embedding)
        
        return embeddings

    async def aembed_query(self, text: str) -> List[float]:
        """
        Async embed query.

        Args:
            text: Query text

        Returns:
            Embedding vector
        """
        return await self._aembed_single(text)

    async def _aembed_single(self, text: str) -> List[float]:
        """
        Async embed single text.

        Args:
            text: Text to embed

        Returns:
            Embedding vector
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.embeddings_url,
                    json={
                        "model": self.model,
                        "input": text,  # Single string
                    },
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    timeout=30.0,
                )
                
                response.raise_for_status()
                data = response.json()
                
                # Extract embedding
                if "data" in data and len(data["data"]) > 0:
                    return data["data"][0]["embedding"]
                else:
                    raise ValueError(f"Invalid response format: {data}")
                    
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            raise


def get_lm_studio_embeddings() -> LMStudioEmbeddings:
    """Get LM Studio embeddings instance."""
    settings = get_settings()
    return LMStudioEmbeddings(
        model=settings.lm_studio_embedding_model,
        base_url=settings.lm_studio_base_url,
        api_key=settings.lm_studio_api_key,
    )
