"""
Metrics computation engine.

Computes real-time KPIs from event streams:
- Visitor count (unique)
- Conversion rate
- Zone popularity and dwell times
- Revenue (from POS correlation)

Hot metrics are published to Redis for sub-200ms API responses.
"""

from collections import defaultdict
from datetime import datetime, timezone

import structlog

logger = structlog.get_logger(__name__)


class MetricsEngine:
    """Computes and caches real-time store metrics."""

    def __init__(self, db_publisher=None, cache_publisher=None):
        self._db_publisher = db_publisher
        self._cache_publisher = cache_publisher

        # In-memory counters (per store, reset periodically)
        self._visitors: dict[str, set[str]] = defaultdict(set)  # store_id -> {visitor_ids}
        self._purchases: dict[str, set[str]] = defaultdict(set)
        self._revenue: dict[str, float] = defaultdict(float)
        self._zone_visitors: dict[str, dict[str, set[str]]] = defaultdict(lambda: defaultdict(set))
        self._zone_dwell: dict[str, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))

    async def process_visitor_event(self, event_data: dict) -> None:
        """Process a visitor enter/exit event for metrics."""
        store_id = event_data.get("store_id", "")
        visitor_id = event_data.get("visitor_id", "")
        event_type = event_data.get("event_type")

        if event_type == "VISITOR_ENTER":
            # Check for staff flag in metadata
            metadata = event_data.get("metadata", {})
            if not metadata.get("is_staff", False):
                self._visitors[store_id].add(visitor_id)

        await self._update_cache(store_id)

    async def process_zone_event(self, event_data: dict) -> None:
        """Process zone events for popularity metrics."""
        store_id = event_data.get("store_id", "")
        zone_id = event_data.get("zone_id", "")
        visitor_id = event_data.get("visitor_id", "")
        event_type = event_data.get("event_type")

        if event_type == "ZONE_ENTER":
            self._zone_visitors[store_id][zone_id].add(visitor_id)

        elif event_type == "ZONE_EXIT":
            dwell = event_data.get("metadata", {}).get("dwell_seconds")
            if dwell:
                self._zone_dwell[store_id][zone_id].append(dwell)

        await self._update_cache(store_id)

    async def process_conversion_event(self, event_data: dict) -> None:
        """Process a purchase/conversion event."""
        store_id = event_data.get("store_id", "")
        visitor_id = event_data.get("visitor_id", "")

        self._purchases[store_id].add(visitor_id)

        amount = event_data.get("metadata", {}).get("amount", 0)
        self._revenue[store_id] += amount

        await self._update_cache(store_id)

        logger.info(
            "Conversion recorded",
            store_id=store_id,
            visitor_id=visitor_id,
            amount=amount,
            total_conversions=len(self._purchases[store_id]),
        )

    async def _update_cache(self, store_id: str) -> None:
        """Push current metrics to Redis cache."""
        if not self._cache_publisher:
            return

        visitors = len(self._visitors.get(store_id, set()))
        purchases = len(self._purchases.get(store_id, set()))
        conversion_rate = purchases / visitors if visitors > 0 else 0.0

        # Zone metrics
        zones = []
        for zone_id, zone_visitors in self._zone_visitors.get(store_id, {}).items():
            zone_dwell = self._zone_dwell.get(store_id, {}).get(zone_id, [])
            avg_dwell = sum(zone_dwell) / len(zone_dwell) if zone_dwell else 0.0
            zones.append({
                "zone_id": zone_id,
                "visitors": len(zone_visitors),
                "avg_dwell": round(avg_dwell, 1),
            })

        metrics = {
            "store_id": store_id,
            "visitors": {
                "total": visitors,
                "unique": visitors,
            },
            "conversion": {
                "rate": round(conversion_rate, 4),
                "purchases": purchases,
                "revenue": round(self._revenue.get(store_id, 0), 2),
            },
            "zones": sorted(zones, key=lambda z: z["visitors"], reverse=True),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }

        await self._cache_publisher.publish_metrics(store_id, metrics)

    def get_metrics(self, store_id: str) -> dict:
        """Get current metrics for a store (from memory)."""
        visitors = len(self._visitors.get(store_id, set()))
        purchases = len(self._purchases.get(store_id, set()))
        return {
            "visitors": visitors,
            "purchases": purchases,
            "conversion_rate": purchases / visitors if visitors > 0 else 0.0,
            "revenue": self._revenue.get(store_id, 0),
        }
