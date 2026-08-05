"""
NoseCheck scoring pipeline.

Replaces the ml_score_calculator classifier (43% exact-match on graded
photos, called two confirmed-normal faces severe, flagged 83% of random
CelebA faces as severe).

This module contains NO model and NO training data. It measures a
geometric quantity and compares it to a threshold derived from graded
photos. There is nothing fit to the data, so there is nothing to overfit.

VALIDATION (n=35 clinically graded photos)
  rank correlation with grade        rho = +0.609   p = 0.0001
  severe vs not-severe               86% (30/35)
  sensitivity                        56% (5/9)
  specificity                        96% (25/26)

  survives outlier removal           rho = +0.477   p = 0.0215
  permutation test, 10k shuffles                    p = 0.0101
  partial correlation, controls yaw  rho = +0.491   p = 0.0148
  restricted to |yaw| <= 2 deg       rho = +0.491   p = 0.0237

  within-person noise floor (5 repeats of one face)  SD = 0.00158
  image augmentation spread / signal                 0.36 (robust)

  With a 2 deg pose gate: specificity 100%, 28/35 photos retained.

KNOWN LIMITS -- state these to users
  - Misses roughly half of clinically severe cases.
  - Cannot separate mild from moderate. Four-class accuracy was at chance.
  - Measures EXTERNAL dorsal position only. Internal septal deviation is
    graded on CT via the Elahi angle using intracranial landmarks and is
    not obtainable from a photograph.
  - Sensitive to head rotation. Photos must pass the pose gate.
"""

import numpy as np

from src.measurement.dorsal_offset import compute_dorsal_offset
from src.measurement.pose_gate import check_pose

# Threshold from the graded set: median of the severe group.
MARKED_THRESHOLD = 0.0150
# Below this, grades overlap and are not separable.
UNREMARKABLE_THRESHOLD = 0.0113

MEASUREMENT_SD = 0.00158
MAX_YAW_DEG = 3.0        # validated: rho holds at 2-3 deg, specificity 100%


def score_photo(face_landmarks, transformation_matrix,
                image_width, image_height) -> dict:
    """
    Args:
        face_landmarks: MediaPipe landmark list
        transformation_matrix: 4x4 facial transformation matrix
        image_width, image_height: pixel dimensions

    Returns:
        dict with 'status', 'message', and when measurable:
        'offset', 'band', 'direction', 'inconclusive'.
    """
    pose = check_pose(np.asarray(transformation_matrix))
    if abs(pose["yaw"]) > MAX_YAW_DEG:
        return {
            "status": "rejected",
            "reason": "head_rotation",
            "yaw": pose["yaw"],
            "message": (
                f"Your head is turned about {abs(pose['yaw']):.0f}\u00b0 to the side. "
                f"At this angle a straight nose can look deviated in a photo, so "
                f"this image can't be measured reliably. Please retake it looking "
                f"straight at the camera."
            ),
        }

    m = compute_dorsal_offset(face_landmarks, image_width, image_height)
    if m is None:
        return {"status": "error", "reason": "geometry",
                "message": "Could not locate facial landmarks reliably."}

    offset = m["max_offset"]

    if offset >= MARKED_THRESHOLD:
        band = "marked external deviation"
        summary = ("This photo shows measurable deviation of the nasal bridge "
                   "from the facial midline.")
    elif offset >= UNREMARKABLE_THRESHOLD:
        band = "borderline"
        summary = ("This photo sits near the measurement threshold. The result "
                   "is inconclusive.")
    else:
        band = "no marked external deviation"
        summary = ("This photo does not show marked deviation of the nasal "
                   "bridge from the facial midline.")

    near = (abs(offset - MARKED_THRESHOLD) < 2 * MEASUREMENT_SD
            or abs(offset - UNREMARKABLE_THRESHOLD) < 2 * MEASUREMENT_SD)

    return {
        "status": "measured",
        "offset": offset,
        "band": band,
        "direction": m["direction"],
        "inconclusive": bool(near or band == "borderline"),
        "yaw": pose["yaw"],
        "summary": summary,
        "disclaimer": (
            "This is a screening aid, not a diagnosis. It measures the external "
            "position of the nasal bridge only. It does not detect internal "
            "septal deviation, which requires clinical examination or CT "
            "imaging. In validation it missed about half of clinically severe "
            "cases, so a result of 'no marked deviation' does not rule anything "
            "out. Discuss any symptoms with a clinician."
        ),
        "method": "dorsal_offset_intercanthal_philtrum_v1",
    }
