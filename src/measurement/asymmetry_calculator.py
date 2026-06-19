"""
Asymmetry calculator for NoseCheck.

Computes lateral deviation, septal angle, nostril asymmetry, and bridge straightness
from nasal landmarks.
"""

import sys
from pathlib import Path

_project_root = Path(__file__).resolve().parent.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

try:
    import config
    MEASUREMENT_CONFIG = config.MEASUREMENT
    SCORING_CONFIG = getattr(config, "SCORING", {})
except ImportError:
    MEASUREMENT_CONFIG = {"normalize_by_face_width": True, "face_width_landmarks": (234, 454)}
    SCORING_CONFIG = {}

from src.measurement.geometry_utils import (
    angle_from_vertical,
    distance,
    distance_to_midline,
    facial_midline,
    robust_facial_midline,
    nostril_width,
)


def calculate(landmarks: dict) -> dict:
    """
    Calculate all asymmetry metrics from nasal landmarks.

    Args:
        landmarks: Dict mapping landmark names to (x, y) coordinates.
                   Required keys: nose_tip, nose_bridge, left_nostril_outer,
                   left_nostril_inner, right_nostril_outer, right_nostril_inner,
                   left_face_edge, right_face_edge.

    Returns:
        Dict with keys: lateral_deviation, septal_angle, nostril_asymmetry,
        bridge_straightness, face_width. All metrics normalized where applicable.
    """
    # Get face width for normalization
    left_face = landmarks["left_face_edge"]
    right_face = landmarks["right_face_edge"]
    face_width = distance(left_face, right_face)
    if face_width < 1e-6:
        face_width = 1.0  # Avoid division by zero

    # Lateral deviation: distance from nose tip to midline (normalized by face width)
    # Uses eye-corner + face-edge averaged midline when eye landmarks are present,
    # which is much less sensitive to small head tilts than face-edges alone.
    midline_x = robust_facial_midline(
        left_face, right_face,
        landmarks.get("left_eye_outer"), landmarks.get("right_eye_outer"),
        landmarks.get("left_eye_inner"), landmarks.get("right_eye_inner"),
    )
    tip = landmarks["nose_tip"]
    lateral_px = abs(distance_to_midline(tip, midline_x))
    lateral_deviation = lateral_px / face_width if MEASUREMENT_CONFIG.get("normalize_by_face_width", True) else lateral_px

    # Septal angle: angle of bridge-to-tip line from vertical
    bridge = landmarks["nose_bridge"]
    septal_angle = abs(angle_from_vertical(bridge, tip))

    # Nostril asymmetry: difference in nostril widths
    left_width = nostril_width(landmarks["left_nostril_outer"], landmarks["left_nostril_inner"])
    right_width = nostril_width(landmarks["right_nostril_outer"], landmarks["right_nostril_inner"])
    nostril_diff = abs(left_width - right_width)
    nostril_sum = left_width + right_width
    nostril_asymmetry = nostril_diff / nostril_sum if nostril_sum > 1e-6 else 0.0

    # Bridge straightness: deviation of bridge from midline
    bridge_midline_dist = abs(distance_to_midline(bridge, midline_x))
    bridge_straightness = bridge_midline_dist / face_width if MEASUREMENT_CONFIG.get("normalize_by_face_width", True) else bridge_midline_dist

    return {
        "lateral_deviation": lateral_deviation,
        "septal_angle": septal_angle,
        "nostril_asymmetry": nostril_asymmetry,
        "bridge_straightness": bridge_straightness,
        "face_width": face_width,
    }


def normalize_for_score(measurements: dict) -> dict:
    """
    Normalize raw measurements to 0-100 scale for scoring.

    Uses configurable scaling factors from config.py.
    Applies a noise floor (also from config) so that sub-pixel jitter
    and normal micro-asymmetry don't inflate the score.
    """
    factors = SCORING_CONFIG.get("scaling_factors", {})
    lateral_scale = factors.get("lateral_deviation", 1500)
    angle_scale = factors.get("septal_angle", 10)
    nostril_scale = factors.get("nostril_asymmetry", 200)
    bridge_scale = factors.get("bridge_straightness", 1500)

    # Noise floor: values below these thresholds are zeroed out
    # Prevents normal micro-asymmetry from registering as deviation
    nf = SCORING_CONFIG.get("noise_floor", {})
    NOISE_FLOOR = {
        "lateral_deviation": nf.get("lateral_deviation", 0.003),
        "septal_angle": nf.get("septal_angle", 0.5),
        "nostril_asymmetry": nf.get("nostril_asymmetry", 0.02),
        "bridge_straightness": nf.get("bridge_straightness", 0.003),
    }

    lateral = max(0, measurements["lateral_deviation"] - NOISE_FLOOR["lateral_deviation"])
    angle = max(0, measurements["septal_angle"] - NOISE_FLOOR["septal_angle"])
    nostril = max(0, measurements["nostril_asymmetry"] - NOISE_FLOOR["nostril_asymmetry"])
    bridge = max(0, measurements["bridge_straightness"] - NOISE_FLOOR["bridge_straightness"])

    lateral_norm = min(100, lateral * lateral_scale)
    angle_norm = min(100, angle * angle_scale)
    nostril_norm = min(100, nostril * nostril_scale)
    bridge_norm = min(100, bridge * bridge_scale)

    return {
        "lateral_deviation": lateral_norm,
        "septal_angle": angle_norm,
        "nostril_asymmetry": nostril_norm,
        "bridge_straightness": bridge_norm,
    }
