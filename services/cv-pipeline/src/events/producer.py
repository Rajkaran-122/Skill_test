"""
Kafka producer for publishing StoreEvents.

Uses aiokafka for async, batched publishing to Kafka topics.
Events are routed to the appropriate topic based on event_type.
"""

import asyncio
import json

import structlog

from src.config import KafkaConfig
from src.events.schemas import EventType, StoreEvent

logger = structlog.get_logger(__name__)

# Event type → Kafka topic mapping
TOPIC_ROUTING: dict[EventType, str] = {
    EventType.VISITOR_ENTER: "visitor-events",
    EventType.VISITOR_EXIT: "visitor-events",
    EventType.ZONE_ENTER: "zone-events",
    EventType.ZONE_EXIT: "zone-events",
    EventType.ZONE_DWELL: "zone-events",
    EventType.QUEUE_JOIN: "queue-events",
    EventType.QUEUE_LEAVE: "queue-events",
    EventType.QUEUE_ABANDON: "queue-events",
    EventType.PURCHASE: "conversion-events",
    EventType.STAFF_DETECTED: "visitor-events",
    EventType.ANOMALY_DETECTED: "anomaly-events",
    EventType.CAMERA_HEARTBEAT: "visitor-events",
}


class EventProducer:
    """Async Kafka producer for StoreEvents."""

    def __init__(self, config: KafkaConfig):
        self._config = config
        self._producer = None
        self._batch: list[StoreEvent] = []
        self._batch_lock = asyncio.Lock()
        self._running = False

    async def start(self) -> None:
        """Initialize and start the Kafka producer."""
        from aiokafka import AIOKafkaProducer

        logger.info(
            "Starting Kafka producer",
            bootstrap_servers=self._config.bootstrap_servers,
            batch_size=self._config.batch_size,
        )

        self._producer = AIOKafkaProducer(
            bootstrap_servers=self._config.bootstrap_servers,
            security_protocol=self._config.security_protocol,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            key_serializer=lambda k: k.encode("utf-8") if k else None,
            linger_ms=self._config.linger_ms,
            acks="all",
            enable_idempotence=True,
        )
        await self._producer.start()
        self._running = True
        logger.info("Kafka producer started")

    async def stop(self) -> None:
        """Flush remaining events and stop the producer."""
        if self._batch:
            await self._flush_batch()

        if self._producer:
            await self._producer.stop()
            self._running = False
            logger.info("Kafka producer stopped")

    async def publish(self, event: StoreEvent) -> None:
        """
        Add an event to the batch. Flushes when batch_size is reached.

        Args:
            event: The StoreEvent to publish.
        """
        async with self._batch_lock:
            self._batch.append(event)

            if len(self._batch) >= self._config.batch_size:
                await self._flush_batch()

    async def publish_immediate(self, event: StoreEvent) -> None:
        """Publish a single event immediately (bypasses batching)."""
        if not self._producer:
            logger.warning("Producer not started, dropping event", event_id=event.event_id)
            return

        topic = TOPIC_ROUTING.get(event.event_type, "visitor-events")

        try:
            await self._producer.send_and_wait(
                topic=topic,
                key=event.store_id,
                value=event.model_dump(mode="json"),
            )
            logger.debug(
                "Event published",
                topic=topic,
                event_type=event.event_type,
                visitor_id=event.visitor_id,
            )
        except Exception as e:
            logger.error(
                "Failed to publish event",
                event_id=event.event_id,
                error=str(e),
            )

    async def _flush_batch(self) -> None:
        """Flush all batched events to Kafka."""
        if not self._producer or not self._batch:
            return

        events = self._batch.copy()
        self._batch.clear()

        # Group events by topic for efficient publishing
        topic_groups: dict[str, list[StoreEvent]] = {}
        for event in events:
            topic = TOPIC_ROUTING.get(event.event_type, "visitor-events")
            if topic not in topic_groups:
                topic_groups[topic] = []
            topic_groups[topic].append(event)

        # Publish all events
        publish_tasks = []
        for topic, topic_events in topic_groups.items():
            for event in topic_events:
                task = self._producer.send(
                    topic=topic,
                    key=event.store_id.encode("utf-8"),
                    value=json.dumps(event.model_dump(mode="json")).encode("utf-8"),
                )
                publish_tasks.append(task)

        try:
            await asyncio.gather(*publish_tasks)
            logger.debug("Batch flushed", event_count=len(events))
        except Exception as e:
            logger.error("Batch flush failed", error=str(e), event_count=len(events))

    async def flush(self) -> None:
        """Force flush any remaining batched events."""
        async with self._batch_lock:
            await self._flush_batch()
