"""
Database publisher — writes processed data to PostgreSQL/TimescaleDB.
"""

import json
from datetime import datetime

import structlog

logger = structlog.get_logger(__name__)


class DBPublisher:
    """Publishes processed events and sessions to the database."""

    def __init__(self, db_pool=None):
        self._pool = db_pool

    async def initialize(self, database_url: str) -> None:
        """Create the database connection pool."""
        import asyncpg

        # Convert SQLAlchemy URL to asyncpg format
        url = database_url.replace("postgresql+asyncpg://", "postgresql://")
        self._pool = await asyncpg.create_pool(url, min_size=5, max_size=20)
        logger.info("Database connection pool created")

    async def close(self) -> None:
        """Close the connection pool."""
        if self._pool:
            await self._pool.close()

    async def publish_event(self, event_data: dict) -> None:
        """Insert a raw event into the events hypertable."""
        if not self._pool:
            return

        async with self._pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO events (event_id, store_id, camera_id, visitor_id, event_type, zone_id, confidence, metadata, timestamp)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                """,
                event_data.get("event_id"),
                event_data.get("store_id"),
                event_data.get("camera_id"),
                event_data.get("visitor_id"),
                event_data.get("event_type"),
                event_data.get("zone_id"),
                event_data.get("confidence"),
                json.dumps(event_data.get("metadata", {})),
                datetime.fromisoformat(event_data["timestamp"]),
            )

    async def publish_session(self, session_data: dict) -> None:
        """Insert a completed session."""
        if not self._pool:
            return

        async with self._pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO sessions (store_id, visitor_id, session_start, session_end, duration_seconds,
                                      zones_visited, is_staff, is_converted, entry_camera, exit_camera)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                """,
                session_data.get("store_id"),
                session_data.get("visitor_id"),
                datetime.fromisoformat(session_data["session_start"]),
                datetime.fromisoformat(session_data["session_end"]) if session_data.get("session_end") else None,
                session_data.get("duration_seconds"),
                json.dumps(session_data.get("zones_visited", [])),
                session_data.get("is_staff", False),
                session_data.get("is_converted", False),
                session_data.get("entry_camera"),
                session_data.get("exit_camera"),
            )

    async def publish_anomaly(self, anomaly_data: dict) -> None:
        """Insert a detected anomaly."""
        if not self._pool:
            return

        async with self._pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO anomalies (store_id, anomaly_type, severity, description, metadata, detected_at)
                VALUES ($1, $2, $3, $4, $5, $6)
                """,
                anomaly_data.get("store_id"),
                anomaly_data.get("anomaly_type"),
                anomaly_data.get("severity"),
                anomaly_data.get("description"),
                json.dumps(anomaly_data.get("metadata", {})),
                datetime.fromisoformat(anomaly_data["detected_at"]),
            )
