"""
Event ingestion endpoint.

POST /api/v1/events/ingest — Receives detection events from the CV pipeline
and publishes them to Kafka for downstream processing.
"""

from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
import structlog

logger = structlog.get_logger(__name__)

router = APIRouter()


class EventPayload(BaseModel):
    """Single event in the ingest request."""
    event_id: str = Field(default_factory=lambda: str(uuid4()))
    store_id: str
    camera_id: str
    visitor_id: str
    event_type: str
    timestamp: datetime
    zone_id: str | None = None
    confidence: float = Field(ge=0.0, le=1.0, default=1.0)
    metadata: dict = Field(default_factory=dict)


class IngestRequest(BaseModel):
    """Batch event ingest request."""
    events: list[EventPayload]


class IngestResponse(BaseModel):
    """Response for successful ingest."""
    status: str = "accepted"
    events_received: int
    trace_id: str


@router.post("/events/ingest", response_model=IngestResponse, status_code=202)
async def ingest_events(request: IngestRequest):
    """
    Ingest a batch of detection events.

    Events are validated and published to Kafka for asynchronous processing.
    Returns 202 Accepted immediately.
    """
    if not request.events:
        raise HTTPException(status_code=400, detail="No events provided")

    trace_id = str(uuid4())

    logger.info(
        "Events ingested",
        trace_id=trace_id,
        event_count=len(request.events),
        store_id=request.events[0].store_id if request.events else None,
    )

    # TODO: Publish events to Kafka
    # For now, we accept and log

    return IngestResponse(
        status="accepted",
        events_received=len(request.events),
        trace_id=trace_id,
    )
