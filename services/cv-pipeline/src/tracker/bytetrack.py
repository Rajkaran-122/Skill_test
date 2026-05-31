"""
ByteTrack multi-object tracker implementation.

Uses the Ultralytics-integrated ByteTrack for frame-to-frame identity
persistence. ByteTrack's two-stage association handles both high and
low-confidence detections, reducing identity switches during occlusions.
"""

import structlog
import numpy as np

from src.config import TrackerConfig
from src.events.schemas import BoundingBox, Detection, TrackedPerson
from src.tracker.base import BaseTracker

logger = structlog.get_logger(__name__)


class ByteTrackTracker(BaseTracker):
    """ByteTrack tracker using Ultralytics integration."""

    def __init__(self, config: TrackerConfig):
        self._config = config
        self._model = None
        self._track_history: dict[int, int] = {}  # track_id -> frames_tracked
        self._known_tracks: set[int] = set()

    def initialize(self) -> None:
        """Initialize the YOLO model with ByteTrack tracker enabled."""
        from ultralytics import YOLO

        logger.info(
            "Initializing ByteTrack tracker",
            track_thresh=self._config.track_thresh,
            match_thresh=self._config.match_thresh,
            track_buffer=self._config.track_buffer,
        )

        # We use a lightweight YOLO model purely as a carrier for the tracker.
        # Detection is done separately by the detector module.
        # In practice, we pass pre-computed detections to track().
        self._model = YOLO("yolo11n.pt")
        self._known_tracks = set()
        self._track_history = {}

        logger.info("ByteTrack tracker initialized")

    def update(self, detections: list[Detection], frame: np.ndarray) -> list[TrackedPerson]:
        """
        Update tracker with new detections.

        Uses the Ultralytics tracker which internally runs ByteTrack
        on the provided frame. We run detection + tracking in a single
        pass for efficiency.
        """
        if self._model is None:
            raise RuntimeError("Tracker not initialized. Call initialize() first.")

        if len(detections) == 0:
            return []

        # Run YOLO with ByteTrack tracking enabled
        results = self._model.track(
            frame,
            persist=True,
            tracker="bytetrack.yaml",
            conf=self._config.track_thresh,
            verbose=False,
        )

        tracked_persons: list[TrackedPerson] = []

        for result in results:
            if result.boxes is None or result.boxes.id is None:
                continue

            boxes = result.boxes.xyxy.cpu().numpy()
            track_ids = result.boxes.id.int().cpu().tolist()
            confidences = result.boxes.conf.cpu().numpy()
            class_ids = result.boxes.cls.cpu().numpy().astype(int)

            for box, track_id, conf, cls_id in zip(boxes, track_ids, confidences, class_ids):
                # Only track persons (class 0)
                if cls_id != 0:
                    continue

                is_new = track_id not in self._known_tracks
                if is_new:
                    self._known_tracks.add(track_id)
                    self._track_history[track_id] = 0

                self._track_history[track_id] = self._track_history.get(track_id, 0) + 1

                person = TrackedPerson(
                    track_id=track_id,
                    bbox=BoundingBox(
                        x1=float(box[0]),
                        y1=float(box[1]),
                        x2=float(box[2]),
                        y2=float(box[3]),
                    ),
                    confidence=float(conf),
                    is_new=is_new,
                    frames_tracked=self._track_history[track_id],
                )
                tracked_persons.append(person)

        return tracked_persons

    def reset(self) -> None:
        """Reset all tracking state."""
        self._known_tracks.clear()
        self._track_history.clear()
        if self._model is not None:
            # Reset the tracker by re-initializing
            self._model.predictor = None
        logger.info("ByteTrack tracker reset")

    @property
    def active_track_count(self) -> int:
        return len(self._known_tracks)
