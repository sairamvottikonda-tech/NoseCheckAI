"""
Asymmetry calculator for NoseCheck.

Computes lateral deviation, septal angle, nostril asymmetry, and bridge straightness
from nasal landmarks.
"""

import math
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


def _bridge_curve_points(landmarks: dict) -> list:
    """
    Collect all available bridge landmarks, ordered from upper (near
    forehead) to lower (near tip), plus the tip itself as the final point.

    Falls back gracefully: if the intermediate bridge points aren't present
    in the landmarks dict (e.g. an older caller that hasn't been updated),
    this returns just [nose_bridge, nose_tip] -- the original 2-point
    behavior -- so nothing breaks for partial landmark sets.
    """
    ordered_keys = ["bridge_upper", "bridge_upper_mid", "nose_bridge", "bridge_mid", "bridge_lower_mid"]
    points = [landmarks[k] for k in ordered_keys if k in landmarks]
    if "nose_tip" in landmarks:
        points.append(landmarks["nose_tip"])
    # Need at least 2 points to measure anything
    if len(points) < 2:
        return [landmarks["nose_bridge"], landmarks["nose_tip"]]
    return points


def _max_curve_deviation_from_line(points: list) -> float:
    """
    Measure the largest perpendicular deviation of any interior point from
    the straight line connecting the first and last points in the list.

    This is what makes a C-curve or S-curve deviation detectable: the two
    endpoints (top of bridge, tip) can line up vertically while a point in
    the middle of the bridge bulges to one side -- a single straight-line
    measurement between just the endpoints would miss that entirely, but
    checking every intermediate point against that line catches it.

    Returns the max perpendicular distance in the same units as the input
    points (pixels, if pixel coordinates were passed in).
    """
    if len(points) < 3:
        # Only two points (or fewer) -- no interior point to bulge, so the
        # straight-line distance between them is the only thing we can
        # measure to begin with. distance_to_midline-style perpendicular
        # deviation doesn't apply with just 2 points.
        return 0.0

    x0, y0 = points[0]
    x1, y1 = points[-1]
    line_dx = x1 - x0
    line_dy = y1 - y0
    line_len = math.sqrt(line_dx ** 2 + line_dy ** 2)
    if line_len < 1e-6:
        return 0.0

    max_dev = 0.0
    for (px, py) in points[1:-1]:
        # Perpendicular distance from point to the line through (x0,y0)-(x1,y1)
        # via the standard 2D point-to-line distance formula.
        dev = abs((px - x0) * line_dy - (py - y0) * line_dx) / line_len
        max_dev = max(max_dev, dev)
    return max_dev


def calculate(landmarks: dict) -> dict:
    """
    Calculate all asymmetry metrics from nasal landmarks.

    Args:
        landmarks: Dict mapping landmark names to (x, y) coordinates.
                   Required keys: nose_tip, nose_bridge, left_nostril_outer,
                   left_nostril_inner, right_nostril_outer, right_nostril_inner,
                   left_face_edge, right_face_edge.
                   Optional (for curve-based bridge measurement): bridge_upper,
                   bridge_upper_mid, bridge_mid, bridge_lower_mid.

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

    # Bridge straightness: previously this only measured how far the single
    # "nose_bridge" landmark sat from the midline -- a C-curve or S-curve
    # deviation that bends partway down the bridge while the bridge-point
    # and tip happen to both sit near the midline would score as
    # essentially straight. Now we measure the largest deviation of ANY
    # point along the bridge (using all available intermediate bridge
    # landmarks) from a straight reference line drawn top-to-tip. This
    # catches a bulge/curve in the middle that the old 2-point check missed.
    curve_points = _bridge_curve_points(landmarks)
    curve_dev_px = _max_curve_deviation_from_line(curve_points)
    # Fall back to the original single-point measurement if we only have
    # 2 points (e.g. intermediate bridge landmarks weren't provided)
    if curve_dev_px == 0.0 and len(curve_points) <= 2:
        bridge_midline_dist = abs(distance_to_midline(bridge, midline_x))
    else:
        bridge_midline_dist = curve_dev_px
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
