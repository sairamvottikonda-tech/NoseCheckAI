"""
Image loader for NoseCheck.

Loads images from file paths and returns them as NumPy arrays suitable
for OpenCV and MediaPipe processing.
"""

from pathlib import Path
from typing import List, Optional, Tuple, Union

import cv2
import numpy as np


def load_image(path: Union[str, Path]) -> Optional[np.ndarray]:
    """
    Load an image from a file path and return as NumPy array (BGR format for OpenCV).

    Args:
        path: Path to the image file (supports jpg, jpeg, png).

    Returns:
        Image as NumPy array in BGR format, or None if loading fails.
    """
    path = Path(path)
    if not path.exists():
        return None

    image = cv2.imread(str(path))
    if image is None:
        return None

    return image


def load_image_rgb(path: Union[str, Path]) -> Optional[np.ndarray]:
    """
    Load an image and convert to RGB format (e.g., for display with Matplotlib).

    Args:
        path: Path to the image file.

    Returns:
        Image as NumPy array in RGB format, or None if loading fails.
    """
    image = load_image(path)
    if image is None:
        return None
    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)


def load_images_from_directory(
    directory: Union[str, Path],
    extensions: Tuple[str, ...] = (".jpg", ".jpeg", ".png"),
) -> List[Tuple[Path, np.ndarray]]:
    """
    Load all images from a directory with the given extensions.

    Args:
        directory: Path to the directory.
        extensions: File extensions to include.

    Returns:
        List of (path, image) tuples.
    """
    directory = Path(directory)
    if not directory.is_dir():
        return []

    results = []
    for path in sorted(directory.iterdir()):
        if path.suffix.lower() in extensions:
            image = load_image(path)
            if image is not None:
                results.append((path, image))

    return results
