"""
Abstract base class for person detectors.

Any detection model (YOLO11, YOLO26, etc.) must implement this interface.
This enables hot-swapping models via configuration without changing pipeline code.
"""

from abc import ABC, abstractmethod

import numpy as np

from src.events.schemas import Detection


class BaseDetector(ABC):
    """Abstract person detector interface."""

    @abstractmethod
    def initialize(self) -> None:
        """Load model weights and prepare for inference."""
        ...

    @abstractmethod
    def detect(self, frame: np.ndarray) -> list[Detection]:
        """
        Detect persons in a single frame.

        Args:
            frame: BGR image as numpy array (H, W, 3).

        Returns:
            List of Detection objects with bounding boxes and confidence scores.
        """
        ...

    @abstractmethod
    def warmup(self) -> None:
        """Run a warmup inference pass to initialize GPU kernels."""
        ...

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Return the model identifier string."""
        ...
