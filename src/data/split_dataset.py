"""
Dataset splitting module.
Splits labeled data into train/val/test sets for YOLO training.
"""

import shutil
import random
from pathlib import Path
from typing import Tuple


def split_dataset(
    images_dir: str,
    labels_dir: str,
    output_dir: str,
    train_ratio: float = 0.7,
    val_ratio: float = 0.2,
    test_ratio: float = 0.1,
    seed: int = 42
) -> Tuple[int, int, int]:
    """
    Split dataset into train/val/test sets.
    
    Args:
        images_dir: Path to directory containing images
        labels_dir: Path to directory containing YOLO format labels
        output_dir: Path to output directory (will create train/val/test subdirs)
        train_ratio: Proportion of data for training
        val_ratio: Proportion of data for validation
        test_ratio: Proportion of data for testing
        seed: Random seed for reproducibility
    
    Returns:
        Tuple of (train_count, val_count, test_count)
    """
    assert abs(train_ratio + val_ratio + test_ratio - 1.0) < 1e-6, \
        "Ratios must sum to 1.0"

    random.seed(seed)

    images_path = Path(images_dir)
    labels_path = Path(labels_dir)
    output_path = Path(output_dir)

    # Collect all image files that have corresponding labels
    image_extensions = {".jpg", ".jpeg", ".png", ".bmp"}
    image_files = [
        f for f in images_path.iterdir()
        if f.suffix.lower() in image_extensions
        and (labels_path / f"{f.stem}.txt").exists()
    ]

    if not image_files:
        print("No images with labels found!")
        return 0, 0, 0

    # Shuffle
    random.shuffle(image_files)

    # Calculate split indices
    total = len(image_files)
    train_end = int(total * train_ratio)
    val_end = train_end + int(total * val_ratio)

    splits = {
        "train": image_files[:train_end],
        "val": image_files[train_end:val_end],
        "test": image_files[val_end:]
    }

    # Create directories and copy files
    for split_name, files in splits.items():
        split_images_dir = output_path / split_name / "images"
        split_labels_dir = output_path / split_name / "labels"
        split_images_dir.mkdir(parents=True, exist_ok=True)
        split_labels_dir.mkdir(parents=True, exist_ok=True)

        for img_file in files:
            # Copy image
            shutil.copy2(str(img_file), str(split_images_dir / img_file.name))

            # Copy label
            label_file = labels_path / f"{img_file.stem}.txt"
            shutil.copy2(str(label_file), str(split_labels_dir / label_file.name))

    train_count = len(splits["train"])
    val_count = len(splits["val"])
    test_count = len(splits["test"])

    print(f"Dataset split complete:")
    print(f"  Train: {train_count} images ({train_count/total*100:.1f}%)")
    print(f"  Val:   {val_count} images ({val_count/total*100:.1f}%)")
    print(f"  Test:  {test_count} images ({test_count/total*100:.1f}%)")

    return train_count, val_count, test_count


if __name__ == "__main__":
    split_dataset(
        images_dir="data/labeled/images",
        labels_dir="data/labeled/labels",
        output_dir="data/splits",
        train_ratio=0.7,
        val_ratio=0.2,
        test_ratio=0.1
    )
