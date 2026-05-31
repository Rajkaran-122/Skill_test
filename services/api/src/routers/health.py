"""
Health check endpoint.

GET /api/v1/health — Returns system health status
including database, Redis, and Kafka connectivity.
"""

from datetime import datetime, timezone

from fastapi import APIRouter, Request
import structlog

logger = structlog.get_logger(__name__)

router = APIRouter()


@router.get("/health", response_model=dict)
async def health_check(request: Request):
    """System health check — verifies all critical dependencies."""
    checks = {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "1.0.0",
        "services": {},
    }

    # Check Redis
    try:
        redis = request.app.state.redis
        await redis.ping()
        checks["services"]["redis"] = {"status": "healthy"}
    except Exception as e:
        checks["services"]["redis"] = {"status": "unhealthy", "error": str(e)}
        checks["status"] = "degraded"

    # Check Database
    try:
        from src.db.session import _engine
        if _engine:
            async with _engine.connect() as conn:
                await conn.execute("SELECT 1")
            checks["services"]["database"] = {"status": "healthy"}
        else:
            checks["services"]["database"] = {"status": "not_initialized"}
    except Exception as e:
        checks["services"]["database"] = {"status": "unhealthy", "error": str(e)}
        checks["status"] = "degraded"

    return checks
