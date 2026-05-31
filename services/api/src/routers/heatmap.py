"""
Heatmap endpoint.

GET /api/v1/stores/{store_id}/heatmap — Returns zone activity heatmap data.
"""

import json
from datetime import datetime, timezone

from fastapi import APIRouter, Request
import structlog

logger = structlog.get_logger(__name__)

router = APIRouter()


@router.get("/stores/{store_id}/heatmap")
async def get_store_heatmap(request: Request, store_id: str):
    """
    Get zone activity heatmap for a store.

    Returns activity intensity (0-1) for each zone based on visitor traffic.
    """
    redis = request.app.state.redis

    # Try cache
    cache_key = f"sip:metrics:{store_id}"
    cached = await redis.get(cache_key)

    zones = []
    if cached:
        metrics = json.loads(cached)
        zone_data = metrics.get("zones", [])
        max_visitors = max((z.get("visitors", 0) for z in zone_data), default=1) or 1

        for zone in zone_data:
            zones.append({
                "zone_id": zone.get("zone_id"),
                "zone_name": zone.get("zone_id", "").replace("_", " ").title(),
                "intensity": round(zone.get("visitors", 0) / max_visitors, 2),
                "visitor_count": zone.get("visitors", 0),
                "avg_dwell": zone.get("avg_dwell", 0),
            })

    return {
        "store_id": store_id,
        "zones": zones,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
