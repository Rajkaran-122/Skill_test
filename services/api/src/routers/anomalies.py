from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import structlog

from src.db.session import get_db
from src.core.security import get_current_user, TokenData
from src.db.models import AnomalyDB

logger = structlog.get_logger(__name__)

router = APIRouter()


@router.get("/stores/{store_id}/anomalies")
async def get_store_anomalies(
    store_id: str,
    include_resolved: bool = Query(default=False, description="Include resolved anomalies"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get active anomalies for a store from Postgres.
    """
    query = select(AnomalyDB).where(AnomalyDB.store_id == store_id)
    
    if not include_resolved:
        query = query.where(AnomalyDB.resolved == False)
        
    query = query.order_by(AnomalyDB.timestamp.desc())

    result = await db.execute(query)
    anomalies = result.scalars().all()

    return {
        "store_id": store_id,
        "anomalies": [
            {
                "id": f"ALT-{a.id}",
                "type": a.anomaly_type,
                "severity": a.severity,
                "store": f"Store {store_id[:8]}", # Mock store name
                "zone": "N/A", # Optional zone info
                "time": a.timestamp.strftime("%I:%M %p"),
                "status": "Resolved" if a.resolved else "Active",
                "desc": a.description
            } for a in anomalies
        ],
        "total": len(anomalies),
    }

@router.post("/anomalies/{anomaly_id}/resolve")
async def resolve_anomaly(
    anomaly_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Mark an anomaly as resolved. 
    Accepts anomaly_id in format 'ALT-5' or just '5'.
    """
    # Strip prefix if it exists
    raw_id = anomaly_id.replace("ALT-", "")
    
    try:
        aid = int(raw_id)
    except ValueError:
        return {"success": False, "message": "Invalid anomaly ID format."}
        
    query = select(AnomalyDB).where(AnomalyDB.id == aid)
    result = await db.execute(query)
    anomaly = result.scalar_one_or_none()
    
    if not anomaly:
        return {"success": False, "message": "Anomaly not found."}
        
    anomaly.resolved = True
    await db.commit()
    
    return {"success": True, "message": "Anomaly resolved successfully."}
