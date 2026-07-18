"""
Image loader for NoseCheck.

Loads images from file paths and returns them as NumPy arrays suitable
for OpenCV and MediaPipe processing.
"""

from pathlib import Path
from typing import Optional, Union

import cv2
import numpy as np

# Register HEIC/HEIF support if pillow-heif is installed
# This allows direct upload of iPhone photos without conversion
try:
    import pillow_heif
    pillow_heif.register_heif_opener()
except ImportError:
    pass


def _load_with_exif_correction(path: Union[str, Path]) -> Optional[np.ndarray]:
    """
    Load an image and guarantee EXIF orientation is applied, returning BGR.
    Supports JPEG, PNG, and HEIC/HEIF (if pillow-heif is installed).
    """
    try:
        from PIL import Image, ImageOps
        with Image.open(str(path)) as pil_img:
            pil_img = ImageOps.exif_transpose(pil_img)
            pil_img = pil_img.convert("RGB")
            rgb = np.array(pil_img)
            return cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
    except Exception:
        image = cv2.imread(str(path))
        return image


def load_image(path: Union[str, Path]) -> Optional[np.ndarray]:
    """
    Load an image from a file path and return as NumPy array (BGR format).

    Supports: JPEG, PNG, HEIC/HEIF (iPhone native format).
    EXIF orientation is always corrected.

    Args:
        path: Path to the image file.

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
