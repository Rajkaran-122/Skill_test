"""
CV Pipeline Orchestrator — Main entry point.

Orchestrates the full computer vision pipeline:
  Video → Detect → Track → Re-ID → Classify → Zone Track → Queue Detect → Events → Kafka

This module:
1. Reads frames from a video source (file, webcam, or RTSP stream).
2. Runs YOLO person detection on each frame.
3. Tracks persons across frames with ByteTrack.
4. Re-identifies persons across cameras with OSNet.
5. Classifies staff vs. customers.
6. Tracks zone entry/exit/dwell.
7. Detects queue formations.
8. Generates and publishes events to Kafka.
"""

import asyncio
import signal
import time

import cv2
import numpy as np
import structlog
from prometheus_client import Counter, Gauge, Histogram, start_http_server

from src.config import PipelineConfig
from src.classifier.staff_classifier import StaffClassifier
from src.detector.yolo_detector import YOLODetector
from src.events.event_generator import EventGenerator
from src.events.producer import EventProducer
from src.events.schemas import IdentifiedPerson
from src.queue.queue_detector import QueueDetector
from src.reid.gallery import FeatureGallery
from src.reid.osnet import OSNetReID
from src.tracker.bytetrack import ByteTrackTracker
from src.zones.zone_tracker import ZoneDefinition, ZoneTracker

logger = structlog.get_logger(__name__)

# ---- Prometheus Metrics ----
FRAMES_PROCESSED = Counter("sip_cv_frames_processed_total", "Total frames processed")
DETECTIONS_COUNT = Counter("sip_cv_detections_total", "Total person detections")
EVENTS_GENERATED = Counter("sip_cv_events_generated_total", "Total events generated", ["event_type"])
ACTIVE_TRACKS = Gauge("sip_cv_active_tracks", "Currently active tracks")
GALLERY_SIZE = Gauge("sip_cv_gallery_size", "Feature gallery size")
FRAME_LATENCY = Histogram("sip_cv_frame_latency_seconds", "Per-frame processing latency")
FPS_GAUGE = Gauge("sip_cv_fps", "Current processing FPS")


