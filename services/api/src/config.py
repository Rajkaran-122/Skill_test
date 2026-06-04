"""API Configuration."""

from pydantic_settings import BaseSettings
from pydantic import Field


class APIConfig(BaseSettings):
    """FastAPI service configuration."""

    # Database
    database_url: str = Field(
        default="sqlite+aiosqlite:///./local_mock.db",
        alias="DATABASE_URL",
    )

    # Redis
    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")

    # Kafka
    kafka_bootstrap_servers: str = Field(default="localhost:9092", alias="KAFKA_BOOTSTRAP_SERVERS")

    # JWT
    jwt_secret_key: str = Field(default="change_this_to_a_secure_random_string", alias="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    jwt_access_token_expire_minutes: int = Field(default=30)

    # CORS
    cors_origins: str = Field(
        default="http://localhost:3000,http://localhost:5173",
        alias="API_CORS_ORIGINS",
    )

    # General
    environment: str = Field(default="development", alias="ENVIRONMENT")
    debug: bool = Field(default=True, alias="DEBUG")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    model_config = {"env_prefix": ""}
