"""Checkpoint management for graph state persistence."""

import json
from pathlib import Path
from typing import Any, Dict, Optional

from langgraph.checkpoint.base import BaseCheckpointSaver, Checkpoint
from langgraph.checkpoint.memory import MemorySaver

from src.core.config import get_settings
from src.core.logging import get_logger

logger = get_logger(__name__)


class FileCheckpointSaver(BaseCheckpointSaver):
    """File-based checkpoint saver for persisting graph state."""

    def __init__(self, checkpoint_dir: Optional[Path] = None) -> None:
        """
        Initialize file checkpoint saver.

        Args:
            checkpoint_dir: Directory for checkpoint files
        """
        settings = get_settings()
        self.checkpoint_dir = checkpoint_dir or settings.checkpoint_dir
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Initialized FileCheckpointSaver at {self.checkpoint_dir}")

    def _get_checkpoint_path(self, thread_id: str, checkpoint_id: str) -> Path:
        """Get path for a checkpoint file."""
        return self.checkpoint_dir / f"{thread_id}_{checkpoint_id}.json"

    def put(
        self,
        config: Dict[str, Any],
        checkpoint: Checkpoint,
        metadata: Dict[str, Any],
    ) -> None:
        """
        Save a checkpoint.

        Args:
            config: Configuration dict
            checkpoint: Checkpoint to save
            metadata: Checkpoint metadata
        """
        thread_id = config.get("configurable", {}).get("thread_id", "default")
        checkpoint_id = checkpoint.get("id", "latest")

        checkpoint_path = self._get_checkpoint_path(thread_id, checkpoint_id)

        data = {
            "config": config,
            "checkpoint": checkpoint,
            "metadata": metadata,
        }

        try:
            with open(checkpoint_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, default=str)
            logger.debug(f"Saved checkpoint: {checkpoint_path}")
        except Exception as e:
            logger.error(f"Failed to save checkpoint: {e}")

    def get(
        self,
        config: Dict[str, Any],
    ) -> Optional[tuple[Checkpoint, Dict[str, Any]]]:
        """
        Load a checkpoint.

        Args:
            config: Configuration dict

        Returns:
            Tuple of (checkpoint, metadata) or None
        """
        thread_id = config.get("configurable", {}).get("thread_id", "default")
        checkpoint_id = "latest"

        checkpoint_path = self._get_checkpoint_path(thread_id, checkpoint_id)

        if not checkpoint_path.exists():
            logger.debug(f"No checkpoint found: {checkpoint_path}")
            return None

        try:
            with open(checkpoint_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            logger.debug(f"Loaded checkpoint: {checkpoint_path}")
            return data["checkpoint"], data["metadata"]
        except Exception as e:
            logger.error(f"Failed to load checkpoint: {e}")
            return None


def get_checkpoint_saver(use_memory: bool = True) -> BaseCheckpointSaver:
    """
    Get checkpoint saver instance.

    Args:
        use_memory: If True, use in-memory saver; otherwise use file-based

    Returns:
        Checkpoint saver instance
    """
    if use_memory:
        return MemorySaver()
    return FileCheckpointSaver()
