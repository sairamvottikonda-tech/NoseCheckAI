"""
NoseCheck scoring pipeline.

Produces a CONTINUOUS 0-100 deviation score derived directly from the
measured geometry. Every photo gets its own number.

MEASUREMENT
  Maximum perpendicular distance of the nasal dorsum from the
  intercanthal -> philtrum midline, normalized by interocular distance.
  No model, no training data, nothing fit -- pure geometry.

SCORE MAPPING
  score = clip(offset / 0.020 * 100, 0, 100)

  0.020 is the top of the observed clinical range (95th percentile of 35
  graded photos was 0.0175). Linear, so the score is directly proportional
  to measured deviation -- doubling the offset doubles the score. Observed
  scores on the graded set spanned 8.1 to 100.

VALIDATION (n=35 clinically graded photos)
  rank correlation with clinical grade   rho = +0.609   p = 0.0001
  severe vs not-severe at score 75       86% (30/35)
  sensitivity 56%, specificity 96%
  with a 3 deg pose gate: specificity 100%

  survives outlier removal               rho = +0.477   p = 0.0215
  permutation test, 10k shuffles                        p = 0.0101
  partial correlation controlling yaw    rho = +0.491   p = 0.0148
  within-person noise floor (5 repeats)  SD = 0.00158  (~8 score points)
  image augmentation spread / signal     0.36 (robust to lighting,
                                         contrast, noise, perspective, JPEG)

  Ten other measurements tested on the same photos returned p > 0.5.

HONEST LIMITS
  - The SCORE is continuous and reflects real measured geometry.
    The four-level mild/moderate/severe LABELS are not reliable --
    four-class accuracy tested at chance. Labels below are coarse
    descriptors, not clinical grades.
  - Misses roughly half of clinically severe cases.
  - Measures EXTERNAL dorsal position only. Internal septal deviation is
    graded on CT and cannot be obtained from a photograph.
  - Repeat photos of the same face vary by about 8 score points. Differences
    smaller than that are not meaningful.
"""

import numpy as np

from src.measurement.dorsal_offset import compute_dorsal_offset
from src.measurement.pose_gate import check_pose

FULL_SCALE_OFFSET = 0.020      # offset mapping to a score of 100
MEASUREMENT_SD = 0.00158       # within-person, ~8 score points
SCORE_UNCERTAINTY = round(MEASUREMENT_SD / FULL_SCALE_OFFSET * 100, 1)
MAX_YAW_DEG = 3.0


def offset_to_score(offset: float) -> float:
    return round(float(np.clip(offset / FULL_SCALE_OFFSET * 100.0, 0.0, 100.0)), 1)


def _descriptor(score: float) -> str:
    """Coarse descriptor. NOT a clinical grade -- see module docstring."""
    if score >= 75:
        return "marked"
    if score >= 55:
        return "moderate"
    if score >= 35:
        return "slight"
    return "minimal"


def score_photo(face_landmarks, transformation_matrix,
                image_width, image_height) -> dict:
    pose = check_pose(np.asarray(transformation_matrix))
    if abs(pose["yaw"]) > MAX_YAW_DEG:
        return {
            "status": "rejected",
            "reason": "head_rotation",
            "yaw": pose["yaw"],
            "message": (
                f"Your head is turned about {abs(pose['yaw']):.0f}\u00b0 to the side. "
                f"At this angle a straight nose can look deviated, so this photo "
                f"can't be measured reliably. Please retake it looking straight "
                f"at the camera."
            ),
        }

    m = compute_dorsal_offset(face_landmarks, image_width, image_height)
    if m is None:
        return {"status": "error", "reason": "geometry",
                "message": "Could not locate facial landmarks reliably."}

    offset = m["max_offset"]
    score = offset_to_score(offset)

    return {
        "status": "measured",
        "deviation_score": score,
        "score_uncertainty": SCORE_UNCERTAINTY,
        "offset": offset,
        "descriptor": _descriptor(score),
        "direction": m["direction"],
        "yaw": pose["yaw"],
        "disclaimer": (
            "Screening aid, not a diagnosis. Measures the external position of "
            "the nasal bridge only; it does not detect internal septal "
            f"deviation. Repeat photos of the same person vary by about "
            f"{SCORE_UNCERTAINTY:.0f} points, so small differences are not "
            "meaningful. In validation it missed about half of clinically "
            "severe cases, so a low score does not rule anything out."
        ),
        "method": "dorsal_offset_intercanthal_philtrum_v2",
    }
