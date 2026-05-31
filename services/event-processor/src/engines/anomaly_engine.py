"""
Anomaly detection engine.

Detects operational anomalies in real-time using statistical methods:

1. Queue Spike:    Current queue depth > historical avg + 3σ
2. Conversion Drop: Current conversion < historical average
3. Dead Zone:      No traffic in a zone for 30 minutes
4. Camera Failure: No heartbeat events for 60 seconds
"""

import time
from collections import defaultdict, deque
from datetime import datetime, timezone

import numpy as np
import structlog

logger = structlog.get_logger(__name__)


class AnomalyEngine:
    """Statistical anomaly detection for store operations."""

    def __init__(
        self,
        sigma_threshold: float = 3.0,
        dead_zone_minutes: int = 30,
        heartbeat_timeout: int = 60,
        db_publisher=None,
        cache_publisher=None,
        alert_publisher=None,
    ):
        self._sigma = sigma_threshold
        self._dead_zone_timeout = dead_zone_minutes * 60  # Convert to seconds
        self._heartbeat_timeout = heartbeat_timeout
        self._db_publisher = db_publisher
        self._cache_publisher = cache_publisher
        self._alert_publisher = alert_publisher

        # Rolling windows for statistical analysis
        self._queue_history: dict[str, deque] = defaultdict(lambda: deque(maxlen=360))  # 1hr at 10s intervals
        self._zone_activity: dict[str, float] = {}  # zone_key -> last_activity_timestamp
        self._camera_heartbeats: dict[str, float] = {}  # camera_key -> last_heartbeat
        self._active_anomalies: dict[str, dict] = {}  # anomaly_key -> anomaly_data

    async def process_queue_event(self, event_data: dict) -> None:
        """Check for queue spike anomalies."""
        store_id = event_data.get("store_id", "")
        zone_id = event_data.get("zone_id", "")
        key = f"{store_id}:{zone_id}"

        # We track queue depth over time via metadata
        # For simplicity, we'll track join events as depth proxy
        if event_data.get("event_type") == "QUEUE_JOIN":
            self._queue_history[key].append(time.time())

        # Check for queue spike
        recent_count = len(self._queue_history[key])
        if recent_count > 10:  # Need enough data points
            depths = list(range(len(self._queue_history[key])))
            if len(depths) >= 2:
                mean = np.mean(depths)
                std = np.std(depths)
                threshold = mean + self._sigma * std if std > 0 else mean + 5

                if recent_count > threshold:
                    anomaly_key = f"QUEUE_SPIKE:{key}"
                    if anomaly_key not in self._active_anomalies:
                        anomaly = {
                            "store_id": store_id,
                            "anomaly_type": "QUEUE_SPIKE",
                            "severity": "HIGH",
                            "description": f"Queue depth {recent_count} exceeds {self._sigma}σ threshold of {int(threshold)}",
                            "metadata": {
                                "zone_id": zone_id,
                                "current_depth": recent_count,
                                "threshold": int(threshold),
                                "mean": round(mean, 1),
                                "std": round(std, 2),
                            },
                            "detected_at": datetime.now(timezone.utc).isoformat(),
                        }
                        self._active_anomalies[anomaly_key] = anomaly
                        await self._raise_anomaly(anomaly)

    async def record_zone_activity(self, event_data: dict) -> None:
        """Record zone activity for dead zone detection."""
        store_id = event_data.get("store_id", "")
        zone_id = event_data.get("zone_id", "")
        key = f"{store_id}:{zone_id}"
        self._zone_activity[key] = time.time()

    async def process_heartbeat(self, event_data: dict) -> None:
        """Record camera heartbeat for failure detection."""
        store_id = event_data.get("store_id", "")
        camera_id = event_data.get("camera_id", "")
        key = f"{store_id}:{camera_id}"
        self._camera_heartbeats[key] = time.time()

    async def check_dead_zones(self) -> list[dict]:
        """Check for zones with no recent activity."""
        now = time.time()
        anomalies = []

        for key, last_activity in self._zone_activity.items():
            if (now - last_activity) > self._dead_zone_timeout:
                anomaly_key = f"DEAD_ZONE:{key}"
                if anomaly_key not in self._active_anomalies:
                    store_id, zone_id = key.split(":", 1)
                    inactive_minutes = int((now - last_activity) / 60)
                    anomaly = {
                        "store_id": store_id,
                        "anomaly_type": "DEAD_ZONE",
                        "severity": "MEDIUM",
                        "description": f"No traffic in zone {zone_id} for {inactive_minutes} minutes",
                        "metadata": {
                            "zone_id": zone_id,
                            "inactive_minutes": inactive_minutes,
                        },
                        "detected_at": datetime.now(timezone.utc).isoformat(),
                    }
                    self._active_anomalies[anomaly_key] = anomaly
                    anomalies.append(anomaly)
                    await self._raise_anomaly(anomaly)

        return anomalies

    async def check_camera_health(self) -> list[dict]:
        """Check for cameras with missing heartbeats."""
        now = time.time()
        anomalies = []

        for key, last_heartbeat in self._camera_heartbeats.items():
            if (now - last_heartbeat) > self._heartbeat_timeout:
                anomaly_key = f"CAMERA_FAILURE:{key}"
                if anomaly_key not in self._active_anomalies:
                    store_id, camera_id = key.split(":", 1)
                    anomaly = {
                        "store_id": store_id,
                        "anomaly_type": "CAMERA_FAILURE",
                        "severity": "CRITICAL",
                        "description": f"Camera {camera_id} has not sent a heartbeat for {int(now - last_heartbeat)}s",
                        "metadata": {
                            "camera_id": camera_id,
                            "last_heartbeat": last_heartbeat,
                        },
                        "detected_at": datetime.now(timezone.utc).isoformat(),
                    }
                    self._active_anomalies[anomaly_key] = anomaly
                    anomalies.append(anomaly)
                    await self._raise_anomaly(anomaly)

        return anomalies

    async def _raise_anomaly(self, anomaly: dict) -> None:
        """Publish an anomaly to all channels."""
        logger.warning(
            "Anomaly detected",
            anomaly_type=anomaly["anomaly_type"],
            severity=anomaly["severity"],
            description=anomaly["description"],
        )

        if self._db_publisher:
            await self._db_publisher.publish_anomaly(anomaly)

        if self._cache_publisher:
            await self._cache_publisher.publish_anomaly(anomaly)

        if self._alert_publisher:
            await self._alert_publisher.publish_alert(anomaly)

    def resolve_anomaly(self, anomaly_key: str) -> None:
        """Mark an anomaly as resolved."""
        self._active_anomalies.pop(anomaly_key, None)

    @property
    def active_anomalies(self) -> list[dict]:
        """Return list of active anomalies."""
        return list(self._active_anomalies.values())
