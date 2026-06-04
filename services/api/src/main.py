"""
Store Intelligence Platform — FastAPI Application.

This is the main entry point for the API service.
Sets up middleware, routers, database connections, Redis,
and the WebSocket manager.
"""

from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from prometheus_fastapi_instrumentator import Instrumentator

from src.config import APIConfig
from src.db.session import init_db, close_db
from src.routers import events, metrics, funnel, heatmap, anomalies, health, websocket, auth, insights

logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle management."""
    config = APIConfig()

    # Startup
    logger.info("Starting SIP API", environment=config.environment)

    # Initialize database
    await init_db(config.database_url)
    logger.info("Database initialized")

    # Initialize Redis
    import redis.asyncio as aioredis
    app.state.redis = aioredis.from_url(config.redis_url, decode_responses=True)
    
    redis_available = False
    try:
        await app.state.redis.ping()
        logger.info("Redis connected")
        redis_available = True
    except Exception as e:
        logger.warning(f"Redis unavailable, falling back to local mode: {e}")
        app.state.redis = None

    # Initialize WebSocket manager
    from src.services.websocket_manager import WebSocketManager
    app.state.ws_manager = WebSocketManager(app.state.redis)
    if redis_available:
        await app.state.ws_manager.start()
    else:
        from src.services.mock_events import simulate_mock_events
        import asyncio
        app.state.mock_task = asyncio.create_task(simulate_mock_events(app))
    logger.info("WebSocket manager started")

    logger.info("SIP API ready")

    yield

    # Shutdown
    logger.info("Shutting down SIP API")
    if hasattr(app.state, 'mock_task'):
        app.state.mock_task.cancel()
    await app.state.ws_manager.stop()
    if app.state.redis:
        await app.state.redis.close()
    await close_db()
    logger.info("SIP API shutdown complete")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    config = APIConfig()

    app = FastAPI(
        title="Store Intelligence Platform API",
        description="AI-powered retail analytics — transforming CCTV footage into business intelligence.",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # CORS
    origins = [o.strip() for o in config.cors_origins.split(",")]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Prometheus metrics
    Instrumentator().instrument(app).expose(app, endpoint="/metrics")

    # Register routers (for challenge harness)
    app.include_router(health.router, tags=["Health"])
    app.include_router(events.router, tags=["Events"])
    app.include_router(metrics.router, tags=["Metrics"])
    app.include_router(funnel.router, tags=["Funnel"])
    app.include_router(heatmap.router, tags=["Heatmap"])
    app.include_router(anomalies.router, tags=["Anomalies"])
    app.include_router(websocket.router, tags=["WebSocket"])
    
    # Register routers (for the React frontend)
    app.include_router(health.router, prefix="/api/v1", tags=["Health_UI"])
    app.include_router(metrics.router, prefix="/api/v1", tags=["Metrics_UI"])
    app.include_router(funnel.router, prefix="/api/v1", tags=["Funnel_UI"])
    app.include_router(heatmap.router, prefix="/api/v1", tags=["Heatmap_UI"])
    app.include_router(anomalies.router, prefix="/api/v1", tags=["Anomalies_UI"])
    app.include_router(insights.router, prefix="/api/v1", tags=["Insights_UI"])
    app.include_router(websocket.router, prefix="/api/v1", tags=["WebSocket_UI"])
    app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])

    # Mount static CCTV footage
    import os
    footage_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../CCTV Footage"))
    if os.path.exists(footage_path):
        app.mount("/footage", StaticFiles(directory=footage_path), name="footage")
    else:
        logger.warning(f"CCTV Footage directory not found at {footage_path}")

    return app


# Application instance
app = create_app()
