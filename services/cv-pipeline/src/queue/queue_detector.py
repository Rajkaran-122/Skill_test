"""
Queue detection module.

Detects queue formations near checkout/billing zones using spatial
clustering of person positions. Tracks queue depth, wait time per
person, and detects queue abandonment.

Algorithm:
1. Filter persons currently in checkout zones.
2. Cluster persons by proximity (max_person_spacing).
3. If cluster size >= min_cluster_size → queue detected.
4. Track join time per person to compute wait time.
5. If a person leaves without completing checkout → abandonment.
"""

import time
from dataclasses import dataclass, field

import structlog
import numpy as np

from src.config import QueueConfig
from src.events.schemas import BoundingBox, QueueSnapshot

logger = structlog.get_logger(__name__)


@dataclass
class QueueMember:
    """A person currently in the queue."""

    visitor_id: str
    join_time: float
    position: tuple[float, float]  # centroid (x, y)
    last_seen: float = field(default_factory=time.time)

    @property
    def wait_seconds(self) -> float:
        return time.time() - self.join_time


class QueueDetector:
    """Detects and tracks queue formations in checkout zones."""

    def __init__(self, config: QueueConfig):
        self._config = config
        self._queues: dict[str, dict[str, QueueMember]] = {}  # zone_id -> {visitor_id -> QueueMember}

    def update(
        self,
        zone_id: str,
        persons_in_zone: list[tuple[str, BoundingBox]],
    ) -> tuple[QueueSnapshot | None, list[str]]:
        """
        Update queue state for a zone.

        Args:
            zone_id: The checkout zone being tracked.
            persons_in_zone: List of (visitor_id, bbox) for persons in this zone.

        Returns:
            Tuple of (QueueSnapshot if queue detected, list of abandoned visitor_ids).
        """
        if zone_id not in self._queues:
            self._queues[zone_id] = {}

        queue = self._queues[zone_id]
        now = time.time()
        current_visitor_ids = {vid for vid, _ in persons_in_zone}
        abandonments: list[str] = []

        # Detect abandonments: people who left the queue zone
        for vid in list(queue.keys()):
            if vid not in current_visitor_ids:
                member = queue[vid]
                if member.wait_seconds > 10:  # Only count if they waited > 10s
                    abandonments.append(vid)
                    logger.info(
                        "Queue abandonment detected",
                        visitor_id=vid,
                        zone_id=zone_id,
                        wait_seconds=round(member.wait_seconds, 1),
                    )
                del queue[vid]

        # Update existing and add new members
        for vid, bbox in persons_in_zone:
            cx, cy = bbox.center
            if vid in queue:
                queue[vid].position = (cx, cy)
                queue[vid].last_seen = now
            else:
                queue[vid] = QueueMember(
                    visitor_id=vid,
                    join_time=now,
                    position=(cx, cy),
                    last_seen=now,
                )

        # Detect queue using spatial clustering
        positions = [(m.visitor_id, m.position) for m in queue.values()]
        is_queue = self._detect_queue_cluster(positions)

        snapshot = None
        if is_queue or len(queue) >= self._config.min_cluster_size:
            avg_wait = (
                sum(m.wait_seconds for m in queue.values()) / len(queue) if queue else 0.0
            )
            snapshot = QueueSnapshot(
                store_id="",  # Will be filled by event generator
                zone_id=zone_id,
                depth=len(queue),
                avg_wait_seconds=avg_wait,
                members=[m.visitor_id for m in queue.values()],
            )

        return snapshot, abandonments

    def _detect_queue_cluster(
        self, positions: list[tuple[str, tuple[float, float]]]
    ) -> bool:
        """
        Detect if positions form a queue-like cluster.

        A queue is detected when there are at least min_cluster_size
        persons within max_person_spacing of each other.
        """
        if len(positions) < self._config.min_cluster_size:
            return False

        # Simple proximity clustering
        coords = np.array([pos for _, pos in positions])
        n = len(coords)

        # Count how many neighbors each person has
        for i in range(n):
            neighbor_count = 0
            for j in range(n):
                if i == j:
                    continue
                dist = np.linalg.norm(coords[i] - coords[j])
                if dist <= self._config.max_person_spacing:
                    neighbor_count += 1

            if neighbor_count >= self._config.min_cluster_size - 1:
                return True

        return False

    def get_queue_depth(self, zone_id: str) -> int:
        """Get current queue depth for a zone."""
        return len(self._queues.get(zone_id, {}))

    def get_all_snapshots(self, store_id: str) -> list[QueueSnapshot]:
        """Get snapshots for all active queues."""
        snapshots = []
        for zone_id, queue in self._queues.items():
            if len(queue) >= self._config.min_cluster_size:
                avg_wait = sum(m.wait_seconds for m in queue.values()) / len(queue) if queue else 0.0
                snapshots.append(
                    QueueSnapshot(
                        store_id=store_id,
                        zone_id=zone_id,
                        depth=len(queue),
                        avg_wait_seconds=avg_wait,
                        members=[m.visitor_id for m in queue.values()],
                    )
                )
        return snapshots

    def clear(self) -> None:
        """Reset all queue state."""
        self._queues.clear()
