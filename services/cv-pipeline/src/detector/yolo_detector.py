"""
YOLO-based person detector implementation.

Uses the Ultralytics library to run YOLO inference.
Supports YOLO11, YOLO26, or any Ultralytics-compatible model
by changing the model path in configuration.
"""

import structlog
import numpy as np

from src.config import DetectorConfig
from src.detector.base import BaseDetector
from src.events.schemas import BoundingBox, Detection

logger = structlog.get_logger(__name__)


class YOLODetector(BaseDetector):
    """YOLO person detector using the Ultralytics library."""

    def __init__(self, config: DetectorConfig):
        self._config = config
        self._model = None
        self._model_name = config.model

    def initialize(self) -> None:
        """Load YOLO model weights."""
        from ultralytics import YOLO

        logger.info(
            "Loading YOLO model",
            model=self._config.model,
            device=self._config.device,
            confidence=self._config.confidence_threshold,
        )

        self._model = YOLO(self._config.model)

        # Move model to specified device
        if self._config.device != "cpu":
            self._model.to(self._config.device)

        logger.info("YOLO model loaded successfully", model=self._config.model)

    def warmup(self) -> None:
        """Run a dummy inference pass to warm up the model."""
        if self._model is None:
            raise RuntimeError("Model not initialized. Call initialize() first.")

        dummy_frame = np.zeros((640, 640, 3), dtype=np.uint8)
        self._model.predict(
            dummy_frame,
            conf=self._config.confidence_threshold,
            classes=[self._config.person_class_id],
            verbose=False,
        )
        logger.info("YOLO model warmup complete")

    def detect(self, frame: np.ndarray) -> list[Detection]:
        """
        Detect persons in a frame using YOLO.

        Args:
            frame: BGR image as numpy array (H, W, 3).

        Returns:
            List of Detection objects for persons only.
        """
        if self._model is None:
            raise RuntimeError("Model not initialized. Call initialize() first.")

        results = self._model.predict(
            frame,
            conf=self._config.confidence_threshold,
            classes=[self._config.person_class_id],
            imgsz=self._config.img_size,
            half=self._config.half_precision,
            verbose=False,
        )

        detections: list[Detection] = []

        for result in results:
            if result.boxes is None or len(result.boxes) == 0:
                continue

            boxes = result.boxes.xyxy.cpu().numpy()
            confidences = result.boxes.conf.cpu().numpy()
            class_ids = result.boxes.cls.cpu().numpy().astype(int)

            for box, conf, cls_id in zip(boxes, confidences, class_ids):
                if cls_id != self._config.person_class_id:
                    continue

                detection = Detection(
                    bbox=BoundingBox(
                        x1=float(box[0]),
                        y1=float(box[1]),
                        x2=float(box[2]),
                        y2=float(box[3]),
                    ),
                    confidence=float(conf),
                    class_id=int(cls_id),
                )
                detections.append(detection)

        return detections

    @property
    def model_name(self) -> str:
        return self._model_name
