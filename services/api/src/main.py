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
from prometheus_fastapi_instrumentator import Instrumentator

from src.config import APIConfig
from src.db.session import init_db, close_db
from src.routers import events, metrics, funnel, heatmap, anomalies, health, websocket

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
    logger.info("Redis connected")

    # Initialize WebSocket manager
    from src.services.websocket_manager import WebSocketManager
    app.state.ws_manager = WebSocketManager(app.state.redis)
    await app.state.ws_manager.start()
    logger.info("WebSocket manager started")

    logger.info("SIP API ready")

    yield

    # Shutdown
    logger.info("Shutting down SIP API")
    await app.state.ws_manager.stop()
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

    # Register routers
    app.include_router(health.router, prefix="/api/v1", tags=["Health"])
    app.include_router(events.router, prefix="/api/v1", tags=["Events"])
    app.include_router(metrics.router, prefix="/api/v1", tags=["Metrics"])
    app.include_router(funnel.router, prefix="/api/v1", tags=["Funnel"])
    app.include_router(heatmap.router, prefix="/api/v1", tags=["Heatmap"])
    app.include_router(anomalies.router, prefix="/api/v1", tags=["Anomalies"])
    app.include_router(websocket.router, prefix="/api/v1", tags=["WebSocket"])

    return app


# Application instance
app = create_app()
