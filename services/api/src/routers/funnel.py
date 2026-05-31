"""
Conversion funnel endpoint.

GET /api/v1/stores/{store_id}/funnel — Returns the conversion funnel.
Entry → Browse → Engage → Queue → Purchase
"""

from fastapi import APIRouter, Request
import structlog

logger = structlog.get_logger(__name__)

router = APIRouter()


@router.get("/stores/{store_id}/funnel")
async def get_conversion_funnel(request: Request, store_id: str):
    """
    Get the store conversion funnel.

    Shows visitor drop-off at each stage:
    Entry → Browse (visit any zone) → Engage (dwell >60s) → Queue → Purchase
    """
    # In production, computed from sessions table
    # Returning sample structure
    return {
        "store_id": store_id,
        "funnel": [
            {"stage": "Entry", "count": 0, "percentage": 100.0},
            {"stage": "Browse", "count": 0, "percentage": 0.0},
            {"stage": "Engage", "count": 0, "percentage": 0.0},
            {"stage": "Queue", "count": 0, "percentage": 0.0},
            {"stage": "Purchase", "count": 0, "percentage": 0.0},
        ],
    }
