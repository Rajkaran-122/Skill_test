"""
Visitor events consumer.

Consumes events from the 'visitor-events' Kafka topic and
routes them to the session builder and metrics engine.
"""

import structlog

from src.consumers.base import BaseConsumer

logger = structlog.get_logger(__name__)


class VisitorConsumer(BaseConsumer):
    """Consumes visitor-events topic."""

    def __init__(self, bootstrap_servers: str, group_id: str, engines: dict):
        super().__init__(
            topic="visitor-events",
            bootstrap_servers=bootstrap_servers,
            group_id=f"{group_id}-visitor",
        )
        self._engines = engines

    async def process_event(self, event_data: dict) -> None:
        """Route visitor events to appropriate engines."""
        event_type = event_data.get("event_type")

        if event_type in ("VISITOR_ENTER", "VISITOR_EXIT"):
            # Session builder
            session_builder = self._engines.get("session_builder")
            if session_builder:
                await session_builder.process_event(event_data)

            # Metrics engine
            metrics_engine = self._engines.get("metrics_engine")
            if metrics_engine:
                await metrics_engine.process_visitor_event(event_data)

        elif event_type == "STAFF_DETECTED":
            session_builder = self._engines.get("session_builder")
            if session_builder:
                await session_builder.mark_staff(event_data)

        elif event_type == "CAMERA_HEARTBEAT":
            anomaly_engine = self._engines.get("anomaly_engine")
            if anomaly_engine:
                await anomaly_engine.process_heartbeat(event_data)

        logger.debug(
            "Visitor event processed",
            event_type=event_type,
            visitor_id=event_data.get("visitor_id"),
        )
