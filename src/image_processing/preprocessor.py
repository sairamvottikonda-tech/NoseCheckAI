"""
Image preprocessor for NoseCheck.

Resizes and normalizes images for consistent analysis pipeline.
"""

import cv2
import numpy as np

# Import config when available; use defaults if not
try:
    import config
    TARGET_WIDTH = config.IMAGE_PROCESSING.get("target_width", 640)
    TARGET_HEIGHT = config.IMAGE_PROCESSING.get("target_height", 480)
    NORMALIZE_LIGHTING = config.IMAGE_PROCESSING.get("normalize_lighting", True)
except ImportError:
    TARGET_WIDTH = 640
    TARGET_HEIGHT = 480
    NORMALIZE_LIGHTING = True


def preprocess(image: np.ndarray) -> np.ndarray:
    """
    Preprocess an image for landmark detection.

    - Resizes to target dimensions (640x480 by default)
    - Optionally normalizes lighting using CLAHE

    Args:
        image: Input image as NumPy array (BGR).

    Returns:
        Preprocessed image.
    """
    processed = image.copy()

    # Resize to target dimensions
    h, w = processed.shape[:2]
    if (w, h) != (TARGET_WIDTH, TARGET_HEIGHT):
        processed = cv2.resize(processed, (TARGET_WIDTH, TARGET_HEIGHT))

    # Optional lighting normalization
    if NORMALIZE_LIGHTING:
        processed = _normalize_lighting(processed)

    return processed


def _normalize_lighting(image: np.ndarray) -> np.ndarray:
    """
    Apply CLAHE (Contrast Limited Adaptive Histogram Equalization) for lighting normalization.

    Args:
        image: BGR image.

    Returns:
        Image with normalized lighting.
    """
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    l_channel, a_channel, b_channel = cv2.split(lab)

    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    l_channel = clahe.apply(l_channel)

    lab = cv2.merge([l_channel, a_channel, b_channel])
    return cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)


def resize_to_target(image: np.ndarray, target_width: int = None, target_height: int = None) -> np.ndarray:
    """
    Resize image to target dimensions.

    Args:
        image: Input image.
        target_width: Target width (default from config).
        target_height: Target height (default from config).

    Returns:
        Resized image.
    """
    target_width = target_width or TARGET_WIDTH
    target_height = target_height or TARGET_HEIGHT
    return cv2.resize(image, (target_width, target_height))
