"""
Abstract base class for multi-object trackers.

Any tracker (ByteTrack, DeepSORT, etc.) must implement this interface.
"""

from abc import ABC, abstractmethod

import numpy as np

from src.events.schemas import Detection, TrackedPerson


class BaseTracker(ABC):
    """Abstract multi-object tracker interface."""

    @abstractmethod
    def initialize(self) -> None:
        """Initialize tracker state."""
        ...

    @abstractmethod
    def update(self, detections: list[Detection], frame: np.ndarray) -> list[TrackedPerson]:
        """
        Update tracker with new detections and return tracked persons.

        Args:
            detections: List of person detections from the current frame.
            frame: The current video frame (for appearance features).

        Returns:
            List of TrackedPerson objects with persistent track IDs.
        """
        ...

    @abstractmethod
    def reset(self) -> None:
        """Reset all tracks."""
        ...

    @property
    @abstractmethod
    def active_track_count(self) -> int:
        """Return the number of currently active tracks."""
        ...
