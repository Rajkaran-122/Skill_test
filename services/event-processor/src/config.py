"""
Event Processor — Configuration.
"""

from pydantic_settings import BaseSettings
from pydantic import Field


class EventProcessorConfig(BaseSettings):
    """Root configuration for the event processor."""

    # Kafka
    kafka_bootstrap_servers: str = Field(default="localhost:9092", alias="KAFKA_BOOTSTRAP_SERVERS")
    kafka_group_id: str = Field(default="sip-event-processor", alias="KAFKA_GROUP_ID")

    # Database
    database_url: str = Field(
        default="postgresql+asyncpg://sip_user:change_me_in_production@localhost:5432/sip_db",
        alias="DATABASE_URL",
    )

    # Redis
    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")

    # Anomaly Detection
    anomaly_sigma_threshold: float = Field(default=3.0, alias="ANOMALY_SIGMA_THRESHOLD")
    anomaly_dead_zone_minutes: int = Field(default=30, alias="ANOMALY_DEAD_ZONE_MINUTES")
    anomaly_camera_heartbeat_timeout: int = Field(default=60, alias="ANOMALY_CAMERA_HEARTBEAT_TIMEOUT_SECONDS")

    # Session Builder
    session_inactivity_timeout: int = Field(default=1800, description="Seconds of inactivity to close session")

    # General
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    metrics_port: int = Field(default=8002, description="Prometheus metrics port")

    model_config = {"env_prefix": ""}
