"""
Queue analytics engine.

Tracks queue metrics over time:
- Queue depth history
- Average wait time per period
- Abandonment rate
- Peak queue times
"""

from collections import defaultdict
from datetime import datetime, timezone

import structlog

logger = structlog.get_logger(__name__)


class QueueEngine:
    """Processes queue events and computes queue analytics."""

    def __init__(self, db_publisher=None, cache_publisher=None):
        self._db_publisher = db_publisher
        self._cache_publisher = cache_publisher
        self._queue_depth: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
        self._wait_times: dict[str, list[float]] = defaultdict(list)
        self._abandonments: dict[str, int] = defaultdict(int)

    async def process_event(self, event_data: dict) -> None:
        """Process a queue event."""
        event_type = event_data.get("event_type")
        store_id = event_data.get("store_id", "")
        zone_id = event_data.get("zone_id", "")
        key = f"{store_id}:{zone_id}"

        if event_type == "QUEUE_JOIN":
            self._queue_depth[store_id][zone_id] += 1
            logger.debug("Queue join", store_id=store_id, zone_id=zone_id, depth=self._queue_depth[store_id][zone_id])

        elif event_type == "QUEUE_LEAVE":
            self._queue_depth[store_id][zone_id] = max(0, self._queue_depth[store_id][zone_id] - 1)
            wait = event_data.get("metadata", {}).get("wait_seconds", 0)
            if wait:
                self._wait_times[key].append(wait)

        elif event_type == "QUEUE_ABANDON":
            self._queue_depth[store_id][zone_id] = max(0, self._queue_depth[store_id][zone_id] - 1)
            self._abandonments[key] += 1
            wait = event_data.get("metadata", {}).get("wait_seconds", 0)
            logger.info(
                "Queue abandonment",
                store_id=store_id,
                zone_id=zone_id,
                wait_seconds=wait,
                total_abandonments=self._abandonments[key],
            )

        # Update cache with current metrics
        if self._cache_publisher:
            await self._cache_publisher.publish_queue_metrics(store_id, {
                "zone_id": zone_id,
                "depth": self._queue_depth[store_id][zone_id],
                "avg_wait": self._get_avg_wait(key),
                "abandonments": self._abandonments[key],
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })

        # Persist to database
        if self._db_publisher:
            await self._db_publisher.publish_event(event_data)

    def get_depth(self, store_id: str, zone_id: str) -> int:
        """Get current queue depth."""
        return self._queue_depth.get(store_id, {}).get(zone_id, 0)

    def _get_avg_wait(self, key: str) -> float:
        """Compute average wait time for a queue zone."""
        times = self._wait_times.get(key, [])
        return sum(times) / len(times) if times else 0.0
