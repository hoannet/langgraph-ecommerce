"""TiDB Vector database connection and management."""

from typing import Optional

from tidb_vector.integrations import TiDBVectorClient

from src.core.config import get_settings
from src.core.logging import get_logger
from src.core.exceptions import LLMError

logger = get_logger(__name__)


class TiDBVector:
    """TiDB Vector connection manager."""

    client: Optional[TiDBVectorClient] = None
    table_name: str = "documents"
    embedding_dimension: int = 768
    distance_strategy: str = "cosine"

    @classmethod
    def connect(
        cls,
        connection_string: Optional[str] = None,
        table_name: Optional[str] = None,
        embedding_dimension: Optional[int] = None,
        distance_strategy: Optional[str] = None,
    ) -> None:
        """
        Connect to TiDB Vector database.

        Args:
            connection_string: TiDB connection string
            table_name: Table name for vector storage
            embedding_dimension: Vector dimension
            distance_strategy: Distance strategy (cosine, l2, inner_product)
        """
        try:
            settings = get_settings()

            # Use provided values or fall back to settings
            conn_string = connection_string or settings.tidb_connection_string
            cls.table_name = table_name or settings.tidb_table_name
            cls.embedding_dimension = embedding_dimension or settings.tidb_embedding_dimension
            cls.distance_strategy = distance_strategy or settings.tidb_distance_strategy

            if not conn_string:
                raise LLMError("TiDB connection string not configured. Set TIDB_CONNECTION_STRING in .env")

            logger.info(f"Connecting to TiDB Vector: table={cls.table_name}, dimension={cls.embedding_dimension}")

            cls.client = TiDBVectorClient(
                connection_string=conn_string,
                table_name=cls.table_name,
                distance_strategy=cls.distance_strategy,
                vector_dimension=cls.embedding_dimension,
            )

            logger.info("✅ TiDB Vector connection established")

        except Exception as e:
            logger.error(f"Failed to connect to TiDB Vector: {e}")
            raise LLMError(f"Failed to connect to TiDB Vector: {e}")

    @classmethod
    def close(cls) -> None:
        """Close TiDB Vector connection."""
        if cls.client:
            # TiDB client doesn't have explicit close method
            cls.client = None
            logger.info("TiDB Vector connection closed")

    @classmethod
    def get_client(cls) -> TiDBVectorClient:
        """
        Get TiDB Vector client instance.

        Returns:
            TiDBVectorClient instance

        Raises:
            RuntimeError: If client not initialized
        """
        if cls.client is None:
            raise RuntimeError("TiDB Vector client not initialized. Call connect() first.")
        return cls.client

    @classmethod
    def is_connected(cls) -> bool:
        """
        Check if TiDB Vector is connected.

        Returns:
            True if connected
        """
        return cls.client is not None


# Convenience function
def get_tidb_client() -> TiDBVectorClient:
    """
    Get TiDB Vector client instance.

    Returns:
        TiDBVectorClient instance
    """
    return TiDBVector.get_client()
