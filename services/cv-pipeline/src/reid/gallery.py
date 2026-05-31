"""
Feature gallery manager for person re-identification.

Maintains an in-memory gallery of person feature embeddings with TTL-based
expiry. Used to assign persistent visitor IDs across cameras and re-entries.

Design:
- Each gallery entry stores a visitor_id, feature embedding, and last-seen time.
- When a new person crop arrives, we extract features and compare against the gallery.
- If similarity exceeds threshold → same visitor (return existing ID).
- If no match → new visitor (assign new ID, add to gallery).
- Entries expire after TTL to bound memory usage.
"""

import time
from dataclasses import dataclass, field

import structlog
import numpy as np

from src.config import ReIDConfig
from src.reid.base import BaseReID

logger = structlog.get_logger(__name__)


@dataclass
class GalleryEntry:
    """A single person in the feature gallery."""

    visitor_id: str
    features: np.ndarray
    last_seen: float = field(default_factory=time.time)
    seen_count: int = 1
    is_staff: bool = False


class FeatureGallery:
    """
    Manages a gallery of person feature embeddings for Re-ID.

    Supports:
    - Matching new detections against known visitors (cosine similarity).
    - TTL-based expiry to prevent unbounded memory growth.
    - Gallery size limit with LRU eviction.
    - Feature averaging for improved matching over time.
    """

    def __init__(self, reid_engine: BaseReID, config: ReIDConfig):
        self._reid = reid_engine
        self._config = config
        self._gallery: dict[str, GalleryEntry] = {}
        self._visitor_counter = 0

    def match_or_create(
        self,
        person_crop: np.ndarray,
        track_id: int | None = None,
    ) -> tuple[str, bool, float]:
        """
        Match a person crop against the gallery, or create a new entry.

        Args:
            person_crop: Cropped person image (H, W, 3) BGR.
            track_id: Optional ByteTrack ID for logging.

        Returns:
            Tuple of (visitor_id, is_new_visitor, match_confidence).
        """
        # Evict expired entries first
        self._evict_expired()

        # Extract features for this person
        features = self._reid.extract_features(person_crop)

        # Search gallery for best match
        best_match_id: str | None = None
        best_similarity: float = 0.0

        for entry in self._gallery.values():
            similarity = self._reid.compute_similarity(features, entry.features)
            if similarity > best_similarity:
                best_similarity = similarity
                best_match_id = entry.visitor_id

        # Check if match exceeds threshold
        if best_match_id is not None and best_similarity >= self._config.similarity_threshold:
            # Update existing entry with running average of features
            entry = self._gallery[best_match_id]
            entry.last_seen = time.time()
            entry.seen_count += 1

            # Exponential moving average of features for stability
            alpha = 0.3
            entry.features = alpha * features + (1 - alpha) * entry.features
            # Re-normalize
            norm = np.linalg.norm(entry.features)
            if norm > 0:
                entry.features = entry.features / norm

            logger.debug(
                "Re-identified visitor",
                visitor_id=best_match_id,
                track_id=track_id,
                similarity=round(best_similarity, 3),
                seen_count=entry.seen_count,
            )

            return best_match_id, False, best_similarity

        # No match — create new visitor
        visitor_id = self._generate_visitor_id()

        # Enforce gallery size limit (LRU eviction)
        if len(self._gallery) >= self._config.gallery_max_size:
            self._evict_lru()

        self._gallery[visitor_id] = GalleryEntry(
            visitor_id=visitor_id,
            features=features,
        )

        logger.debug(
            "New visitor registered",
            visitor_id=visitor_id,
            track_id=track_id,
            gallery_size=len(self._gallery),
        )

        return visitor_id, True, 1.0

    def mark_as_staff(self, visitor_id: str) -> None:
        """Mark a visitor as staff in the gallery."""
        if visitor_id in self._gallery:
            self._gallery[visitor_id].is_staff = True

    def is_staff(self, visitor_id: str) -> bool:
        """Check if a visitor is marked as staff."""
        entry = self._gallery.get(visitor_id)
        return entry.is_staff if entry else False

    def get_entry(self, visitor_id: str) -> GalleryEntry | None:
        """Get a gallery entry by visitor ID."""
        return self._gallery.get(visitor_id)

    @property
    def size(self) -> int:
        """Number of entries in the gallery."""
        return len(self._gallery)

    def _generate_visitor_id(self) -> str:
        """Generate a unique visitor ID."""
        self._visitor_counter += 1
        return f"VIS_{self._visitor_counter:06d}"

    def _evict_expired(self) -> None:
        """Remove gallery entries that have exceeded the TTL."""
        now = time.time()
        expired = [
            vid
            for vid, entry in self._gallery.items()
            if (now - entry.last_seen) > self._config.gallery_ttl_seconds
        ]
        for vid in expired:
            del self._gallery[vid]

        if expired:
            logger.debug("Evicted expired gallery entries", count=len(expired))

    def _evict_lru(self) -> None:
        """Evict the least recently used gallery entry."""
        if not self._gallery:
            return

        oldest_id = min(self._gallery, key=lambda vid: self._gallery[vid].last_seen)
        del self._gallery[oldest_id]
        logger.debug("Evicted LRU gallery entry", visitor_id=oldest_id)

    def clear(self) -> None:
        """Clear the entire gallery."""
        self._gallery.clear()
        self._visitor_counter = 0
        logger.info("Gallery cleared")
