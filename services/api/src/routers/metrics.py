from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime, date

from src.db.session import get_db
from src.core.security import get_current_user, TokenData
from src.db.models import StoreSessionDB, AnomalyDB

router = APIRouter()

@router.get("/stores/{store_id}/metrics")
async def get_store_metrics(
    store_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get aggregated KPIs from PostgreSQL database.
    """
    today = date.today()
    
    # Visitors Today
    visitors_query = select(func.count(StoreSessionDB.id)).where(
        StoreSessionDB.store_id == store_id,
        func.date(StoreSessionDB.entry_time) == today
    )
    visitors_res = await db.execute(visitors_query)
    visitors_today = visitors_res.scalar() or 0

    # Conversion Rate (All time for now, or today)
    converted_query = select(func.count(StoreSessionDB.id)).where(
        StoreSessionDB.store_id == store_id,
        func.date(StoreSessionDB.entry_time) == today,
        StoreSessionDB.converted == True
    )
    converted_res = await db.execute(converted_query)
    converted_today = converted_res.scalar() or 0
    
    conversion_rate = (converted_today / visitors_today * 100) if visitors_today > 0 else 0.0

    # Mock Revenue based on conversions * average order value (e.g. ₹3,500)
    revenue = converted_today * 3500

    # Active Alerts
    alerts_query = select(func.count(AnomalyDB.id)).where(
        AnomalyDB.store_id == store_id,
        AnomalyDB.resolved == False
    )
    alerts_res = await db.execute(alerts_query)
    active_alerts = alerts_res.scalar() or 0

    return {
        "store_id": store_id,
        "kpis": {
            "visitors_today": visitors_today,
            "visitors_change": 5.2, # Mock trend
            "conversion_rate": round(conversion_rate, 1),
            "conversion_change": 1.1, # Mock trend
            "revenue": revenue,
            "revenue_change": 2.3, # Mock trend
            "queue_depth": 5, # Mock, since queue requires real-time spatial analysis
            "queue_change": -2.0,
            "active_alerts": active_alerts,
            "alerts_change": 0.0
        },
        "visitor_trend": [
            {"time": "09:00", "visitors": int(visitors_today * 0.1), "purchases": int(converted_today * 0.1)},
            {"time": "12:00", "visitors": int(visitors_today * 0.4), "purchases": int(converted_today * 0.4)},
            {"time": "15:00", "visitors": int(visitors_today * 0.3), "purchases": int(converted_today * 0.3)},
            {"time": "18:00", "visitors": int(visitors_today * 0.2), "purchases": int(converted_today * 0.2)}
        ]
    }
