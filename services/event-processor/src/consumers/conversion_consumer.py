"""Conversion events consumer."""

import structlog
from src.consumers.base import BaseConsumer

logger = structlog.get_logger(__name__)


class ConversionConsumer(BaseConsumer):
    """Consumes conversion-events topic."""

    def __init__(self, bootstrap_servers: str, group_id: str, engines: dict):
        super().__init__(
            topic="conversion-events",
            bootstrap_servers=bootstrap_servers,
            group_id=f"{group_id}-conversion",
        )
        self._engines = engines

    async def process_event(self, event_data: dict) -> None:
        """Route conversion events to the metrics engine."""
        metrics_engine = self._engines.get("metrics_engine")
        if metrics_engine:
            await metrics_engine.process_conversion_event(event_data)

        session_builder = self._engines.get("session_builder")
        if session_builder:
            await session_builder.mark_converted(event_data)

        logger.debug("Conversion event processed", visitor_id=event_data.get("visitor_id"))
