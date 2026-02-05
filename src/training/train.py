"""
YOLO model training module for product recognition.
Uses Ultralytics YOLO for training on custom product dataset.
"""

from pathlib import Path
from ultralytics import YOLO


def train_model(
    data_yaml: str = "models/configs/dataset.yaml",
    model_name: str = "yolov8n.pt",
    epochs: int = 100,
    imgsz: int = 640,
    batch: int = 16,
    project: str = "models/weights",
    name: str = "product_detector",
    device: str = "auto",
    patience: int = 20,
    save_period: int = 10,
    resume: bool = False
) -> str:
    """
    Train YOLO model on product dataset.
    
    Args:
        data_yaml: Path to dataset YAML config
        model_name: Base model to use (yolov8n/s/m/l/x.pt)
        epochs: Number of training epochs
        imgsz: Input image size
        batch: Batch size
        project: Directory to save results
        name: Experiment name
        device: Device to train on ('auto', 'cpu', '0', '0,1')
        patience: Early stopping patience
        save_period: Save checkpoint every N epochs
        resume: Resume training from last checkpoint
    
    Returns:
        Path to best model weights
    """
    # Load model
    if resume:
        model = YOLO(f"{project}/{name}/weights/last.pt")
    else:
        model = YOLO(model_name)

    # Train
    results = model.train(
        data=data_yaml,
        epochs=epochs,
        imgsz=imgsz,
        batch=batch,
        project=project,
        name=name,
        device=device,
        patience=patience,
        save_period=save_period,
        # Augmentation settings
        hsv_h=0.015,       # Hue augmentation
        hsv_s=0.7,         # Saturation augmentation
        hsv_v=0.4,         # Value augmentation
        degrees=10.0,      # Rotation augmentation
        translate=0.1,     # Translation augmentation
        scale=0.5,         # Scale augmentation
        fliplr=0.5,        # Horizontal flip probability
        flipud=0.0,        # Vertical flip probability
        mosaic=1.0,        # Mosaic augmentation
        mixup=0.1,         # Mixup augmentation
    )

    best_model_path = f"{project}/{name}/weights/best.pt"
    print(f"\nTraining complete! Best model saved at: {best_model_path}")
    return best_model_path


def validate_model(
    model_path: str,
    data_yaml: str = "models/configs/dataset.yaml",
    imgsz: int = 640,
    batch: int = 16
) -> dict:
    """Validate trained model on validation set."""
    model = YOLO(model_path)
    results = model.val(data=data_yaml, imgsz=imgsz, batch=batch)

    metrics = {
        "mAP50": results.box.map50,
        "mAP50-95": results.box.map,
        "precision": results.box.mp,
        "recall": results.box.mr,
    }

    print(f"\nValidation Results:")
    for metric, value in metrics.items():
        print(f"  {metric}: {value:.4f}")

    return metrics


if __name__ == "__main__":
    # Train model
    best_path = train_model(
        data_yaml="models/configs/dataset.yaml",
        model_name="yolov8n.pt",
        epochs=100,
        batch=16
    )

    # Validate
    validate_model(best_path)
