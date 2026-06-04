from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class BaseEvent(BaseModel):
    """Base schema for all incoming events."""
    event_id: str = Field(..., description="Unique identifier for the event")
    store_id: str = Field(..., description="Store identifier")
    camera_id: str = Field(..., description="Camera identifier")
    timestamp: datetime = Field(..., description="ISO-8601 timestamp of the event")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Detection confidence score")


class EventMetadata(BaseModel):
    queue_depth: Optional[int] = None
    sku_zone: Optional[str] = None
    session_seq: Optional[int] = None

class VisitorEvent(BaseEvent):
    """Schema for a visitor detection/tracking event from the CV pipeline."""
    visitor_id: str = Field(..., description="Unique tracker ID from ByteTrack/OSNet")
    event_type: str = Field(..., description="Type: ENTRY, EXIT, ZONE_ENTER, ZONE_EXIT, ZONE_DWELL, BILLING_QUEUE_JOIN, BILLING_QUEUE_ABANDON, REENTRY")
    zone_id: Optional[str] = Field(default=None, description="Zone identifier if applicable")
    dwell_ms: Optional[int] = Field(default=None, description="Dwell time in ms")
    is_staff: bool = Field(default=False, description="Whether the visitor is staff")
    metadata: Optional[EventMetadata] = Field(default=None, description="Nested flexible metadata")


class SessionCreate(BaseModel):
    """Schema for creating a unified visitor session."""
    visitor_id: str
    store_id: str
    entry_time: datetime
    exit_time: Optional[datetime] = None
    is_staff: bool = False
    converted: bool = False
    trajectory: List[Dict[str, Any]] = []


class AnomalyEvent(BaseEvent):
    """Schema for anomaly engine alerts."""
    anomaly_type: str = Field(..., description="QUEUE_SPIKE, DEAD_ZONE, CONVERSION_DROP")
    severity: str = Field(..., description="LOW, MEDIUM, HIGH, CRITICAL")
    description: str
    metric_value: float
    threshold: float
