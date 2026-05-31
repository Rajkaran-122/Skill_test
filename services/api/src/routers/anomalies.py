"""
Anomalies endpoint.

GET /api/v1/stores/{store_id}/anomalies — Returns active anomalies.
"""

import json
from fastapi import APIRouter, Request, Query
import structlog

logger = structlog.get_logger(__name__)

router = APIRouter()


@router.get("/stores/{store_id}/anomalies")
async def get_store_anomalies(
    request: Request,
    store_id: str,
    include_resolved: bool = Query(default=False, description="Include resolved anomalies"),
):
    """
    Get active anomalies for a store.

    Returns queue spikes, conversion drops, dead zones, and camera failures.
    """
    redis = request.app.state.redis

    cache_key = f"sip:anomalies:{store_id}"
    cached = await redis.get(cache_key)
    anomalies = json.loads(cached) if cached else []

    if not include_resolved:
        anomalies = [a for a in anomalies if not a.get("is_resolved", False)]

    return {
        "store_id": store_id,
        "anomalies": anomalies,
        "total": len(anomalies),
    }
