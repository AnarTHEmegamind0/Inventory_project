"""
Detection business logic service.
Handles model loading and detection operations.
"""

from pathlib import Path
from typing import Optional

from ..config import settings


class DetectionService:
    """Manages product detection operations."""

    _detector = None

    @classmethod
    def get_detector(cls):
        """Get or initialize the product detector (singleton)."""
        if cls._detector is None:
            model_path = Path(settings.MODEL_PATH)
            if model_path.exists():
                from src.inference.detector import ProductDetector
                cls._detector = ProductDetector(
                    model_path=str(model_path),
                    conf_threshold=settings.CONFIDENCE_THRESHOLD,
                    iou_threshold=settings.IOU_THRESHOLD,
                )
            else:
                print(f"Model not found at {model_path}. Detection disabled.")
                return None
        return cls._detector

    @classmethod
    def detect_from_file(cls, image_path: str) -> Optional[dict]:
        """Run detection on an image file."""
        detector = cls.get_detector()
        if detector is None:
            return None

        result = detector.detect(image_path)
        return result.to_dict()
