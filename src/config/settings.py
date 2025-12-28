from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import Optional

class Settings(BaseSettings):
    """Configuration settings loaded from environment variables."""
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8", 
        extra="ignore"
    )

    # Core Settings
    SERVICE_NAME: str = "WarehouseRatMonitor"
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"

    # Infrastructure Settings (Redis)
    REDIS_HOST: str = Field(default="localhost")
    REDIS_PORT: int = Field(default=6379)
    REDIS_CHANNEL: str = "rat_detections"

    # Database Settings (PostgreSQL/SQLite)
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str
    # Example: Use Pydantic property for SQLAlchemy connection string
    @property
    def DATABASE_URL(self) -> str:
        # Note: You might need to adjust the driver based on your choice (e.g., psycopg2)
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


    # AI/Twilio Settings
    ROBOFLOW_API_KEY: str
    ROBOFLOW_MODEL_ID: str

    TWILIO_ACCOUNT_SID: str
    TWILIO_AUTH_TOKEN: str
    TWILIO_FROM_NUMBER: str
    TWILIO_TO_NUMBER: str

    OPENAI_API_KEY: Optional[str] = None # Optional for local testing

# Global settings instance
settings = Settings()
