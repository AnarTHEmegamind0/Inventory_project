"""
Visualization utilities for product detection results.
"""

import cv2
import numpy as np
from pathlib import Path
from typing import List, Dict, Optional


# Color palette for different classes
COLORS = [
    (0, 255, 0),    # Green
    (255, 0, 0),    # Blue
    (0, 0, 255),    # Red
    (255, 255, 0),  # Cyan
    (0, 255, 255),  # Yellow
    (255, 0, 255),  # Magenta
    (128, 255, 0),  # Light green
    (255, 128, 0),  # Light blue
    (0, 128, 255),  # Orange
    (128, 0, 255),  # Purple
]


def get_color(class_id: int) -> tuple:
    """Get a consistent color for a class ID."""
    return COLORS[class_id % len(COLORS)]


def draw_detection_results(
    image: np.ndarray,
    detections: List[Dict],
    show_labels: bool = True,
    show_confidence: bool = True,
    line_thickness: int = 2,
    font_scale: float = 0.6,
) -> np.ndarray:
    """
    Draw detection boxes and labels on image.
    
    Args:
        image: Input image (BGR)
        detections: List of detection dicts with keys:
            class_id, class_name, confidence, bbox [x1,y1,x2,y2]
        show_labels: Whether to show class labels
        show_confidence: Whether to show confidence scores
        line_thickness: Box line thickness
        font_scale: Font size scale
    
    Returns:
        Annotated image
    """
    annotated = image.copy()

    for det in detections:
        x1, y1, x2, y2 = [int(c) for c in det["bbox"]]
        color = get_color(det["class_id"])

        # Draw bounding box
        cv2.rectangle(annotated, (x1, y1), (x2, y2), color, line_thickness)

        # Draw label background and text
        if show_labels:
            label = det["class_name"]
            if show_confidence:
                label += f" {det['confidence']:.2f}"

            (text_w, text_h), baseline = cv2.getTextSize(
                label, cv2.FONT_HERSHEY_SIMPLEX, font_scale, 1
            )

            # Label background
            cv2.rectangle(
                annotated,
                (x1, y1 - text_h - 10),
                (x1 + text_w + 5, y1),
                color,
                -1,
            )

            # Label text
            cv2.putText(
                annotated,
                label,
                (x1 + 2, y1 - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                font_scale,
                (255, 255, 255),
                1,
                cv2.LINE_AA,
            )

    return annotated


def create_summary_image(
    image: np.ndarray,
    detections: List[Dict],
    title: str = "Detection Summary"
) -> np.ndarray:
    """Create a summary image with detection stats overlay."""
    annotated = draw_detection_results(image, detections)
    h, w = annotated.shape[:2]

    # Add summary overlay
    overlay = annotated.copy()
    cv2.rectangle(overlay, (10, 10), (300, 80), (0, 0, 0), -1)
    annotated = cv2.addWeighted(overlay, 0.6, annotated, 0.4, 0)

    # Add text
    cv2.putText(
        annotated,
        title,
        (20, 35),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2,
    )
    cv2.putText(
        annotated,
        f"Products detected: {len(detections)}",
        (20, 65),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (0, 255, 0),
        1,
    )

    return annotated


def save_annotated_image(
    image: np.ndarray,
    output_path: str,
) -> None:
    """Save annotated image to file."""
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(output), image)
    print(f"Saved: {output_path}")
