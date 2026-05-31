"""
Store Intelligence Platform — CV Pipeline Configuration.

Centralized configuration using Pydantic Settings.
All config values are loaded from environment variables.
"""

from pydantic_settings import BaseSettings
from pydantic import Field


class KafkaConfig(BaseSettings):
    """Kafka producer configuration."""

    bootstrap_servers: str = Field(default="localhost:9092", alias="KAFKA_BOOTSTRAP_SERVERS")
    security_protocol: str = Field(default="PLAINTEXT", alias="KAFKA_SECURITY_PROTOCOL")
    batch_size: int = Field(default=50, description="Number of events to batch before publishing")
    linger_ms: int = Field(default=100, description="Max time to wait for batch to fill (ms)")

    # Topic names
    visitor_topic: str = "visitor-events"
    zone_topic: str = "zone-events"
    queue_topic: str = "queue-events"
    conversion_topic: str = "conversion-events"
    anomaly_topic: str = "anomaly-events"
    dashboard_topic: str = "dashboard-events"


class DetectorConfig(BaseSettings):
    """YOLO detector configuration."""

    model: str = Field(default="yolo11n.pt", alias="YOLO_MODEL")
    confidence_threshold: float = Field(default=0.5, alias="YOLO_CONFIDENCE_THRESHOLD")
    device: str = Field(default="cpu", alias="YOLO_DEVICE")
    person_class_id: int = Field(default=0, description="COCO class ID for 'person'")
    img_size: int = Field(default=640, description="Input image size for YOLO")
    half_precision: bool = Field(default=False, description="Use FP16 inference (GPU only)")


class TrackerConfig(BaseSettings):
    """ByteTrack tracker configuration."""

    track_thresh: float = Field(default=0.5, alias="BYTETRACK_TRACK_THRESH")
    match_thresh: float = Field(default=0.8, alias="BYTETRACK_MATCH_THRESH")
    track_buffer: int = Field(default=30, description="Frames to keep lost tracks alive")
    frame_rate: int = Field(default=20, description="Video frame rate for Kalman filter")


class ReIDConfig(BaseSettings):
    """OSNet Re-Identification configuration."""

    model: str = Field(default="osnet_x1_0", alias="OSNET_MODEL")
    similarity_threshold: float = Field(default=0.7, alias="OSNET_SIMILARITY_THRESHOLD")
    gallery_ttl_seconds: int = Field(default=7200, alias="REID_GALLERY_TTL_SECONDS")
    gallery_max_size: int = Field(default=10000, alias="REID_GALLERY_MAX_SIZE")
    feature_dim: int = Field(default=512, description="OSNet feature embedding dimension")


class StaffClassifierConfig(BaseSettings):
    """Staff classification configuration."""

    # Appearance-based
    uniform_colors_hsv: list[tuple[int, int, int]] = Field(
        default=[(120, 100, 100)],
        description="HSV color ranges for staff uniforms",
    )
    color_tolerance: int = Field(default=30, description="Color matching tolerance in HSV space")

    # Behavioral
    min_presence_minutes: int = Field(default=30, description="Minimum presence to flag as staff")
    checkout_zone_frequency_threshold: int = Field(
        default=5, description="Min checkout zone visits to flag as staff"
    )


class QueueConfig(BaseSettings):
    """Queue detection configuration."""

    zone_ids: list[str] = Field(default=["CHECKOUT"], alias="QUEUE_ZONE_IDS")
    alert_threshold: int = Field(default=10, alias="QUEUE_ALERT_THRESHOLD")
    abandon_timeout_seconds: int = Field(default=300, alias="QUEUE_ABANDON_TIMEOUT_SECONDS")
    min_cluster_size: int = Field(default=3, description="Minimum people to form a queue")
    max_person_spacing: float = Field(default=150.0, description="Max pixel distance between queue members")


class VideoConfig(BaseSettings):
    """Video source configuration."""

    source: str = Field(default="0", alias="VIDEO_SOURCE")
    fps: int = Field(default=20, alias="VIDEO_FPS")
    buffer_size: int = Field(default=10, description="Frame buffer size")


class PipelineConfig(BaseSettings):
    """Root configuration aggregating all sub-configs."""

    # Sub-configs
    kafka: KafkaConfig = Field(default_factory=KafkaConfig)
    detector: DetectorConfig = Field(default_factory=DetectorConfig)
    tracker: TrackerConfig = Field(default_factory=TrackerConfig)
    reid: ReIDConfig = Field(default_factory=ReIDConfig)
    staff: StaffClassifierConfig = Field(default_factory=StaffClassifierConfig)
    queue: QueueConfig = Field(default_factory=QueueConfig)
    video: VideoConfig = Field(default_factory=VideoConfig)

    # General
    store_id: str = Field(default="STORE001", alias="STORE_ID")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    metrics_port: int = Field(default=8001, description="Prometheus metrics port")

    model_config = {"env_prefix": "", "env_nested_delimiter": "__"}
