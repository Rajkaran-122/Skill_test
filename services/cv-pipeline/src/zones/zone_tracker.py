"""
Zone tracking module.

Tracks which zone each person is in using polygon-based point-in-polygon
tests on person centroids. Generates ZONE_ENTER, ZONE_EXIT, and ZONE_DWELL
events as persons move between store zones.

Zones are defined as polygons (list of (x, y) vertices) configured per store.
"""

import time
from dataclasses import dataclass, field

import structlog
import numpy as np

from src.events.schemas import BoundingBox, ZoneDwellRecord

logger = structlog.get_logger(__name__)


@dataclass
class ZoneDefinition:
    """A zone defined by a polygon on the store floor plan."""

    zone_id: str
    zone_code: str
    name: str
    zone_type: str  # 'entrance', 'aisle', 'checkout', 'display'
    polygon: list[tuple[float, float]]  # List of (x, y) vertices


@dataclass
class VisitorZoneState:
    """Tracks a visitor's current zone and dwell records."""

    visitor_id: str
    current_zone: str | None = None
    zone_enter_time: float | None = None
    dwell_records: list[ZoneDwellRecord] = field(default_factory=list)
    zone_history: list[str] = field(default_factory=list)


@dataclass
class ZoneTransition:
    """Represents a zone transition event."""

    visitor_id: str
    from_zone: str | None
    to_zone: str | None
    transition_type: str  # 'enter', 'exit', 'transfer'
    dwell_seconds: float | None = None


class ZoneTracker:
    """
    Tracks person positions against store zone polygons.

    Uses ray-casting algorithm for point-in-polygon detection.
    """

    def __init__(self):
        self._zones: list[ZoneDefinition] = []
        self._visitor_states: dict[str, VisitorZoneState] = {}

    def configure_zones(self, zones: list[ZoneDefinition]) -> None:
        """Load zone definitions for the store."""
        self._zones = zones
        logger.info("Zones configured", count=len(zones), zones=[z.zone_code for z in zones])

    def update(
        self,
        visitor_id: str,
        bbox: BoundingBox,
    ) -> list[ZoneTransition]:
        """
        Update zone tracking for a visitor.

        Args:
            visitor_id: The visitor's ID.
            bbox: Current bounding box of the visitor.

        Returns:
            List of zone transitions that occurred (enter, exit, transfer).
        """
        # Determine which zone the person's centroid is in
        cx, cy = bbox.center
        current_zone = self._find_zone(cx, cy)

        # Get or create visitor state
        if visitor_id not in self._visitor_states:
            self._visitor_states[visitor_id] = VisitorZoneState(visitor_id=visitor_id)

        state = self._visitor_states[visitor_id]
        transitions: list[ZoneTransition] = []
        now = time.time()

        if current_zone != state.current_zone:
            # Zone changed — generate transition events
            if state.current_zone is not None:
                # Exiting previous zone
                dwell = now - state.zone_enter_time if state.zone_enter_time else None
                transitions.append(
                    ZoneTransition(
                        visitor_id=visitor_id,
                        from_zone=state.current_zone,
                        to_zone=current_zone,
                        transition_type="exit",
                        dwell_seconds=dwell,
                    )
                )

            if current_zone is not None:
                # Entering new zone
                transitions.append(
                    ZoneTransition(
                        visitor_id=visitor_id,
                        from_zone=state.current_zone,
                        to_zone=current_zone,
                        transition_type="enter",
                    )
                )
                state.zone_history.append(current_zone)

            state.current_zone = current_zone
            state.zone_enter_time = now

        return transitions

    def get_visitor_zone(self, visitor_id: str) -> str | None:
        """Get the current zone of a visitor."""
        state = self._visitor_states.get(visitor_id)
        return state.current_zone if state else None

    def get_zone_occupancy(self) -> dict[str, int]:
        """Get the number of visitors in each zone."""
        occupancy: dict[str, int] = {z.zone_code: 0 for z in self._zones}
        for state in self._visitor_states.values():
            if state.current_zone and state.current_zone in occupancy:
                occupancy[state.current_zone] += 1
        return occupancy

    def get_visitor_journey(self, visitor_id: str) -> list[str]:
        """Get the ordered list of zones a visitor has been in."""
        state = self._visitor_states.get(visitor_id)
        return state.zone_history if state else []

    def _find_zone(self, x: float, y: float) -> str | None:
        """Find which zone contains the point (x, y)."""
        for zone in self._zones:
            if self._point_in_polygon(x, y, zone.polygon):
                return zone.zone_code
        return None

    @staticmethod
    def _point_in_polygon(x: float, y: float, polygon: list[tuple[float, float]]) -> bool:
        """
        Ray-casting algorithm for point-in-polygon detection.

        Args:
            x, y: Point coordinates.
            polygon: List of (x, y) vertices.

        Returns:
            True if point is inside the polygon.
        """
        n = len(polygon)
        if n < 3:
            return False

        inside = False
        j = n - 1

        for i in range(n):
            xi, yi = polygon[i]
            xj, yj = polygon[j]

            if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi) + xi):
                inside = not inside

            j = i

        return inside

    def remove_visitor(self, visitor_id: str) -> None:
        """Remove a visitor from zone tracking (e.g., on exit)."""
        self._visitor_states.pop(visitor_id, None)

    def clear(self) -> None:
        """Reset all zone tracking state."""
        self._visitor_states.clear()
