"""
Alert publisher — publishes anomaly alerts to the dashboard-events Kafka topic.
"""

import json

import structlog

logger = structlog.get_logger(__name__)


class AlertPublisher:
    """Publishes anomaly alerts to Kafka for dashboard consumption."""

    def __init__(self):
        self._producer = None

    async def initialize(self, bootstrap_servers: str) -> None:
        """Create the Kafka producer for alerts."""
        from aiokafka import AIOKafkaProducer

        self._producer = AIOKafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        )
        await self._producer.start()
        logger.info("Alert publisher started")

    async def close(self) -> None:
        """Stop the Kafka producer."""
        if self._producer:
            await self._producer.stop()

    async def publish_alert(self, anomaly_data: dict) -> None:
        """Publish an anomaly alert to the dashboard-events topic."""
        if not self._producer:
            return

        await self._producer.send(
            topic="dashboard-events",
            key=anomaly_data.get("store_id", "").encode("utf-8"),
            value=anomaly_data,
        )
        logger.info(
            "Alert published",
            anomaly_type=anomaly_data.get("anomaly_type"),
            severity=anomaly_data.get("severity"),
        )
