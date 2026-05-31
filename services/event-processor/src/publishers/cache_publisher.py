"""
Cache publisher — writes hot metrics to Redis for fast API responses.
Also handles Redis Pub/Sub for real-time WebSocket dashboard updates.
"""

import json

import structlog

logger = structlog.get_logger(__name__)


class CachePublisher:
    """Publishes metrics and events to Redis for caching and real-time updates."""

    def __init__(self):
        self._redis = None

    async def initialize(self, redis_url: str) -> None:
        """Create the Redis connection."""
        import redis.asyncio as aioredis

        self._redis = aioredis.from_url(redis_url, decode_responses=True)
        logger.info("Redis connection established")

    async def close(self) -> None:
        """Close the Redis connection."""
        if self._redis:
            await self._redis.close()

    async def publish_metrics(self, store_id: str, metrics: dict) -> None:
        """Cache store metrics and publish to dashboard channel."""
        if not self._redis:
            return

        key = f"sip:metrics:{store_id}"
        await self._redis.set(key, json.dumps(metrics), ex=300)  # 5 min TTL

        # Publish to Redis Pub/Sub for real-time WebSocket fan-out
        channel = f"sip:dashboard:{store_id}"
        await self._redis.publish(channel, json.dumps({
            "type": "METRICS_UPDATE",
            "store_id": store_id,
            "data": metrics,
        }))

    async def publish_queue_metrics(self, store_id: str, queue_data: dict) -> None:
        """Cache queue metrics."""
        if not self._redis:
            return

        key = f"sip:queue:{store_id}:{queue_data.get('zone_id', '')}"
        await self._redis.set(key, json.dumps(queue_data), ex=60)

        channel = f"sip:dashboard:{store_id}"
        await self._redis.publish(channel, json.dumps({
            "type": "QUEUE_UPDATE",
            "store_id": store_id,
            "data": queue_data,
        }))

    async def publish_anomaly(self, anomaly_data: dict) -> None:
        """Publish anomaly alert for real-time dashboard notification."""
        if not self._redis:
            return

        store_id = anomaly_data.get("store_id", "")

        # Store active anomaly
        key = f"sip:anomalies:{store_id}"
        anomalies = await self._redis.get(key)
        anomaly_list = json.loads(anomalies) if anomalies else []
        anomaly_list.append(anomaly_data)
        await self._redis.set(key, json.dumps(anomaly_list), ex=3600)

        # Publish alert to dashboard channel
        channel = f"sip:dashboard:{store_id}"
        await self._redis.publish(channel, json.dumps({
            "type": "ANOMALY_ALERT",
            "store_id": store_id,
            "data": anomaly_data,
        }))

    async def get_metrics(self, store_id: str) -> dict | None:
        """Retrieve cached metrics for a store."""
        if not self._redis:
            return None

        key = f"sip:metrics:{store_id}"
        data = await self._redis.get(key)
        return json.loads(data) if data else None
