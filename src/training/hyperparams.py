"""
Hyperparameter configuration for model training.
Centralized config to make experiments reproducible.
"""

# Default training hyperparameters
TRAINING_CONFIG = {
    # Model
    "model_name": "yolov8n.pt",      # Options: yolov8n/s/m/l/x.pt
    "imgsz": 640,                      # Input image size

    # Training
    "epochs": 100,
    "batch": 16,
    "patience": 20,                    # Early stopping patience
    "save_period": 10,                 # Save checkpoint every N epochs

    # Optimizer
    "optimizer": "auto",               # Options: SGD, Adam, AdamW, auto
    "lr0": 0.01,                       # Initial learning rate
    "lrf": 0.01,                       # Final learning rate factor
    "momentum": 0.937,
    "weight_decay": 0.0005,
    "warmup_epochs": 3.0,
    "warmup_momentum": 0.8,

    # Augmentation
    "hsv_h": 0.015,
    "hsv_s": 0.7,
    "hsv_v": 0.4,
    "degrees": 10.0,
    "translate": 0.1,
    "scale": 0.5,
    "fliplr": 0.5,
    "flipud": 0.0,
    "mosaic": 1.0,
    "mixup": 0.1,

    # Detection
    "conf_threshold": 0.25,
    "iou_threshold": 0.45,
}


# Product classes - customize based on your inventory
PRODUCT_CLASSES = [
    "product_a",
    "product_b",
    "product_c",
    # Add your product classes here
]


# Experiment presets
PRESETS = {
    "quick_test": {
        "model_name": "yolov8n.pt",
        "epochs": 10,
        "batch": 8,
        "imgsz": 320,
    },
    "standard": {
        "model_name": "yolov8s.pt",
        "epochs": 100,
        "batch": 16,
        "imgsz": 640,
    },
    "high_accuracy": {
        "model_name": "yolov8m.pt",
        "epochs": 200,
        "batch": 8,
        "imgsz": 640,
        "patience": 30,
    },
}


def get_config(preset: str = None) -> dict:
    """Get training configuration, optionally based on a preset."""
    config = TRAINING_CONFIG.copy()

    if preset and preset in PRESETS:
        config.update(PRESETS[preset])

    return config
