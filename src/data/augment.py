"""
Data augmentation module for product recognition training.
Applies various transformations to increase training data diversity.
"""

import cv2
import numpy as np
from pathlib import Path
from typing import List, Tuple
import random


def random_brightness(image: np.ndarray, factor_range: Tuple[float, float] = (0.7, 1.3)) -> np.ndarray:
    """Randomly adjust image brightness."""
    factor = random.uniform(*factor_range)
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV).astype(np.float32)
    hsv[:, :, 2] *= factor
    hsv[:, :, 2] = np.clip(hsv[:, :, 2], 0, 255)
    return cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)


def random_flip(image: np.ndarray, labels: np.ndarray = None) -> Tuple[np.ndarray, np.ndarray]:
    """Randomly flip image horizontally."""
    if random.random() > 0.5:
        image = cv2.flip(image, 1)
        if labels is not None and len(labels) > 0:
            labels = labels.copy()
            # Flip x_center for YOLO format (class, x_center, y_center, w, h)
            labels[:, 1] = 1.0 - labels[:, 1]
    return image, labels


def random_rotation(
    image: np.ndarray,
    max_angle: float = 15.0
) -> np.ndarray:
    """Randomly rotate image within a small angle range."""
    angle = random.uniform(-max_angle, max_angle)
    h, w = image.shape[:2]
    center = (w // 2, h // 2)
    matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(image, matrix, (w, h), borderValue=(114, 114, 114))
    return rotated


def add_noise(image: np.ndarray, noise_level: float = 25.0) -> np.ndarray:
    """Add Gaussian noise to image."""
    noise = np.random.normal(0, noise_level, image.shape).astype(np.float32)
    noisy = np.clip(image.astype(np.float32) + noise, 0, 255)
    return noisy.astype(np.uint8)


def random_blur(image: np.ndarray, max_kernel: int = 5) -> np.ndarray:
    """Apply random Gaussian blur."""
    kernel_size = random.choice(range(1, max_kernel + 1, 2))
    return cv2.GaussianBlur(image, (kernel_size, kernel_size), 0)


def augment_image(
    image: np.ndarray,
    labels: np.ndarray = None,
    apply_flip: bool = True,
    apply_brightness: bool = True,
    apply_rotation: bool = True,
    apply_noise: bool = False,
    apply_blur: bool = False
) -> Tuple[np.ndarray, np.ndarray]:
    """Apply a chain of random augmentations to an image."""
    aug_image = image.copy()
    aug_labels = labels.copy() if labels is not None else None

    if apply_flip:
        aug_image, aug_labels = random_flip(aug_image, aug_labels)

    if apply_brightness:
        aug_image = random_brightness(aug_image)

    if apply_rotation:
        aug_image = random_rotation(aug_image)

    if apply_noise and random.random() > 0.5:
        aug_image = add_noise(aug_image)

    if apply_blur and random.random() > 0.5:
        aug_image = random_blur(aug_image)

    return aug_image, aug_labels


def augment_dataset(
    images_dir: str,
    labels_dir: str,
    output_images_dir: str,
    output_labels_dir: str,
    num_augmentations: int = 3
) -> int:
    """Augment entire dataset with multiple variations per image."""
    images_path = Path(images_dir)
    labels_path = Path(labels_dir)
    out_images = Path(output_images_dir)
    out_labels = Path(output_labels_dir)
    out_images.mkdir(parents=True, exist_ok=True)
    out_labels.mkdir(parents=True, exist_ok=True)

    count = 0
    for img_file in images_path.glob("*.jpg"):
        image = cv2.imread(str(img_file))
        if image is None:
            continue

        # Load corresponding label
        label_file = labels_path / f"{img_file.stem}.txt"
        labels = None
        if label_file.exists():
            labels = np.loadtxt(str(label_file)).reshape(-1, 5)

        for i in range(num_augmentations):
            aug_img, aug_labels = augment_image(image, labels)

            # Save augmented image
            aug_name = f"{img_file.stem}_aug{i}{img_file.suffix}"
            cv2.imwrite(str(out_images / aug_name), aug_img)

            # Save augmented labels
            if aug_labels is not None:
                aug_label_name = f"{img_file.stem}_aug{i}.txt"
                np.savetxt(str(out_labels / aug_label_name), aug_labels, fmt="%.6f")

            count += 1

    print(f"Generated {count} augmented images -> {output_images_dir}")
    return count


if __name__ == "__main__":
    augment_dataset(
        images_dir="data/labeled/images",
        labels_dir="data/labeled/labels",
        output_images_dir="data/augmented/images",
        output_labels_dir="data/augmented/labels",
        num_augmentations=3
    )
