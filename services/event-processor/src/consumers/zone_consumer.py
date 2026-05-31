"""Zone events consumer."""

import structlog
from src.consumers.base import BaseConsumer

logger = structlog.get_logger(__name__)


class ZoneConsumer(BaseConsumer):
    """Consumes zone-events topic."""

    def __init__(self, bootstrap_servers: str, group_id: str, engines: dict):
        super().__init__(
            topic="zone-events",
            bootstrap_servers=bootstrap_servers,
            group_id=f"{group_id}-zone",
        )
        self._engines = engines

    async def process_event(self, event_data: dict) -> None:
        """Route zone events to analytics engines."""
        event_type = event_data.get("event_type")

        # Session builder: track zone visits
        session_builder = self._engines.get("session_builder")
        if session_builder:
            await session_builder.process_zone_event(event_data)

        # Metrics engine: zone popularity
        metrics_engine = self._engines.get("metrics_engine")
        if metrics_engine:
            await metrics_engine.process_zone_event(event_data)

        # Anomaly engine: dead zone detection
        anomaly_engine = self._engines.get("anomaly_engine")
        if anomaly_engine and event_type == "ZONE_ENTER":
            await anomaly_engine.record_zone_activity(event_data)

        logger.debug("Zone event processed", event_type=event_type, zone_id=event_data.get("zone_id"))
