"""
OSNet person re-identification implementation.

Uses TorchReID's OSNet model to extract 512-dimensional appearance
feature embeddings. These embeddings are used to match persons across
different cameras and re-entry scenarios, preventing duplicate counting.
"""

import structlog
import numpy as np
import cv2
import torch
from scipy.spatial.distance import cosine

from src.config import ReIDConfig
from src.reid.base import BaseReID

logger = structlog.get_logger(__name__)


class OSNetReID(BaseReID):
    """OSNet-based person re-identification."""

    def __init__(self, config: ReIDConfig):
        self._config = config
        self._model = None
        self._device = "cpu"
        self._input_size = (256, 128)  # Standard OSNet input: height x width

    def initialize(self) -> None:
        """Load OSNet model from TorchReID."""
        try:
            import torchreid

            logger.info("Loading OSNet model", model=self._config.model)

            self._device = "cuda" if torch.cuda.is_available() else "cpu"

            self._model = torchreid.models.build_model(
                name=self._config.model,
                num_classes=1000,
                pretrained=True,
            )
            self._model = self._model.to(self._device)
            self._model.eval()

            logger.info(
                "OSNet model loaded",
                model=self._config.model,
                device=self._device,
                feature_dim=self._config.feature_dim,
            )

        except ImportError:
            logger.warning(
                "TorchReID not installed. Using placeholder Re-ID (random features). "
                "Install with: pip install torchreid"
            )
            self._model = None

    def extract_features(self, person_crop: np.ndarray) -> np.ndarray:
        """
        Extract a 512-dimensional feature vector from a person crop.

        Args:
            person_crop: Cropped person image (H, W, 3) in BGR format.

        Returns:
            Normalized feature vector as (512,) numpy array.
        """
        if self._model is None:
            # Fallback: return random normalized features for development
            features = np.random.randn(self._config.feature_dim).astype(np.float32)
            return features / np.linalg.norm(features)

        # Preprocess: resize, convert BGR→RGB, normalize
        img = cv2.resize(person_crop, (self._input_size[1], self._input_size[0]))
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = img.astype(np.float32) / 255.0

        # ImageNet normalization
        mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)
        std = np.array([0.229, 0.224, 0.225], dtype=np.float32)
        img = (img - mean) / std

        # HWC → CHW → NCHW
        img = np.transpose(img, (2, 0, 1))
        img = np.expand_dims(img, axis=0)

        tensor = torch.from_numpy(img).to(self._device)

        with torch.no_grad():
            features = self._model(tensor)

        features = features.cpu().numpy().flatten()

        # L2 normalize
        norm = np.linalg.norm(features)
        if norm > 0:
            features = features / norm

        return features

    def compute_similarity(self, features_a: np.ndarray, features_b: np.ndarray) -> float:
        """
        Compute cosine similarity between two feature vectors.

        Returns a value in [0, 1] where 1 means identical.
        """
        return float(1.0 - cosine(features_a, features_b))

    @property
    def feature_dim(self) -> int:
        return self._config.feature_dim
