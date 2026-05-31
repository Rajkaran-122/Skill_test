"""
Staff vs. Customer classifier.

Uses two complementary strategies to identify store employees:

1. **Appearance-based**: Detects uniform colors in person crops using HSV
   color matching. If the dominant color of a person's clothing matches
   the configured staff uniform color, they are flagged as staff.

2. **Behavioral**: Tracks long-duration presence and frequent checkout
   zone visits. If a person has been present for longer than the threshold
   or frequently accesses the billing area, they are classified as staff.

Staff are excluded from customer metrics (visitor count, conversion rate, etc.)
"""

import time
from dataclasses import dataclass, field

import structlog
import numpy as np
import cv2

from src.config import StaffClassifierConfig

logger = structlog.get_logger(__name__)


@dataclass
class PersonBehavior:
    """Tracks behavioral patterns for a visitor."""

    visitor_id: str
    first_seen: float = field(default_factory=time.time)
    last_seen: float = field(default_factory=time.time)
    checkout_zone_visits: int = 0
    uniform_score: float = 0.0  # Running average of uniform detection
    classification_count: int = 0

    @property
    def presence_minutes(self) -> float:
        return (self.last_seen - self.first_seen) / 60.0


class StaffClassifier:
    """Classifies persons as staff or customers."""

    def __init__(self, config: StaffClassifierConfig):
        self._config = config
        self._behaviors: dict[str, PersonBehavior] = {}

    def classify(
        self,
        visitor_id: str,
        person_crop: np.ndarray,
        current_zone: str | None = None,
    ) -> bool:
        """
        Classify a person as staff or customer.

        Args:
            visitor_id: The person's visitor ID.
            person_crop: Cropped person image (H, W, 3) BGR.
            current_zone: The zone the person is currently in (e.g., 'CHECKOUT').

        Returns:
            True if the person is classified as staff.
        """
        # Get or create behavior tracker
        if visitor_id not in self._behaviors:
            self._behaviors[visitor_id] = PersonBehavior(visitor_id=visitor_id)

        behavior = self._behaviors[visitor_id]
        behavior.last_seen = time.time()
        behavior.classification_count += 1

        # Track checkout zone visits
        if current_zone and current_zone.upper() in ("CHECKOUT", "BILLING", "COUNTER"):
            behavior.checkout_zone_visits += 1

        # Appearance check: detect uniform color
        uniform_detected = self._detect_uniform(person_crop)
        alpha = 0.2
        behavior.uniform_score = alpha * (1.0 if uniform_detected else 0.0) + (1 - alpha) * behavior.uniform_score

        # Decision logic: combine appearance + behavior
        is_staff = False

        # Strong appearance signal
        if behavior.uniform_score > 0.6:
            is_staff = True

        # Behavioral: long presence
        if behavior.presence_minutes >= self._config.min_presence_minutes:
            is_staff = True

        # Behavioral: frequent checkout access
        if behavior.checkout_zone_visits >= self._config.checkout_zone_frequency_threshold:
            is_staff = True

        if is_staff and behavior.classification_count <= 1:
            logger.info(
                "Staff detected",
                visitor_id=visitor_id,
                uniform_score=round(behavior.uniform_score, 2),
                presence_min=round(behavior.presence_minutes, 1),
                checkout_visits=behavior.checkout_zone_visits,
            )

        return is_staff

    def _detect_uniform(self, person_crop: np.ndarray) -> bool:
        """
        Check if the person crop contains the staff uniform color.

        Uses the middle third of the person crop (torso area)
        and checks for the dominant color against configured uniform colors.
        """
        if person_crop is None or person_crop.size == 0:
            return False

        h, w = person_crop.shape[:2]
        if h < 10 or w < 10:
            return False

        # Extract torso region (middle third vertically)
        torso_top = h // 3
        torso_bottom = 2 * h // 3
        torso = person_crop[torso_top:torso_bottom, :, :]

        # Convert to HSV
        hsv = cv2.cvtColor(torso, cv2.COLOR_BGR2HSV)

        # Check against each configured uniform color
        tolerance = self._config.color_tolerance
        for target_hsv in self._config.uniform_colors_hsv:
            target_h, target_s, target_v = target_hsv

            lower = np.array([
                max(0, target_h - tolerance),
                max(0, target_s - 50),
                max(0, target_v - 50),
            ])
            upper = np.array([
                min(179, target_h + tolerance),
                min(255, target_s + 50),
                min(255, target_v + 50),
            ])

            mask = cv2.inRange(hsv, lower, upper)
            ratio = np.sum(mask > 0) / mask.size

            if ratio > 0.3:  # >30% of torso matches uniform color
                return True

        return False

    def get_behavior(self, visitor_id: str) -> PersonBehavior | None:
        """Get behavioral data for a visitor."""
        return self._behaviors.get(visitor_id)

    def clear(self) -> None:
        """Reset all behavioral tracking."""
        self._behaviors.clear()
