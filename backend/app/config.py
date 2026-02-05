"""
Application configuration.
Loads settings from environment variables.
"""

import os
from pathlib import Path
from dataclasses import dataclass


@dataclass
class Settings:
    """Application settings."""

    # MongoDB
    MONGODB_URI: str = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    MONGODB_DB_NAME: str = os.getenv("MONGODB_DB_NAME", "inventory_audit")

    # API
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    API_DEBUG: bool = os.getenv("API_DEBUG", "true").lower() == "true"

    # CORS
    CORS_ORIGINS: list = None

    # ML Model
    MODEL_PATH: str = os.getenv(
        "MODEL_PATH", "models/weights/product_detector/weights/best.pt"
    )
    CONFIDENCE_THRESHOLD: float = float(os.getenv("CONFIDENCE_THRESHOLD", "0.25"))
    IOU_THRESHOLD: float = float(os.getenv("IOU_THRESHOLD", "0.45"))

    # Audit
    AUDIT_TOLERANCE: float = float(os.getenv("AUDIT_TOLERANCE", "0.1"))
    AUDIT_CRITICAL_THRESHOLD: float = float(
        os.getenv("AUDIT_CRITICAL_THRESHOLD", "0.3")
    )

    # File Upload
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "data/uploads")
    MAX_UPLOAD_SIZE: int = int(os.getenv("MAX_UPLOAD_SIZE", str(10 * 1024 * 1024)))  # 10MB

    # Project paths
    PROJECT_ROOT: str = str(Path(__file__).parent.parent.parent)

    def __post_init__(self):
        if self.CORS_ORIGINS is None:
            self.CORS_ORIGINS = [
                "http://localhost:3000",
                "http://localhost:5173",
            ]
        # Ensure upload directory exists
        Path(self.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)


settings = Settings()
