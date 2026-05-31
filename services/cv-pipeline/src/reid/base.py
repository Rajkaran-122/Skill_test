"""
Abstract base class for person re-identification engines.
"""

from abc import ABC, abstractmethod

import numpy as np


class BaseReID(ABC):
    """Abstract person re-identification interface."""

    @abstractmethod
    def initialize(self) -> None:
        """Load Re-ID model weights."""
        ...

    @abstractmethod
    def extract_features(self, person_crop: np.ndarray) -> np.ndarray:
        """
        Extract a feature embedding from a person crop.

        Args:
            person_crop: Cropped person image (H, W, 3) BGR.

        Returns:
            Feature vector as 1D numpy array.
        """
        ...

    @abstractmethod
    def compute_similarity(self, features_a: np.ndarray, features_b: np.ndarray) -> float:
        """
        Compute similarity between two feature vectors.

        Args:
            features_a: Feature vector A.
            features_b: Feature vector B.

        Returns:
            Similarity score in [0, 1]. Higher = more similar.
        """
        ...

    @property
    @abstractmethod
    def feature_dim(self) -> int:
        """Return the dimensionality of the feature embedding."""
        ...
