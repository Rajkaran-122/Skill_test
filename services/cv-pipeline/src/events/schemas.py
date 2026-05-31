"""
Event schemas shared across the CV pipeline.

All events conform to the core StoreEvent schema defined in the BRD.
Specialized event types extend the base with type-specific metadata.
"""

from datetime import datetime
from enum import Enum
from uuid import uuid4

from pydantic import BaseModel, Field


class EventType(str, Enum):
    """All event types in the SIP system."""

    VISITOR_ENTER = "VISITOR_ENTER"
    VISITOR_EXIT = "VISITOR_EXIT"
    ZONE_ENTER = "ZONE_ENTER"
    ZONE_EXIT = "ZONE_EXIT"
    ZONE_DWELL = "ZONE_DWELL"
    QUEUE_JOIN = "QUEUE_JOIN"
    QUEUE_LEAVE = "QUEUE_LEAVE"
    QUEUE_ABANDON = "QUEUE_ABANDON"
    PURCHASE = "PURCHASE"
    STAFF_DETECTED = "STAFF_DETECTED"
    ANOMALY_DETECTED = "ANOMALY_DETECTED"
    CAMERA_HEARTBEAT = "CAMERA_HEARTBEAT"


class AnomalyType(str, Enum):
    """Anomaly categories."""

    QUEUE_SPIKE = "QUEUE_SPIKE"
    CONVERSION_DROP = "CONVERSION_DROP"
    DEAD_ZONE = "DEAD_ZONE"
    CAMERA_FAILURE = "CAMERA_FAILURE"


class Severity(str, Enum):
    """Anomaly severity levels."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class BoundingBox(BaseModel):
    """Bounding box for a detected person."""

    x1: float
    y1: float
    x2: float
    y2: float

    @property
    def center(self) -> tuple[float, float]:
        """Return the center point of the bounding box."""
        return ((self.x1 + self.x2) / 2, (self.y1 + self.y2) / 2)

    @property
    def width(self) -> float:
        return self.x2 - self.x1

    @property
    def height(self) -> float:
        return self.y2 - self.y1

    @property
    def area(self) -> float:
        return self.width * self.height


class Detection(BaseModel):
    """A single person detection from YOLO."""

    bbox: BoundingBox
    confidence: float = Field(ge=0.0, le=1.0)
    class_id: int = 0  # 0 = person in COCO


class TrackedPerson(BaseModel):
    """A tracked person with persistent ID."""

    track_id: int
    bbox: BoundingBox
    confidence: float = Field(ge=0.0, le=1.0)
    is_new: bool = False  # True if first frame for this track
    frames_tracked: int = 1


class IdentifiedPerson(BaseModel):
    """A re-identified person with a global visitor ID."""

    track_id: int
    visitor_id: str
    bbox: BoundingBox
    confidence: float = Field(ge=0.0, le=1.0)
    is_staff: bool = False
    is_new_visitor: bool = False
    re_id_confidence: float = Field(default=1.0, ge=0.0, le=1.0)


class StoreEvent(BaseModel):
    """
    Core event schema for the SIP platform.

    This is the canonical event format published to Kafka.
    All downstream consumers expect this schema.
    """

    event_id: str = Field(default_factory=lambda: str(uuid4()))
    store_id: str
    camera_id: str
    visitor_id: str
    event_type: EventType
    timestamp: datetime
    zone_id: str | None = None
    confidence: float = Field(ge=0.0, le=1.0)
    metadata: dict = Field(default_factory=dict)

    def to_kafka_key(self) -> bytes:
        """Return the Kafka partition key (store_id)."""
        return self.store_id.encode("utf-8")

    def to_kafka_value(self) -> bytes:
        """Serialize event to JSON bytes for Kafka."""
        return self.model_dump_json().encode("utf-8")

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class QueueSnapshot(BaseModel):
    """Snapshot of queue state at a point in time."""

    store_id: str
    zone_id: str
    depth: int
    avg_wait_seconds: float = 0.0
    members: list[str] = Field(default_factory=list)  # visitor_ids
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ZoneDwellRecord(BaseModel):
    """Records a visitor's dwell in a zone."""

    visitor_id: str
    zone_id: str
    enter_time: datetime
    exit_time: datetime | None = None

    @property
    def dwell_seconds(self) -> float | None:
        if self.exit_time is None:
            return None
        return (self.exit_time - self.enter_time).total_seconds()