class CVPipeline:
    """
    Main CV Pipeline orchestrator.

    Processes video frames through the full detection → tracking → re-id →
    classification → zone/queue tracking → event generation pipeline.
    """

    def __init__(self, config: PipelineConfig):
        self._config = config
        self._running = False

        # Initialize components
        self._detector = YOLODetector(config.detector)
        self._tracker = ByteTrackTracker(config.tracker)
        self._reid = OSNetReID(config.reid)
        self._gallery = FeatureGallery(self._reid, config.reid)
        self._staff_classifier = StaffClassifier(config.staff)
        self._zone_tracker = ZoneTracker()
        self._queue_detector = QueueDetector(config.queue)
        self._event_generator = EventGenerator(config)
        self._producer = EventProducer(config.kafka)

        # Frame counter for heartbeat
        self._frame_count = 0
        self._heartbeat_interval = 300  # Send heartbeat every 300 frames

    async def initialize(self) -> None:
        """Initialize all pipeline components."""
        logger.info("Initializing CV pipeline", store_id=self._config.store_id)

        # Start Prometheus metrics server
        start_http_server(self._config.metrics_port)
        logger.info("Prometheus metrics server started", port=self._config.metrics_port)

        # Initialize CV components
        self._detector.initialize()
        self._detector.warmup()
        self._tracker.initialize()
        self._reid.initialize()

        # Configure zones (loaded from config or database)
        # For development, use sample zones
        sample_zones = [
            ZoneDefinition("z1", "ENTRANCE", "Main Entrance", "entrance", [(0, 0), (200, 0), (200, 150), (0, 150)]),
            ZoneDefinition("z2", "SKINCARE", "Skincare", "aisle", [(200, 0), (500, 0), (500, 300), (200, 300)]),
            ZoneDefinition("z3", "ELECTRONICS", "Electronics", "aisle", [(500, 0), (800, 0), (800, 300), (500, 300)]),
            ZoneDefinition("z4", "CHECKOUT", "Checkout", "checkout", [(400, 300), (800, 300), (800, 450), (400, 450)]),
            ZoneDefinition("z5", "EXIT", "Main Exit", "entrance", [(600, 450), (800, 450), (800, 600), (600, 600)]),
        ]
        self._zone_tracker.configure_zones(sample_zones)

        # Start Kafka producer
        await self._producer.start()

        logger.info("CV pipeline initialized successfully")

    async def run(self) -> None:
        """Run the pipeline on the configured video source."""
        self._running = True

        # Open video source
        source = self._config.video.source
        if source.isdigit():
            source = int(source)

        cap = cv2.VideoCapture(source)
        if not cap.isOpened():
            logger.error("Failed to open video source", source=self._config.video.source)
            return

        target_fps = self._config.video.fps
        frame_interval = 1.0 / target_fps

        logger.info(
            "Pipeline running",
            source=self._config.video.source,
            target_fps=target_fps,
        )

        try:
            while self._running:
                start_time = time.time()

                # Offload blocking I/O to thread
                ret, frame = await asyncio.to_thread(cap.read)
                if not ret:
                    # End of video file — loop or stop
                    if isinstance(source, int):
                        # Webcam disconnected
                        logger.warning("Video source disconnected")
                        break
                    else:
                        # Video file ended — loop for simulation
                        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                        continue

                # Process frame through the full pipeline
                await self._process_frame(frame)

                # Frame rate control
                elapsed = time.time() - start_time
                sleep_time = frame_interval - elapsed
                if sleep_time > 0:
                    await asyncio.sleep(sleep_time)

                # Update FPS metric
                actual_fps = 1.0 / max(time.time() - start_time, 0.001)
                FPS_GAUGE.set(actual_fps)

        except asyncio.CancelledError:
            logger.info("Pipeline cancelled")
        finally:
            cap.release()
            await self._producer.flush()
            await self._producer.stop()
            logger.info("Pipeline stopped", total_frames=self._frame_count)

    async def _process_frame(self, frame: np.ndarray) -> None:
        """Process a single video frame through the full pipeline."""
        with FRAME_LATENCY.time():
            self._frame_count += 1

            # 1. Detect persons - Offloaded to thread to prevent blocking event loop
            detections = await asyncio.to_thread(self._detector.detect, frame)
            DETECTIONS_COUNT.inc(len(detections))

            if not detections:
                # Send heartbeat periodically even with no detections
                if self._frame_count % self._heartbeat_interval == 0:
                    heartbeat = self._event_generator.camera_heartbeat()
                    await self._producer.publish(heartbeat)
                return

            # 2. Track persons across frames
            tracked = self._tracker.update(detections, frame)
            ACTIVE_TRACKS.set(self._tracker.active_track_count)

            # 3. Re-identify and classify each tracked person
            events = []
            for person in tracked:
                # Crop person from frame
                x1, y1 = int(max(0, person.bbox.x1)), int(max(0, person.bbox.y1))
                x2, y2 = int(min(frame.shape[1], person.bbox.x2)), int(min(frame.shape[0], person.bbox.y2))

                if x2 <= x1 or y2 <= y1:
                    continue

                person_crop = frame[y1:y2, x1:x2]

                # Re-ID: match against gallery
                visitor_id, is_new, reid_conf = self._gallery.match_or_create(
                    person_crop, track_id=person.track_id
                )
                GALLERY_SIZE.set(self._gallery.size)

                # Get current zone for staff classification
                current_zone = self._zone_tracker.get_visitor_zone(visitor_id)

                # Staff classification
                is_staff = self._staff_classifier.classify(
                    visitor_id, person_crop, current_zone
                )

                identified = IdentifiedPerson(
                    track_id=person.track_id,
                    visitor_id=visitor_id,
                    bbox=person.bbox,
                    confidence=person.confidence,
                    is_staff=is_staff,
                    is_new_visitor=is_new,
                    re_id_confidence=reid_conf,
                )

                # Generate visitor enter event for new visitors
                if is_new and not is_staff:
                    enter_event = self._event_generator.visitor_enter(identified)
                    events.append(enter_event)
                elif is_new and is_staff:
                    staff_event = self._event_generator.staff_detected(identified)
                    events.append(staff_event)
                    self._gallery.mark_as_staff(visitor_id)

                # 4. Zone tracking
                if not is_staff:
                    transitions = self._zone_tracker.update(visitor_id, person.bbox)
                    for transition in transitions:
                        zone_events = self._event_generator.zone_transition(transition)
                        events.extend(zone_events)

            # 5. Queue detection (for checkout zones)
            for queue_zone in self._config.queue.zone_ids:
                # Get persons currently in the queue zone
                persons_in_zone = []
                for person in tracked:
                    visitor_zone = self._zone_tracker.get_visitor_zone(
                        f"VIS_{person.track_id:06d}"  # Simplified mapping
                    )
                    if visitor_zone == queue_zone:
                        persons_in_zone.append(
                            (f"VIS_{person.track_id:06d}", person.bbox)
                        )

                snapshot, abandonments = self._queue_detector.update(queue_zone, persons_in_zone)

                for abandoned_vid in abandonments:
                    abandon_event = self._event_generator.queue_abandon(abandoned_vid, queue_zone)
                    events.append(abandon_event)

            # 6. Publish all events
            for event in events:
                await self._producer.publish(event)
                EVENTS_GENERATED.labels(event_type=event.event_type.value).inc()

            # Periodic heartbeat
            if self._frame_count % self._heartbeat_interval == 0:
                heartbeat = self._event_generator.camera_heartbeat()
                await self._producer.publish(heartbeat)

            FRAMES_PROCESSED.inc()

    def stop(self) -> None:
        """Signal the pipeline to stop."""
        self._running = False
        logger.info("Pipeline stop requested")


async def main():
    """Entry point for the CV pipeline service."""
    # Configure structured logging
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
    )

    config = PipelineConfig()
    pipeline = CVPipeline(config)

    # Handle graceful shutdown
    loop = asyncio.get_event_loop()

    def shutdown_handler():
        pipeline.stop()

    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, shutdown_handler)
        except NotImplementedError:
            # Windows doesn't support add_signal_handler
            pass

    await pipeline.initialize()
    await pipeline.run()


if __name__ == "__main__":
    asyncio.run(main())
