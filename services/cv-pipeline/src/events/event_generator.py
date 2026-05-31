"""
Event generator — converts CV pipeline outputs into StoreEvent objects.

This module sits between the CV processing components (detector, tracker,
re-id, zone tracker, queue detector) and the Kafka producer. It transforms
raw CV results into structured business events.
"""

from datetime import datetime, timezone

import structlog

from src.config import PipelineConfig
from src.events.schemas import (
    EventType,
    IdentifiedPerson,
    QueueSnapshot,
    StoreEvent,
)
from src.zones.zone_tracker import ZoneTransition

logger = structlog.get_logger(__name__)


class EventGenerator:
    """Generates StoreEvent objects from CV pipeline outputs."""

    def __init__(self, config: PipelineConfig):
        self._store_id = config.store_id
        self._camera_id = "CAM01"  # Will be set per camera stream

    def set_camera(self, camera_id: str) -> None:
        """Set the current camera ID for generated events."""
        self._camera_id = camera_id

    def visitor_enter(self, person: IdentifiedPerson) -> StoreEvent:
        """Generate a VISITOR_ENTER event."""
        return StoreEvent(
            store_id=self._store_id,
            camera_id=self._camera_id,
            visitor_id=person.visitor_id,
            event_type=EventType.VISITOR_ENTER,
            timestamp=datetime.now(timezone.utc),
            confidence=person.confidence,
            metadata={
                "track_id": person.track_id,
                "bbox": {
                    "x1": person.bbox.x1,
                    "y1": person.bbox.y1,
                    "x2": person.bbox.x2,
                    "y2": person.bbox.y2,
                },
                "is_staff": person.is_staff,
                "re_id_confidence": person.re_id_confidence,
            },
        )

    def visitor_exit(self, visitor_id: str, confidence: float = 1.0) -> StoreEvent:
        """Generate a VISITOR_EXIT event."""
        return StoreEvent(
            store_id=self._store_id,
            camera_id=self._camera_id,
            visitor_id=visitor_id,
            event_type=EventType.VISITOR_EXIT,
            timestamp=datetime.now(timezone.utc),
            confidence=confidence,
        )

    def zone_transition(self, transition: ZoneTransition) -> list[StoreEvent]:
        """Generate zone enter/exit events from a zone transition."""
        events: list[StoreEvent] = []
        now = datetime.now(timezone.utc)

        if transition.transition_type == "exit" and transition.from_zone:
            events.append(
                StoreEvent(
                    store_id=self._store_id,
                    camera_id=self._camera_id,
                    visitor_id=transition.visitor_id,
                    event_type=EventType.ZONE_EXIT,
                    timestamp=now,
                    zone_id=transition.from_zone,
                    confidence=1.0,
                    metadata={
                        "dwell_seconds": transition.dwell_seconds,
                        "to_zone": transition.to_zone,
                    },
                )
            )

        if transition.transition_type == "enter" and transition.to_zone:
            events.append(
                StoreEvent(
                    store_id=self._store_id,
                    camera_id=self._camera_id,
                    visitor_id=transition.visitor_id,
                    event_type=EventType.ZONE_ENTER,
                    timestamp=now,
                    zone_id=transition.to_zone,
                    confidence=1.0,
                    metadata={"from_zone": transition.from_zone},
                )
            )

        return events

    def queue_join(self, visitor_id: str, zone_id: str) -> StoreEvent:
        """Generate a QUEUE_JOIN event."""
        return StoreEvent(
            store_id=self._store_id,
            camera_id=self._camera_id,
            visitor_id=visitor_id,
            event_type=EventType.QUEUE_JOIN,
            timestamp=datetime.now(timezone.utc),
            zone_id=zone_id,
            confidence=1.0,
        )

    def queue_abandon(
        self, visitor_id: str, zone_id: str, wait_seconds: float = 0.0
    ) -> StoreEvent:
        """Generate a QUEUE_ABANDON event."""
        return StoreEvent(
            store_id=self._store_id,
            camera_id=self._camera_id,
            visitor_id=visitor_id,
            event_type=EventType.QUEUE_ABANDON,
            timestamp=datetime.now(timezone.utc),
            zone_id=zone_id,
            confidence=1.0,
            metadata={"wait_seconds": wait_seconds},
        )

    def staff_detected(self, person: IdentifiedPerson) -> StoreEvent:
        """Generate a STAFF_DETECTED event."""
        return StoreEvent(
            store_id=self._store_id,
            camera_id=self._camera_id,
            visitor_id=person.visitor_id,
            event_type=EventType.STAFF_DETECTED,
            timestamp=datetime.now(timezone.utc),
            confidence=person.confidence,
        )

    def camera_heartbeat(self) -> StoreEvent:
        """Generate a CAMERA_HEARTBEAT event for health monitoring."""
        return StoreEvent(
            store_id=self._store_id,
            camera_id=self._camera_id,
            visitor_id="SYSTEM",
            event_type=EventType.CAMERA_HEARTBEAT,
            timestamp=datetime.now(timezone.utc),
            confidence=1.0,
            metadata={"status": "active"},
        )
