"""
Abstract base consumer for Kafka topics.

Provides common functionality for all event consumers:
- Connection management
- Deserialization
- Error handling with DLQ
- Graceful shutdown
"""

import asyncio
import json
from abc import ABC, abstractmethod

import structlog

logger = structlog.get_logger(__name__)


class BaseConsumer(ABC):
    """Abstract Kafka consumer with common lifecycle management."""

    def __init__(
        self,
        topic: str,
        bootstrap_servers: str,
        group_id: str,
    ):
        self._topic = topic
        self._bootstrap_servers = bootstrap_servers
        self._group_id = group_id
        self._consumer = None
        self._running = False

    async def start(self) -> None:
        """Initialize and start the Kafka consumer."""
        from aiokafka import AIOKafkaConsumer

        self._consumer = AIOKafkaConsumer(
            self._topic,
            bootstrap_servers=self._bootstrap_servers,
            group_id=self._group_id,
            auto_offset_reset="latest",
            enable_auto_commit=True,
            auto_commit_interval_ms=5000,
            value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        )
        await self._consumer.start()
        self._running = True
        logger.info("Consumer started", topic=self._topic, group_id=self._group_id)

    async def stop(self) -> None:
        """Stop the consumer gracefully."""
        self._running = False
        if self._consumer:
            await self._consumer.stop()
        logger.info("Consumer stopped", topic=self._topic)

    async def run(self) -> None:
        """Main consume loop."""
        if not self._consumer:
            raise RuntimeError("Consumer not started. Call start() first.")

        try:
            async for message in self._consumer:
                if not self._running:
                    break

                try:
                    event_data = message.value
                    await self.process_event(event_data)
                except Exception as e:
                    logger.error(
                        "Failed to process event",
                        topic=self._topic,
                        error=str(e),
                        offset=message.offset,
                        partition=message.partition,
                    )
                    # TODO: Publish to DLQ
        except asyncio.CancelledError:
            logger.info("Consumer cancelled", topic=self._topic)

    @abstractmethod
    async def process_event(self, event_data: dict) -> None:
        """
        Process a single event.

        Args:
            event_data: Deserialized event dictionary.
        """
        ...
