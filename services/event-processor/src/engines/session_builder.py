"""
Session builder engine.

Assembles visitor sessions from discrete events. A session represents
a complete visitor journey: entry → zone visits → queue → purchase → exit.

Sessions are built using a sliding window approach:
- A session starts on VISITOR_ENTER.
- Zone events are appended to the session's zone history.
- A session closes on VISITOR_EXIT or after an inactivity timeout.
"""

import time
from dataclasses import dataclass, field
from datetime import datetime, timezone

import structlog

logger = structlog.get_logger(__name__)


@dataclass
class ActiveSession:
    """An active (in-progress) visitor session."""

    store_id: str
    visitor_id: str
    session_start: datetime
    last_activity: float = field(default_factory=time.time)
    zones_visited: list[dict] = field(default_factory=list)
    is_staff: bool = False
    is_converted: bool = False
    entry_camera: str | None = None
    exit_camera: str | None = None


class SessionBuilder:
    """Builds visitor sessions from event streams."""

    def __init__(self, inactivity_timeout: int = 1800, db_publisher=None, cache_publisher=None):
        self._timeout = inactivity_timeout
        self._sessions: dict[str, ActiveSession] = {}  # visitor_id -> session
        self._db_publisher = db_publisher
        self._cache_publisher = cache_publisher

    async def process_event(self, event_data: dict) -> None:
        """Process a visitor enter/exit event."""
        event_type = event_data.get("event_type")
        visitor_id = event_data.get("visitor_id")
        store_id = event_data.get("store_id")

        if event_type == "VISITOR_ENTER":
            session = ActiveSession(
                store_id=store_id,
                visitor_id=visitor_id,
                session_start=datetime.fromisoformat(event_data["timestamp"]),
                entry_camera=event_data.get("camera_id"),
            )
            self._sessions[visitor_id] = session
            logger.debug("Session started", visitor_id=visitor_id, store_id=store_id)

        elif event_type == "VISITOR_EXIT":
            session = self._sessions.pop(visitor_id, None)
            if session:
                session.exit_camera = event_data.get("camera_id")
                await self._close_session(session)

    async def process_zone_event(self, event_data: dict) -> None:
        """Add a zone visit to the active session."""
        visitor_id = event_data.get("visitor_id")
        session = self._sessions.get(visitor_id)

        if session:
            session.last_activity = time.time()

            if event_data.get("event_type") == "ZONE_ENTER":
                session.zones_visited.append({
                    "zone_id": event_data.get("zone_id"),
                    "entered_at": event_data.get("timestamp"),
                })

            elif event_data.get("event_type") == "ZONE_EXIT":
                # Update the last zone with exit time and dwell
                if session.zones_visited:
                    last_zone = session.zones_visited[-1]
                    if last_zone.get("zone_id") == event_data.get("zone_id"):
                        last_zone["exited_at"] = event_data.get("timestamp")
                        dwell = event_data.get("metadata", {}).get("dwell_seconds")
                        if dwell:
                            last_zone["dwell_seconds"] = dwell

    async def mark_staff(self, event_data: dict) -> None:
        """Mark a session's visitor as staff."""
        visitor_id = event_data.get("visitor_id")
        session = self._sessions.get(visitor_id)
        if session:
            session.is_staff = True

    async def mark_converted(self, event_data: dict) -> None:
        """Mark a session as converted (purchased)."""
        visitor_id = event_data.get("visitor_id")
        session = self._sessions.get(visitor_id)
        if session:
            session.is_converted = True
            logger.info("Session marked as converted", visitor_id=visitor_id)

    async def check_timeouts(self) -> None:
        """Close sessions that have been inactive for too long."""
        now = time.time()
        timed_out = [
            vid for vid, session in self._sessions.items()
            if (now - session.last_activity) > self._timeout
        ]
        for vid in timed_out:
            session = self._sessions.pop(vid)
            await self._close_session(session)
            logger.debug("Session timed out", visitor_id=vid)

    async def _close_session(self, session: ActiveSession) -> None:
        """Finalize and persist a session."""
        duration = None
        if session.session_start:
            duration = int((datetime.now(timezone.utc) - session.session_start).total_seconds())

        session_data = {
            "store_id": session.store_id,
            "visitor_id": session.visitor_id,
            "session_start": session.session_start.isoformat(),
            "session_end": datetime.now(timezone.utc).isoformat(),
            "duration_seconds": duration,
            "zones_visited": session.zones_visited,
            "is_staff": session.is_staff,
            "is_converted": session.is_converted,
            "entry_camera": session.entry_camera,
            "exit_camera": session.exit_camera,
        }

        # Publish to database
        if self._db_publisher:
            await self._db_publisher.publish_session(session_data)

        logger.info(
            "Session closed",
            visitor_id=session.visitor_id,
            duration=duration,
            zones_count=len(session.zones_visited),
            is_converted=session.is_converted,
            is_staff=session.is_staff,
        )

    @property
    def active_count(self) -> int:
        return len(self._sessions)
