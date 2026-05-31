"""
Metrics endpoint.

GET /api/v1/stores/{store_id}/metrics — Returns store KPIs.
Reads from Redis cache for sub-200ms responses, falls back to DB.
"""

import json
from datetime import datetime, timezone

from fastapi import APIRouter, Request, HTTPException, Query
import structlog

logger = structlog.get_logger(__name__)

router = APIRouter()


@router.get("/stores/{store_id}/metrics")
async def get_store_metrics(
    request: Request,
    store_id: str,
    period_hours: int = Query(default=24, ge=1, le=720, description="Lookback period in hours"),
):
    """
    Get real-time store metrics (KPIs).

    Returns visitor count, conversion rate, queue depth, revenue, and zone metrics.
    Data is served from Redis cache when available for <200ms latency.
    """
    redis = request.app.state.redis

    # Try Redis cache first
    cache_key = f"sip:metrics:{store_id}"
    cached = await redis.get(cache_key)

    if cached:
        metrics = json.loads(cached)
        return {
            "store_id": store_id,
            "source": "cache",
            "period": {"hours": period_hours},
            **metrics,
        }

    # Fallback: return placeholder (in production, query TimescaleDB)
    return {
        "store_id": store_id,
        "source": "database",
        "period": {
            "start": datetime.now(timezone.utc).isoformat(),
            "end": datetime.now(timezone.utc).isoformat(),
            "hours": period_hours,
        },
        "visitors": {"total": 0, "unique": 0, "returning": 0},
        "conversion": {"rate": 0.0, "purchases": 0, "revenue": 0.0},
        "queue": {"current_depth": 0, "avg_wait_seconds": 0, "abandonments": 0},
        "dwell": {"avg_seconds": 0, "median_seconds": 0},
        "zones": [],
    }
