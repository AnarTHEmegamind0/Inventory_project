"""Tests for the Product Detector."""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np


def test_preprocess_resize():
    """Test image resize function."""
    from src.data.preprocess import resize_image

    # Create a dummy image (100x200)
    image = np.zeros((100, 200, 3), dtype=np.uint8)
    resized = resize_image(image, target_size=(640, 640))

    assert resized.shape == (640, 640, 3)


def test_preprocess_normalize():
    """Test image normalization."""
    from src.data.preprocess import normalize_image

    image = np.full((100, 100, 3), 255, dtype=np.uint8)
    normalized = normalize_image(image)

    assert normalized.max() <= 1.0
    assert normalized.min() >= 0.0
    assert normalized.dtype == np.float32


def test_detection_result_to_dict():
    """Test DetectionResult serialization."""
    from src.inference.detector import Detection, DetectionResult

    det = Detection(
        class_id=0,
        class_name="cola",
        confidence=0.95,
        bbox=[100.0, 200.0, 300.0, 400.0],
        bbox_center=[200.0, 300.0],
    )

    result = DetectionResult(
        image_path="test.jpg",
        timestamp="2024-01-01T00:00:00",
        detections=[det],
        total_products=1,
        processing_time_ms=50.0,
    )

    d = result.to_dict()
    assert d["total_products"] == 1
    assert len(d["detections"]) == 1
    assert d["detections"][0]["class_name"] == "cola"


if __name__ == "__main__":
    test_preprocess_resize()
    test_preprocess_normalize()
    test_detection_result_to_dict()
    print("All detector tests passed!")
