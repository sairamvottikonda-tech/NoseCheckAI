"""
Deviation score calculator for NoseCheck.

Combines asymmetry metrics into a normalized 0-100 deviation score
and classifies severity (normal, mild, moderate, severe).
"""

import sys
from pathlib import Path

_project_root = Path(__file__).resolve().parent.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

try:
    import config
    SCORING_CONFIG = config.SCORING
except ImportError:
    SCORING_CONFIG = {
        "weights": {
            "lateral_deviation": 0.4,
            "septal_angle": 0.3,
            "nostril_asymmetry": 0.2,
            "bridge_straightness": 0.1,
        },
        "classification_thresholds": {
            "normal": (0, 25),
            "mild": (25, 50),
            "moderate": (50, 75),
            "severe": (75, 100),
        },
    }


def calculate_score(measurements: dict) -> dict:
    """
    Calculate deviation score and classification from asymmetry measurements.

    Args:
        measurements: Dict from asymmetry_calculator.calculate() with keys
                      lateral_deviation, septal_angle, nostril_asymmetry,
                      bridge_straightness.

    Returns:
        Dict with keys: deviation_score (0-100), classification (str),
        raw_metrics (dict).
    """
    from src.measurement.asymmetry_calculator import normalize_for_score

    weights = SCORING_CONFIG["weights"]
    normalized = normalize_for_score(measurements)

    # Weighted sum (each metric already 0-100)
    deviation_score = (
        weights["lateral_deviation"] * normalized["lateral_deviation"]
        + weights["septal_angle"] * normalized["septal_angle"]
        + weights["nostril_asymmetry"] * normalized["nostril_asymmetry"]
        + weights["bridge_straightness"] * normalized["bridge_straightness"]
    )
    deviation_score = min(100, max(0, round(deviation_score, 1)))

    classification = _classify(deviation_score)

    return {
        "deviation_score": deviation_score,
        "classification": classification,
        "raw_metrics": measurements,
        "normalized_metrics": normalized,
    }


def _classify(score: float) -> str:
    """
    Classify severity based on deviation score.

    Args:
        score: Deviation score 0-100.

    Returns:
        One of: normal, mild, moderate, severe.
    """
    thresholds = SCORING_CONFIG["classification_thresholds"]
    for label, (low, high) in thresholds.items():
        if low <= score < high:
            return label
    return "severe"  # score >= 75


def calculate_score_from_landmarks(landmarks: dict) -> dict:
    """
    Convenience: compute measurements and score from landmarks in one call.

    Args:
        landmarks: Dict from landmark_detection.detector.detect_landmarks().

    Returns:
        Same as calculate_score().
    """
    from src.measurement.asymmetry_calculator import calculate

    measurements = calculate(landmarks)
    return calculate_score(measurements)
