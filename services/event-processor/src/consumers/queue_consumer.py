"""Queue events consumer."""

import structlog
from src.consumers.base import BaseConsumer

logger = structlog.get_logger(__name__)


class QueueConsumer(BaseConsumer):
    """Consumes queue-events topic."""

    def __init__(self, bootstrap_servers: str, group_id: str, engines: dict):
        super().__init__(
            topic="queue-events",
            bootstrap_servers=bootstrap_servers,
            group_id=f"{group_id}-queue",
        )
        self._engines = engines

    async def process_event(self, event_data: dict) -> None:
        """Route queue events to analytics engines."""
        queue_engine = self._engines.get("queue_engine")
        if queue_engine:
            await queue_engine.process_event(event_data)

        anomaly_engine = self._engines.get("anomaly_engine")
        if anomaly_engine:
            await anomaly_engine.process_queue_event(event_data)

        logger.debug("Queue event processed", event_type=event_data.get("event_type"))
