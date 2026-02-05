"""
Image preprocessing module for product recognition.
Handles image resizing, normalization, and cleaning.
"""

import cv2
import numpy as np
from pathlib import Path
from typing import Tuple, Optional


def resize_image(
    image: np.ndarray,
    target_size: Tuple[int, int] = (640, 640)
) -> np.ndarray:
    """Resize image to target size while maintaining aspect ratio with padding."""
    h, w = image.shape[:2]
    target_w, target_h = target_size

    # Calculate scale factor
    scale = min(target_w / w, target_h / h)
    new_w = int(w * scale)
    new_h = int(h * scale)

    # Resize
    resized = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_LINEAR)

    # Create padded image (letterbox)
    padded = np.full((target_h, target_w, 3), 114, dtype=np.uint8)
    pad_x = (target_w - new_w) // 2
    pad_y = (target_h - new_h) // 2
    padded[pad_y:pad_y + new_h, pad_x:pad_x + new_w] = resized

    return padded


def normalize_image(image: np.ndarray) -> np.ndarray:
    """Normalize image pixel values to [0, 1] range."""
    return image.astype(np.float32) / 255.0


def load_image(image_path: str) -> Optional[np.ndarray]:
    """Load an image from file path."""
    path = Path(image_path)
    if not path.exists():
        print(f"Image not found: {image_path}")
        return None

    image = cv2.imread(str(path))
    if image is None:
        print(f"Failed to load image: {image_path}")
        return None

    return image


def preprocess_image(
    image_path: str,
    target_size: Tuple[int, int] = (640, 640),
    normalize: bool = False
) -> Optional[np.ndarray]:
    """Full preprocessing pipeline: load -> resize -> normalize."""
    image = load_image(image_path)
    if image is None:
        return None

    image = resize_image(image, target_size)

    if normalize:
        image = normalize_image(image)

    return image


def batch_preprocess(
    image_dir: str,
    output_dir: str,
    target_size: Tuple[int, int] = (640, 640),
    extensions: Tuple[str, ...] = (".jpg", ".jpeg", ".png", ".bmp")
) -> int:
    """Preprocess all images in a directory and save to output directory."""
    input_path = Path(image_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    count = 0
    for img_file in input_path.iterdir():
        if img_file.suffix.lower() in extensions:
            image = preprocess_image(str(img_file), target_size)
            if image is not None:
                output_file = output_path / img_file.name
                cv2.imwrite(str(output_file), image)
                count += 1

    print(f"Preprocessed {count} images -> {output_dir}")
    return count


if __name__ == "__main__":
    # Example usage
    batch_preprocess(
        image_dir="data/raw",
        output_dir="data/labeled/images",
        target_size=(640, 640)
    )
