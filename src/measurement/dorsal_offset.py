"""
Dorsal offset from the intercanthal->philtrum midline.

This is the only measurement in this project that has survived a full set
of controls. Validation on n=24 clinically graded photos:

    offset vs grade                      rho = +0.526   p = 0.0083
    with strongest outlier removed       rho = +0.477   p = 0.0215
    permutation test (10,000 shuffles)                  p = 0.0101
    partial correlation, controlling yaw rho = +0.491   p = 0.0148
    restricted to |yaw| <= 2 deg (n=21)  rho = +0.491   p = 0.0237

    within-person noise floor (5 repeat photos):  SD = 0.00158
    between-grade SD:                                  0.00651
    signal-to-noise:                                   4.13

Ten other measurements tested on the same data returned p > 0.5, including
lateral deviation from the face-edge midline, dorsal offset from
glabella-menton, tip angle, drift slope, sidewall (BTAL) symmetry, shadow
intensity asymmetry, pixel mirror difference, and HOG silhouette features.

MIDLINE:
  Point A = midpoint of the inner eye corners (landmarks 133, 362)
  Point B = philtrum midpoint (landmark 164)
Both are midline anchors independent of nasal anatomy, so a deviated nose
cannot drag the reference line toward itself.

WHAT IT MEASURES:
Maximum perpendicular distance of any dorsum sample point from that line,
normalized by interocular distance. Per-grade medians observed:

    normal    0.0067      moderate  0.0063
    mild      0.0097      severe    0.0150

SCOPE -- IMPORTANT:
This is a monotonic ranking relationship, not a four-class classifier.
Four-class leave-one-out accuracy was 25%, at chance. Normal, mild and
moderate overlap heavily; severe separates. Treat the output as
"more deviated / less deviated," and at most as severe vs not-severe.

It measures EXTERNAL dorsal position only. Internal septal deviation is
graded on CT via the Elahi angle using intracranial landmarks and cannot
be obtained from a photograph.

POSE SENSITIVITY:
The measurement correlates with head yaw (rho = +0.577). The grade
correlation survives controlling for yaw, but photos should still pass the
pose gate before this is trusted.
"""

import numpy as np

L_INNER_CANTHUS = 133
R_INNER_CANTHUS = 362
PHILTRUM = 164
L_EYE_OUTER = 33
R_EYE_OUTER = 263

# Dorsum sample points, radix -> tip. Index 168 defines the top of the
# dorsum and is excluded from the max, since it sits at the reference end.
DORSUM_IDXS = [168, 6, 197, 195, 5, 4, 1]

# Observed within-person SD across 5 repeat photos of one subject.
MEASUREMENT_SD = 0.00158

# Median of the severe group; below this, grades overlap and are not
# separable by this measurement.
SEVERE_MEDIAN = 0.0150
NONSEVERE_MEDIAN = 0.0075


def compute_dorsal_offset(face_landmarks, image_width, image_height):
    """
    Args:
        face_landmarks: MediaPipe landmark list
        image_width, image_height: pixel dimensions

    Returns:
        dict with max_offset, per-point profile, direction, and an
        uncertainty flag -- or None if geometry is degenerate.
    """
    def px(i):
        lm = face_landmarks[i]
        return np.array([lm.x * image_width, lm.y * image_height], dtype=float)

    canthal_mid = (px(L_INNER_CANTHUS) + px(R_INNER_CANTHUS)) / 2.0
    philtrum = px(PHILTRUM)

    interocular = np.linalg.norm(px(R_EYE_OUTER) - px(L_EYE_OUTER))
    if interocular < 1e-6:
        return None

    d = philtrum - canthal_mid
    L = np.linalg.norm(d)
    if L < 1e-6:
        return None

    profile = {}
    for idx in DORSUM_IDXS:
        p = px(idx)
        signed = ((p[0] - canthal_mid[0]) * d[1]
                  - (p[1] - canthal_mid[1]) * d[0]) / L
        profile[idx] = round(signed / interocular, 5)

    scored = {i: val for i, val in profile.items() if i != DORSUM_IDXS[0]}
    max_idx = max(scored, key=lambda i: abs(scored[i]))
    max_offset = abs(scored[max_idx])
    signed_at_max = scored[max_idx]

    if max_offset < 2 * MEASUREMENT_SD:
        direction = "not determinable"
    else:
        direction = "right" if signed_at_max > 0 else "left"

    return {
        "max_offset": round(max_offset, 5),
        "max_at_landmark": max_idx,
        "direction": direction,
        "profile": profile,
        "uncertainty": MEASUREMENT_SD,
        "interocular_px": round(float(interocular), 1),
    }


def interpret(max_offset: float) -> dict:
    """
    Maps offset to a defensible verbal band.

    Deliberately coarse. Four-class classification on this measurement was
    at chance (25% LOO); only the severe group separated. Reporting mild vs
    moderate here would claim precision the data does not support.
    """
    midpoint = (SEVERE_MEDIAN + NONSEVERE_MEDIAN) / 2.0

    if max_offset >= SEVERE_MEDIAN:
        band = "marked external deviation"
    elif max_offset >= midpoint:
        band = "possible external deviation"
    else:
        band = "no marked external deviation"

    near_boundary = (abs(max_offset - midpoint) < 2 * MEASUREMENT_SD
                     or abs(max_offset - SEVERE_MEDIAN) < 2 * MEASUREMENT_SD)

    return {
        "band": band,
        "near_boundary": near_boundary,
        "note": ("This result sits close to a threshold and should be "
                 "treated as inconclusive." if near_boundary else ""),
    }
