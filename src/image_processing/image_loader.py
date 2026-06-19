"""
Image loader for NoseCheck.

Loads images from file paths and returns them as NumPy arrays suitable
for OpenCV and MediaPipe processing.
"""

from pathlib import Path
from typing import List, Optional, Tuple, Union

import cv2
import numpy as np


def _load_with_exif_correction(path: Union[str, Path]) -> Optional[np.ndarray]:
    """
    Load an image and guarantee EXIF orientation is applied, returning BGR.

    Phone cameras (especially iPhones) commonly save photos with the raw
    sensor data in one orientation plus an EXIF "Orientation" tag saying
    how to rotate it for display. Whether cv2.imread() honors this tag is
    version- and build-dependent (older/some OpenCV builds ignore it
    entirely), which would silently feed a sideways or upside-down face
    into landmark detection. Pillow's EXIF handling is well established and
    library-version independent, so we use it explicitly here rather than
    trusting OpenCV's internal behavior.
    """
    try:
        from PIL import Image, ImageOps
        with Image.open(str(path)) as pil_img:
            pil_img = ImageOps.exif_transpose(pil_img)  # applies/clears EXIF rotation
            pil_img = pil_img.convert("RGB")
            rgb = np.array(pil_img)
            return cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
    except Exception:
        # Fall back to direct OpenCV read if Pillow can't open it for any reason
        image = cv2.imread(str(path))
        return image


def load_image(path: Union[str, Path]) -> Optional[np.ndarray]:
    """
    Load an image from a file path and return as NumPy array (BGR format for OpenCV).

    EXIF orientation is always corrected, so the returned array is "upright"
    regardless of how the originating camera stored the raw pixel data.

    Args:
        path: Path to the image file (supports jpg, jpeg, png).

    Returns:
        Image as NumPy array in BGR format, or None if loading fails.
    """
    path = Path(path)
    if not path.exists():
        return None

    image = _load_with_exif_correction(path)
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
