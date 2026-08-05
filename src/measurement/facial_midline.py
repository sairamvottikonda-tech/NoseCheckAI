"""
Facial midline reference for nasal deviation measurement.

WHY THIS REPLACES THE FACE-EDGE MIDLINE:
The previous midline averaged the face-edge midpoint (landmarks 234/454)
with the eye-corner midpoint. Face edges shift with hairline, jaw shape,
soft-tissue asymmetry, and head rotation, so the reference line moved with
factors unrelated to the nose.

Measured on 10 photos, three midline definitions disagreed by a mean of
3.32 px and a max of 8.80 px. The full normal-to-severe range of dorsal
offset in this dataset spans roughly 1.5 px. The reference line was
therefore uncertain by more than twice the magnitude of the signal it was
used to measure.

DEFINITION USED HERE (glabella -> menton):
From the rhinoplasty literature: "A line drawn from midline glabella to
menton helps to assess nasal symmetry. This simple method is one of the
best means to analyze septal deviation and the position of the nasal
bones. It also emphasizes asymmetries of the maxilla or mandible."

Both endpoints are midline skeletal landmarks. Neither depends on face
edges or on bilateral structures that can be individually asymmetric.

HONEST SCOPE NOTE:
This is a correctness fix, not an accuracy fix. Two earlier experiments
already used anchored midlines (nasion->lip, glabella->menton) and still
found no correlation between measured deviation and clinical grade. This
change makes the app's measurement well-defined and reproducible; it does
not by itself make it clinically predictive.
"""

import numpy as np

GLABELLA_IDX = 9
MENTON_IDX = 152


def compute_midline(landmarks_px: dict):
    """
    Args:
        landmarks_px: dict needing 'glabella' and 'menton' as (x, y) tuples.

    Returns:
        (p0, p1) defining the midline, or None if degenerate.
    """
    g = np.asarray(landmarks_px["glabella"], dtype=float)
    m = np.asarray(landmarks_px["menton"], dtype=float)
    if np.linalg.norm(m - g) < 1e-6:
        return None
    return (g, m)


def signed_offset(point, midline) -> float:
    """
    Signed perpendicular distance from `point` to the midline.
    Positive = right of the line (in image coordinates, viewer's right).
    """
    p = np.asarray(point, dtype=float)
    a, b = midline
    d = b - a
    L = np.linalg.norm(d)
    if L < 1e-9:
        return 0.0
    return float(((p[0]-a[0])*d[1] - (p[1]-a[1])*d[0]) / L)


def midline_x_at_height(midline, y: float) -> float:
    """x-coordinate of the midline at a given image row."""
    a, b = midline
    if abs(b[1] - a[1]) < 1e-9:
        return float(a[0])
    t = (y - a[1]) / (b[1] - a[1])
    return float(a[0] + t * (b[0] - a[0]))


def extract_midline_landmarks(face_landmarks, image_width, image_height) -> dict:
    """Pull glabella and menton from a MediaPipe result as float pixels."""
    def px(i):
        lm = face_landmarks[i]
        return (lm.x * image_width, lm.y * image_height)
    return {"glabella": px(GLABELLA_IDX), "menton": px(MENTON_IDX)}
