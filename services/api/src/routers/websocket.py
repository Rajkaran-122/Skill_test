"""
WebSocket endpoint for real-time dashboard updates.

WS /api/v1/ws/dashboard/{store_id} — Streams live metrics, queue
updates, and anomaly alerts to connected dashboard clients.

Uses Redis Pub/Sub for fan-out across multiple API instances.
"""

import asyncio
import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import structlog

logger = structlog.get_logger(__name__)

router = APIRouter()


@router.websocket("/ws/dashboard/{store_id}")
async def websocket_dashboard(websocket: WebSocket, store_id: str):
    """
    WebSocket endpoint for real-time dashboard data.

    Subscribes to the Redis Pub/Sub channel for the given store
    and forwards all updates to the connected client.
    """
    await websocket.accept()
    logger.info("WebSocket connected", store_id=store_id)

    ws_manager = websocket.app.state.ws_manager
    await ws_manager.connect(store_id, websocket)

    try:
        # Send initial snapshot
        redis = websocket.app.state.redis
        cache_key = f"sip:metrics:{store_id}"
        cached = await redis.get(cache_key)
        if cached:
            await websocket.send_json({
                "type": "INITIAL_SNAPSHOT",
                "store_id": store_id,
                "data": json.loads(cached),
            })

        # Keep connection alive and listen for client messages
        while True:
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=30)
                # Handle client messages (e.g., ping)
                if data == "ping":
                    await websocket.send_text("pong")
            except asyncio.TimeoutError:
                # Send heartbeat
                await websocket.send_json({"type": "HEARTBEAT"})

    except WebSocketDisconnect:
        logger.info("WebSocket disconnected", store_id=store_id)
    except Exception as e:
        logger.error("WebSocket error", store_id=store_id, error=str(e))
    finally:
        await ws_manager.disconnect(store_id, websocket)
