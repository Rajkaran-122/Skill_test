from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime, timezone, date
import structlog

from src.db.session import get_db
from src.core.security import get_current_user, TokenData
from src.db.models import VisitorEventDB

logger = structlog.get_logger(__name__)

router = APIRouter()


@router.get("/stores/{store_id}/heatmap")
async def get_zone_heatmap(
    store_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get zone activity heatmap for a store from Postgres.
    """
    today = date.today()

    # Get visitors per zone
    query = select(
        VisitorEventDB.zone_id,
        func.count(func.distinct(VisitorEventDB.visitor_id)).label("visitors")
    ).where(
        VisitorEventDB.store_id == store_id,
        func.date(VisitorEventDB.timestamp) == today,
        VisitorEventDB.zone_id.is_not(None)
    ).group_by(VisitorEventDB.zone_id)

    result = await db.execute(query)
    zone_data = result.all()

    zones = []
    max_visitors = max((z.visitors for z in zone_data), default=1) or 1

    for row in zone_data:
        zones.append({
            "zone_id": row.zone_id,
            "zone_name": str(row.zone_id).replace("_", " ").title(),
            "intensity": round(row.visitors / max_visitors, 2),
            "visitor_count": row.visitors,
            "avg_dwell": row.visitors * 2, # Mock dwell time calculation
        })

    return {
        "store_id": store_id,
        "zones": zones,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
