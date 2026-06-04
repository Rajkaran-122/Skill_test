from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import date
import structlog

from src.db.session import get_db
from src.core.security import get_current_user, TokenData
from src.db.models import StoreSessionDB, VisitorEventDB

logger = structlog.get_logger(__name__)

router = APIRouter()


@router.get("/stores/{store_id}/funnel")
async def get_store_funnel(
    store_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get the store conversion funnel from the PostgreSQL DB.
    """
    today = date.today()

    # Total Entries (Sessions today)
    entries_query = select(func.count(StoreSessionDB.id)).where(
        StoreSessionDB.store_id == store_id,
        func.date(StoreSessionDB.entry_time) == today
    )
    entries = (await db.execute(entries_query)).scalar() or 0

    # Browse: Visitors who entered any zone
    browse_query = select(func.count(func.distinct(VisitorEventDB.visitor_id))).where(
        VisitorEventDB.store_id == store_id,
        func.date(VisitorEventDB.timestamp) == today,
        VisitorEventDB.event_type == "ZONE_ENTER"
    )
    browse = (await db.execute(browse_query)).scalar() or 0

    # Engage: Visitors who dwelled (For now, use Browse * 0.7 if no complex dwell calc)
    engage = int(browse * 0.7)

    # Queue: Visitors who hit CHECKOUT zone
    queue_query = select(func.count(func.distinct(VisitorEventDB.visitor_id))).where(
        VisitorEventDB.store_id == store_id,
        func.date(VisitorEventDB.timestamp) == today,
        VisitorEventDB.zone_id == "CHECKOUT"
    )
    queue = (await db.execute(queue_query)).scalar() or 0

    # Purchase: Converted sessions
    purchase_query = select(func.count(StoreSessionDB.id)).where(
        StoreSessionDB.store_id == store_id,
        func.date(StoreSessionDB.entry_time) == today,
        StoreSessionDB.converted == True
    )
    purchase = (await db.execute(purchase_query)).scalar() or 0

    # Calculate percentages
    def pct(count):
        return round((count / entries * 100), 1) if entries > 0 else 0.0

    return {
        "store_id": store_id,
        "funnel": [
            {"stage": "Entry", "count": entries, "percentage": 100.0 if entries > 0 else 0.0},
            {"stage": "Browse", "count": browse, "percentage": pct(browse)},
            {"stage": "Engage", "count": engage, "percentage": pct(engage)},
            {"stage": "Queue", "count": queue, "percentage": pct(queue)},
            {"stage": "Purchase", "count": purchase, "percentage": pct(purchase)},
        ],
    }
