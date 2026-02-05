"""
Model evaluation module.
Evaluates trained model performance and generates reports.
"""

import json
from pathlib import Path
from datetime import datetime

import cv2
import numpy as np
from ultralytics import YOLO


def evaluate_on_test_set(
    model_path: str,
    test_images_dir: str = "data/splits/test/images",
    test_labels_dir: str = "data/splits/test/labels",
    conf_threshold: float = 0.5,
    iou_threshold: float = 0.5
) -> dict:
    """
    Evaluate model on test set and generate detailed metrics.
    
    Returns:
        Dictionary containing evaluation metrics
    """
    model = YOLO(model_path)
    test_images = Path(test_images_dir)

    results = model.predict(
        source=str(test_images),
        conf=conf_threshold,
        iou=iou_threshold,
        save=False,
        verbose=False
    )

    # Collect metrics
    total_images = len(results)
    total_detections = sum(len(r.boxes) for r in results)
    avg_confidence = 0.0

    if total_detections > 0:
        all_confs = []
        for r in results:
            all_confs.extend(r.boxes.conf.cpu().numpy().tolist())
        avg_confidence = np.mean(all_confs)

    evaluation = {
        "model_path": model_path,
        "timestamp": datetime.now().isoformat(),
        "test_images": total_images,
        "total_detections": total_detections,
        "avg_detections_per_image": total_detections / max(total_images, 1),
        "avg_confidence": float(avg_confidence),
        "conf_threshold": conf_threshold,
        "iou_threshold": iou_threshold,
    }

    return evaluation


def save_evaluation_report(
    evaluation: dict,
    output_path: str = "models/evaluation_report.json"
) -> None:
    """Save evaluation results to JSON file."""
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    with open(output, "w") as f:
        json.dump(evaluation, f, indent=2)

    print(f"Evaluation report saved to: {output_path}")


def compare_models(
    model_paths: list,
    test_images_dir: str = "data/splits/test/images"
) -> list:
    """Compare multiple models on the same test set."""
    results = []

    for model_path in model_paths:
        print(f"\nEvaluating: {model_path}")
        evaluation = evaluate_on_test_set(model_path, test_images_dir)
        results.append(evaluation)

    # Print comparison
    print("\n" + "=" * 60)
    print("Model Comparison:")
    print("=" * 60)
    for r in results:
        print(f"  {Path(r['model_path']).name}:")
        print(f"    Detections: {r['total_detections']}")
        print(f"    Avg Confidence: {r['avg_confidence']:.4f}")
    print("=" * 60)

    return results


if __name__ == "__main__":
    evaluation = evaluate_on_test_set(
        model_path="models/weights/product_detector/weights/best.pt"
    )
    save_evaluation_report(evaluation)
    print(json.dumps(evaluation, indent=2))
