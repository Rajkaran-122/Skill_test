"""
WebSocket connection manager with Redis Pub/Sub fan-out.

Manages WebSocket connections per store and uses Redis Pub/Sub
to receive real-time updates from the event processor. This
enables horizontal scaling of API instances — all instances
receive the same updates via Redis.
"""

import asyncio
import json
from collections import defaultdict

import structlog
from fastapi import WebSocket

logger = structlog.get_logger(__name__)


class WebSocketManager:
    """Manages WebSocket connections with Redis Pub/Sub fan-out."""

    def __init__(self, redis):
        self._redis = redis
        self._connections: dict[str, set[WebSocket]] = defaultdict(set)
        self._pubsub = None
        self._listener_task = None

    async def start(self) -> None:
        """Start the Redis Pub/Sub listener."""
        self._pubsub = self._redis.pubsub()
        self._listener_task = asyncio.create_task(self._listen())
        logger.info("WebSocket manager started")

    async def stop(self) -> None:
        """Stop the manager and close all connections."""
        if self._listener_task:
            self._listener_task.cancel()
        if self._pubsub:
            await self._pubsub.unsubscribe()
            await self._pubsub.close()
        logger.info("WebSocket manager stopped")

    async def connect(self, store_id: str, websocket: WebSocket) -> None:
        """Register a new WebSocket connection for a store."""
        self._connections[store_id].add(websocket)

        # Subscribe to the store's Redis channel if this is the first connection
        if len(self._connections[store_id]) == 1 and self._pubsub:
            channel = f"sip:dashboard:{store_id}"
            await self._pubsub.subscribe(channel)
            logger.info("Subscribed to Redis channel", channel=channel)

        logger.debug(
            "WebSocket connected",
            store_id=store_id,
            total_connections=len(self._connections[store_id]),
        )

    async def disconnect(self, store_id: str, websocket: WebSocket) -> None:
        """Remove a WebSocket connection."""
        self._connections[store_id].discard(websocket)

        # Unsubscribe if no more connections for this store
        if not self._connections[store_id]:
            if self._pubsub:
                channel = f"sip:dashboard:{store_id}"
                await self._pubsub.unsubscribe(channel)
            del self._connections[store_id]

    async def _listen(self) -> None:
        """Listen for Redis Pub/Sub messages and broadcast to WebSocket clients."""
        try:
            async for message in self._pubsub.listen():
                if message["type"] != "message":
                    continue

                channel = message["channel"]
                if isinstance(channel, bytes):
                    channel = channel.decode("utf-8")

                # Extract store_id from channel name: "sip:dashboard:{store_id}"
                parts = channel.split(":")
                if len(parts) >= 3:
                    store_id = parts[2]
                else:
                    continue

                data = message["data"]
                if isinstance(data, bytes):
                    data = data.decode("utf-8")

                # Broadcast to all connected WebSocket clients for this store
                await self._broadcast(store_id, data)

        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error("Redis Pub/Sub listener error", error=str(e))

    async def broadcast_local(self, store_id: str, data: str) -> None:
        """Broadcast data locally without Redis (for local dev)."""
        await self._broadcast(store_id, data)

    async def _broadcast(self, store_id: str, data: str) -> None:
        """Send data to all WebSocket clients for a store."""
        connections = self._connections.get(store_id, set())
        if not connections:
            return

        dead_connections = set()
        for ws in connections:
            try:
                await ws.send_text(data)
            except Exception:
                dead_connections.add(ws)

        # Clean up dead connections
        for ws in dead_connections:
            self._connections[store_id].discard(ws)

    @property
    def total_connections(self) -> int:
        """Total active WebSocket connections across all stores."""
        return sum(len(conns) for conns in self._connections.values())
