"""
Detection result document model for MongoDB.
"""

from pydantic import BaseModel
from typing import List


class BoundingBox(BaseModel):
    """Single detection bounding box."""
    class_id: int
    class_name: str
    confidence: float
    bbox: List[float]  # [x1, y1, x2, y2]


class DetectionDocument(BaseModel):
    """Detection result document schema."""
    image_path: str
    timestamp: str
    detections: List[BoundingBox] = []
    total_products: int = 0
    processing_time_ms: float = 0.0
