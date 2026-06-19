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

    - Resizes to fit within target dimensions WHILE PRESERVING ASPECT RATIO
      (letterboxed/padded, never stretched). This matters a lot in practice:
      most phone photos are portrait (e.g. 1080x1920), and naively resizing
      to a fixed 640x480 (4:3 landscape) box stretches the image horizontally
      by ~2.4x relative to vertical, which directly corrupts every
      horizontal-distance metric (lateral_deviation, nostril_asymmetry,
      bridge_straightness).
    - Optionally normalizes lighting using CLAHE

    Args:
        image: Input image as NumPy array (BGR).

    Returns:
        Preprocessed image, same aspect ratio as input, fit within
        (TARGET_WIDTH, TARGET_HEIGHT) and padded with black bars as needed.
    """
    processed = image.copy()

    # Normalize to 3-channel BGR. Some uploads (old scanned photos, certain
    # camera/export modes, or images that lost color info during compression)
    # arrive as single-channel grayscale. Every downstream step (CLAHE,
    # MediaPipe's RGB conversion, etc.) assumes 3 channels, so converting
    # here once avoids a crash later -- this previously caused an
    # unhandled cv2.error if NORMALIZE_LIGHTING was ever enabled.
    if processed.ndim == 2:
        processed = cv2.cvtColor(processed, cv2.COLOR_GRAY2BGR)
    elif processed.ndim == 3 and processed.shape[2] == 4:
        # RGBA (e.g. some PNG uploads) -> drop alpha channel
        processed = cv2.cvtColor(processed, cv2.COLOR_BGRA2BGR)

    h, w = processed.shape[:2]
    if (w, h) != (TARGET_WIDTH, TARGET_HEIGHT):
        # Scale so the image fits *within* the target box without distortion
        scale = min(TARGET_WIDTH / w, TARGET_HEIGHT / h)
        new_w = max(1, round(w * scale))
        new_h = max(1, round(h * scale))
        resized = cv2.resize(processed, (new_w, new_h), interpolation=cv2.INTER_AREA)

        # Letterbox (pad) to the exact target size, centering the image
        pad_w = TARGET_WIDTH - new_w
        pad_h = TARGET_HEIGHT - new_h
        top = pad_h // 2
        bottom = pad_h - top
        left = pad_w // 2
        right = pad_w - left
        processed = cv2.copyMakeBorder(
            resized, top, bottom, left, right,
            borderType=cv2.BORDER_CONSTANT, value=(0, 0, 0)
        )

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
