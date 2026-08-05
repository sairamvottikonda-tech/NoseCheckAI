"""
Dorsal deviation profile: maximum perpendicular displacement of the nasal
dorsum from the facial midline, sampled along the full length of the bridge.

RATIONALE:
The crooked-nose literature classifies external nasal deviation into three
types (I-shaped, C-shaped, S-shaped). In C- and S-shaped deviation, the
dorsum bows away from midline and the tip returns toward center. One study
of 63 crooked-nose patients found ~30% I-type and ~70% C-type.

A tip-referenced angle (nasion -> tip vs nasion -> upper lip) therefore
misses the majority of crooked noses: it samples the one point that has
returned to midline. Measured on 15 labeled photos, that angle placed every
clinically-graded patient under 1.4 deg.

This module instead samples perpendicular offset at every available dorsum
point and reports the maximum, plus the sign pattern that distinguishes
deviation type.

MIDLINE DEFINITION:
Nasion (168) -> upper lip midpoint (0). Both are soft-tissue landmarks on
the facial midline, verified visually. This avoids face-edge-derived
midlines, which shift with head rotation and facial asymmetry.

NORMALIZATION:
Offsets are divided by interocular distance (outer eye corner to outer eye
corner) to make values comparable across image sizes and face sizes.
"""

import math

NASION_IDX = 168
UPPER_LIP_IDX = 0
LEFT_EYE_OUTER_IDX = 33
RIGHT_EYE_OUTER_IDX = 263

# Dorsum sample points, ordered from radix down to tip
DORSUM_IDXS = [168, 6, 197, 195, 5, 4, 1]


def _perp_offset(point, line_a, line_b):
    """
    Signed perpendicular distance from point to the line through
    line_a -> line_b. Positive = right side of the line as drawn
    top-to-bottom in image coordinates.
    """
    ax, ay = line_a
    bx, by = line_b
    px, py = point

    dx, dy = bx - ax, by - ay
    length = math.hypot(dx, dy)
    if length < 1e-9:
        return 0.0

    # 2D cross product gives signed area; divide by length for distance
    cross = (px - ax) * dy - (py - ay) * dx
    return cross / length


def compute_dorsal_profile(face_landmarks, image_width, image_height) -> dict:
    """
    Args:
        face_landmarks: MediaPipe landmark list
        image_width, image_height: pixel dimensions

    Returns dict with:
        max_offset_norm   -- largest |offset| along dorsum, normalized
        max_at_index      -- which dorsum landmark showed the max
        profile           -- normalized signed offset at each dorsum point
        deviation_type    -- 'straight' | 'I/C-type' | 'S-type'
        interocular_px    -- normalization denominator, for transparency
    """
    def px(i):
        lm = face_landmarks[i]
        return (lm.x * image_width, lm.y * image_height)

    nasion = px(NASION_IDX)
    upper_lip = px(UPPER_LIP_IDX)
    l_eye = px(LEFT_EYE_OUTER_IDX)
    r_eye = px(RIGHT_EYE_OUTER_IDX)

    interocular = math.dist(l_eye, r_eye)
    if interocular < 1e-6:
        return None

    profile = {}
    for idx in DORSUM_IDXS:
        raw = _perp_offset(px(idx), nasion, upper_lip)
        profile[idx] = round(raw / interocular, 5)

    # Exclude the nasion itself: it defines the line, so its offset is 0
    scored = {i: v for i, v in profile.items() if i != NASION_IDX}

    max_idx = max(scored, key=lambda i: abs(scored[i]))
    max_offset = abs(scored[max_idx])

    # Sign pattern -> deviation type. Ignore points below the noise floor.
    NOISE = 0.002
    signs = [(1 if v > NOISE else (-1 if v < -NOISE else 0))
             for v in scored.values()]
    nonzero = [s for s in signs if s != 0]

    if not nonzero:
        dev_type = "straight"
    elif len(set(nonzero)) > 1:
        dev_type = "S-type"
    else:
        dev_type = "I/C-type"

    return {
        "max_offset_norm": round(max_offset, 5),
        "max_at_index": max_idx,
        "profile": profile,
        "deviation_type": dev_type,
        "interocular_px": round(interocular, 1),
    }
