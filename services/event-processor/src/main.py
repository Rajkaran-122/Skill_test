"""
Event Processor — Main entry point.

Orchestrates all Kafka consumers and analytics engines.
Runs all consumers concurrently as async tasks.
"""

import asyncio
import signal

import structlog
from prometheus_client import start_http_server

from src.config import EventProcessorConfig
from src.consumers.visitor_consumer import VisitorConsumer
from src.consumers.zone_consumer import ZoneConsumer
from src.consumers.queue_consumer import QueueConsumer
from src.consumers.conversion_consumer import ConversionConsumer
from src.engines.session_builder import SessionBuilder
from src.engines.queue_engine import QueueEngine
from src.engines.metrics_engine import MetricsEngine
from src.engines.anomaly_engine import AnomalyEngine
from src.publishers.db_publisher import DBPublisher
from src.publishers.cache_publisher import CachePublisher
from src.publishers.alert_publisher import AlertPublisher

logger = structlog.get_logger(__name__)


class EventProcessor:
    """Main event processor orchestrating consumers and engines."""

    def __init__(self, config: EventProcessorConfig):
        self._config = config
        self._running = False

        # Publishers
        self._db_publisher = DBPublisher()
        self._cache_publisher = CachePublisher()
        self._alert_publisher = AlertPublisher()

        # Analytics engines
        self._session_builder = SessionBuilder(
            inactivity_timeout=config.session_inactivity_timeout,
            db_publisher=self._db_publisher,
            cache_publisher=self._cache_publisher,
        )
        self._queue_engine = QueueEngine(
            db_publisher=self._db_publisher,
            cache_publisher=self._cache_publisher,
        )
        self._metrics_engine = MetricsEngine(
            db_publisher=self._db_publisher,
            cache_publisher=self._cache_publisher,
        )
        self._anomaly_engine = AnomalyEngine(
            sigma_threshold=config.anomaly_sigma_threshold,
            dead_zone_minutes=config.anomaly_dead_zone_minutes,
            heartbeat_timeout=config.anomaly_camera_heartbeat_timeout,
            db_publisher=self._db_publisher,
            cache_publisher=self._cache_publisher,
            alert_publisher=self._alert_publisher,
        )

        # Engine registry for consumers
        self._engines = {
            "session_builder": self._session_builder,
            "queue_engine": self._queue_engine,
            "metrics_engine": self._metrics_engine,
            "anomaly_engine": self._anomaly_engine,
        }

        # Consumers
        self._consumers = [
            VisitorConsumer(config.kafka_bootstrap_servers, config.kafka_group_id, self._engines),
            ZoneConsumer(config.kafka_bootstrap_servers, config.kafka_group_id, self._engines),
            QueueConsumer(config.kafka_bootstrap_servers, config.kafka_group_id, self._engines),
            ConversionConsumer(config.kafka_bootstrap_servers, config.kafka_group_id, self._engines),
        ]

    async def start(self) -> None:
        """Initialize all components and start processing."""
        logger.info("Starting event processor")

        # Start Prometheus metrics
        start_http_server(self._config.metrics_port)

        # Initialize publishers
        await self._db_publisher.initialize(self._config.database_url)
        await self._cache_publisher.initialize(self._config.redis_url)
        await self._alert_publisher.initialize(self._config.kafka_bootstrap_servers)

        # Start all consumers
        for consumer in self._consumers:
            await consumer.start()

        self._running = True
        logger.info("Event processor started", consumers=len(self._consumers))

    async def run(self) -> None:
        """Run all consumers and periodic tasks concurrently."""
        tasks = []

        # Consumer tasks
        for consumer in self._consumers:
            tasks.append(asyncio.create_task(consumer.run()))

        # Periodic maintenance tasks
        tasks.append(asyncio.create_task(self._periodic_session_cleanup()))
        tasks.append(asyncio.create_task(self._periodic_anomaly_check()))

        try:
            await asyncio.gather(*tasks)
        except asyncio.CancelledError:
            logger.info("Event processor cancelled")

    async def stop(self) -> None:
        """Gracefully stop all components."""
        self._running = False

        for consumer in self._consumers:
            await consumer.stop()

        await self._alert_publisher.close()
        await self._cache_publisher.close()
        await self._db_publisher.close()

        logger.info("Event processor stopped")

    async def _periodic_session_cleanup(self) -> None:
        """Periodically close timed-out sessions."""
        while self._running:
            await asyncio.sleep(60)  # Check every minute
            await self._session_builder.check_timeouts()

    async def _periodic_anomaly_check(self) -> None:
        """Periodically check for dead zones and camera failures."""
        while self._running:
            await asyncio.sleep(30)  # Check every 30 seconds
            await self._anomaly_engine.check_dead_zones()
            await self._anomaly_engine.check_camera_health()


async def main():
    """Entry point for the event processor service."""
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
    )

    config = EventProcessorConfig()
    processor = EventProcessor(config)

    loop = asyncio.get_event_loop()

    def shutdown():
        asyncio.ensure_future(processor.stop())

    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, shutdown)
        except NotImplementedError:
            pass

    await processor.start()
    await processor.run()


if __name__ == "__main__":
    asyncio.run(main())
