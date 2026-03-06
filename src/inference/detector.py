"""
Product detector module.
Handles product detection using trained YOLO model.
"""

import cv2
import numpy as np
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass, field
from datetime import datetime

from ultralytics import YOLO


@dataclass
class Detection:
    """Single product detection result."""
    class_id: int
    class_name: str
    confidence: float
    bbox: List[float]       # [x1, y1, x2, y2]
    bbox_center: List[float]  # [cx, cy]


@dataclass
class DetectionResult:
    """Complete detection result for one image."""
    image_path: str
    timestamp: str
    detections: List[Detection] = field(default_factory=list)
    total_products: int = 0
    processing_time_ms: float = 0.0

    def to_dict(self) -> dict:
        """Convert to dictionary for API response / MongoDB storage."""
        return {
            "image_path": self.image_path,
            "timestamp": self.timestamp,
            "total_products": self.total_products,
            "processing_time_ms": self.processing_time_ms,
            "detections": [
                {
                    "class_id": d.class_id,
                    "class_name": d.class_name,
                    "confidence": d.confidence,
                    "bbox": d.bbox,
                    "bbox_center": d.bbox_center,
                }
                for d in self.detections
            ],
        }


class ProductDetector:
    """
    Product detection engine using YOLO model.
    
    Usage:
        detector = ProductDetector("models/weights/best.pt")
        result = detector.detect("path/to/image.jpg")
        print(result.total_products)
    """

    def __init__(
        self,
        model_path: str,
        conf_threshold: float = 0.25,
        iou_threshold: float = 0.45,
        device: str = "auto"
    ):
        self.model_path = model_path
        self.conf_threshold = conf_threshold
        self.iou_threshold = iou_threshold
        self.device = device

        # Load model
        self.model = YOLO(model_path)
        self.class_names = self.model.names
        print(f"Model loaded: {model_path}")
        print(f"Classes: {self.class_names}")

    def detect(self, image_source, conf: float = None) -> DetectionResult:
        """
        Run product detection on an image.
        
        Args:
            image_source: Image file path (str) or numpy array
            conf: Override confidence threshold
            
        Returns:
            DetectionResult with all detected products
        """
        conf = conf or self.conf_threshold
        start_time = cv2.getTickCount()

        # Run inference
        results = self.model.predict(
            source=image_source,
            conf=conf,
            iou=self.iou_threshold,
            device=self.device,
            verbose=False,
        )

        # Calculate processing time
        end_time = cv2.getTickCount()
        processing_time = (end_time - start_time) / cv2.getTickFrequency() * 1000

        # Parse results
        detections = []
        if results and len(results) > 0:
            result = results[0]
            boxes = result.boxes

            for i in range(len(boxes)):
                box = boxes[i]
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().tolist()
                cls_id = int(box.cls[0].item())
                confidence = float(box.conf[0].item())

                detection = Detection(
                    class_id=cls_id,
                    class_name=self.class_names.get(cls_id, f"class_{cls_id}"),
                    confidence=confidence,
                    bbox=[x1, y1, x2, y2],
                    bbox_center=[(x1 + x2) / 2, (y1 + y2) / 2],
                )
                detections.append(detection)

        image_path = image_source if isinstance(image_source, str) else "numpy_array"

        return DetectionResult(
            image_path=image_path,
            timestamp=datetime.now().isoformat(),
            detections=detections,
            total_products=len(detections),
            processing_time_ms=round(processing_time, 2),
        )

    def detect_batch(self, image_paths: List[str]) -> List[DetectionResult]:
        """Run detection on multiple images."""
        results = []
        for path in image_paths:
            result = self.detect(path)
            results.append(result)
        return results

    def draw_detections(
        self,
        image: np.ndarray,
        result: DetectionResult,
        show_labels: bool = True,
        show_confidence: bool = True
    ) -> np.ndarray:
        """Draw detection boxes on image."""
        annotated = image.copy()

        for det in result.detections:
            x1, y1, x2, y2 = [int(c) for c in det.bbox]
            color = (0, 255, 0)

            # Draw box
            cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)

            # Draw label
            if show_labels:
                label = det.class_name
                if show_confidence:
                    label += f" {det.confidence:.2f}"

                (text_w, text_h), _ = cv2.getTextSize(
                    label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1
                )
                cv2.rectangle(
                    annotated,
                    (x1, y1 - text_h - 10),
                    (x1 + text_w, y1),
                    color,
                    -1,
                )
                cv2.putText(
                    annotated,
                    label,
                    (x1, y1 - 5),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 0, 0),
                    1,
                )

        return annotated


if __name__ == "__main__":
    # Example usage
    detector = ProductDetector("models/weights/product_detector/weights/best.pt")
    result = detector.detect("data/splits/test/images/sample.jpg")
    print(f"Detected {result.total_products} products in {result.processing_time_ms}ms")
    for det in result.detections:
        print(f"  - {det.class_name}: {det.confidence:.2f}")
