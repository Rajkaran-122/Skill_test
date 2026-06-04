from typing import Optional, Dict, Any, List
from datetime import datetime
from sqlmodel import SQLModel, Field, JSON, Column
from sqlalchemy import text


class VisitorEventDB(SQLModel, table=True):
    """
    Database model for Visitor Events.
    This table will be converted to a TimescaleDB hypertable partitioned by `timestamp`.
    """
    __tablename__ = "visitor_events"

    id: Optional[int] = Field(default=None, primary_key=True)
    event_id: str = Field(index=True, unique=True)
    store_id: str = Field(index=True)
    camera_id: str
    visitor_id: str = Field(index=True)
    event_type: str
    zone_id: Optional[str] = Field(default=None, index=True)
    dwell_ms: Optional[int] = Field(default=None)
    is_staff: bool = Field(default=False, index=True)
    metadata_json: Optional[Dict[str, Any]] = Field(default={}, sa_column=Column(JSON))
    timestamp: datetime = Field(
        sa_column_kwargs={"server_default": text("CURRENT_TIMESTAMP")}
    )
    confidence: float


class StoreSessionDB(SQLModel, table=True):
    """
    Database model for stitched visitor sessions.
    Aggregates raw events into a single row per visitor visit.
    """
    __tablename__ = "store_sessions"

    id: Optional[int] = Field(default=None, primary_key=True)
    visitor_id: str = Field(index=True)
    store_id: str = Field(index=True)
    entry_time: datetime = Field(index=True)
    exit_time: Optional[datetime] = None
    
    # Flags for analytics filtering
    is_staff: bool = Field(default=False, index=True)
    converted: bool = Field(default=False, index=True)
    
    # Store trajectory array as JSON
    trajectory: List[Dict[str, Any]] = Field(default=[], sa_column=Column(JSON))


class AnomalyDB(SQLModel, table=True):
    """Database model for persisted anomaly alerts."""
    __tablename__ = "anomalies"

    id: Optional[int] = Field(default=None, primary_key=True)
    store_id: str = Field(index=True)
    anomaly_type: str = Field(index=True)
    severity: str = Field(index=True)
    description: str
    timestamp: datetime = Field(
        sa_column_kwargs={"server_default": text("CURRENT_TIMESTAMP")}
    )
    metric_value: float
    threshold: float
    resolved: bool = Field(default=False)
