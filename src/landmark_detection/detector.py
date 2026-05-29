"""
Facial landmark detector for NoseCheck.

Uses MediaPipe Face Landmarker (Tasks API). Model is downloaded during build.
"""

import sys
from pathlib import Path

import cv2
import numpy as np

# Add project root for config import
_project_root = Path(__file__).resolve().parent.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

try:
    import config
    LANDMARK_CONFIG = config.LANDMARK_DETECTION
    NASAL_LANDMARKS = config.NASAL_LANDMARKS
except ImportError:
    LANDMARK_CONFIG = {
        "min_detection_confidence": 0.5,
        "min_tracking_confidence": 0.5,
        "static_image_mode": True,
    }
    NASAL_LANDMARKS = {
        "nose_tip": 1,
        "nose_bridge": 168,
        "left_nostril_outer": 129,
        "left_nostril_inner": 203,
        "right_nostril_outer": 358,
        "right_nostril_inner": 423,
        "left_face_edge": 234,
        "right_face_edge": 454,
    }

_MODEL_PATH = _project_root / "models" / "face_landmarker.task"
_FACE_LANDMARKER = None


def _download_model_if_needed():
    """Download Face Landmarker model if not present."""
    if _MODEL_PATH.exists():
        return
    _MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    try:
        import urllib.request
        url = "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task"
        urllib.request.urlretrieve(url, str(_MODEL_PATH))
    except Exception as e:
        raise FileNotFoundError(
            f"Could not download model. Please download manually from "
            f"https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task "
            f"and place at {_MODEL_PATH}. Error: {e}"
        )


def _get_face_landmarker():
    """Get or create the Face Landmarker instance (cached)."""
    global _FACE_LANDMARKER
    if _FACE_LANDMARKER is None:
        import mediapipe as mp
        _download_model_if_needed()
        BaseOptions = mp.tasks.BaseOptions
        FaceLandmarker = mp.tasks.vision.FaceLandmarker
        FaceLandmarkerOptions = mp.tasks.vision.FaceLandmarkerOptions
        VisionRunningMode = mp.tasks.vision.RunningMode

        base_options = BaseOptions(
            model_asset_path=str(_MODEL_PATH),
            delegate=BaseOptions.Delegate.CPU,
        )
        options = FaceLandmarkerOptions(
            base_options=base_options,
            running_mode=VisionRunningMode.IMAGE,
            num_faces=1,
            min_face_detection_confidence=LANDMARK_CONFIG.get(
                "min_detection_confidence", 0.5
            ),
            min_face_presence_confidence=LANDMARK_CONFIG.get(
                "min_tracking_confidence", 0.5
            ),
        )
        _FACE_LANDMARKER = FaceLandmarker.create_from_options(options)
    return _FACE_LANDMARKER


def detect_landmarks(image: np.ndarray):
    """
    Detect nasal landmarks using MediaPipe Face Landmarker.

    Args:
        image: Input image as NumPy array (BGR or RGB).

    Returns:
        Dict mapping landmark names to (x, y) pixel coordinates,
        or None if no face detected.
    """
    if len(image.shape) == 2:
        image_rgb = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
    else:
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    import mediapipe as mp
    landmarker = _get_face_landmarker()
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image_rgb)
    results = landmarker.detect(mp_image)

    if not results.face_landmarks:
        return None

    face_landmarks = results.face_landmarks[0]
    h, w = image.shape[:2]
    landmarks = {}

    for name, idx in NASAL_LANDMARKS.items():
        lm = face_landmarks[idx]
        x = lm.x * w
        y = lm.y * h
        landmarks[name] = (x, y)

    return landmarks


def detect_landmarks_normalized(image: np.ndarray):
    """Detect landmarks and return normalized coordinates (0-1)."""
    if len(image.shape) == 2:
        image_rgb = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
    else:
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    import mediapipe as mp
    landmarker = _get_face_landmarker()
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image_rgb)
    results = landmarker.detect(mp_image)

    if not results.face_landmarks:
        return None

    face_landmarks = results.face_landmarks[0]
    landmarks = {}
    for name, idx in NASAL_LANDMARKS.items():
        lm = face_landmarks[idx]
        landmarks[name] = (lm.x, lm.y)
    return landmarks
