"""
Geometry utilities for nasal asymmetry calculations.

Provides functions for computing midline, distances, and angles
from landmark coordinates.
"""

import math
from typing import NamedTuple


class Point(NamedTuple):
    """2D point (x, y)."""
    x: float
    y: float


def distance(p1, p2):
    """
    Euclidean distance between two points.

    Args:
        p1: (x1, y1)
        p2: (x2, y2)

    Returns:
        Distance in pixels.
    """
    return math.sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2)


def midpoint(p1, p2):
    """
    Midpoint between two points.

    Args:
        p1: (x1, y1)
        p2: (x2, y2)

    Returns:
        (mid_x, mid_y)
    """
    return ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2)


def facial_midline(left_face, right_face):
    """
    Compute the facial midline as the vertical line through the midpoint
    of the left and right face edges.

    NOTE: this is a simple approximation that assumes the head has zero
    roll (perfectly level). See `robust_facial_midline` for a version that
    corrects for head tilt using eye landmarks as well -- prefer that one
    for real-world photos where the head is rarely held perfectly level.

    Returns the x-coordinate of the midline (constant vertical line).
    """
    mid = midpoint(left_face, right_face)
    return mid[0]


def robust_facial_midline(left_face, right_face, left_eye_outer=None, right_eye_outer=None,
                           left_eye_inner=None, right_eye_inner=None):
    """
    Compute a head-tilt-robust facial midline x-coordinate.

    Using only the face-edge midpoint (facial_midline above) is sensitive to
    head roll: tilting your head a few degrees shifts where that midpoint
    falls, which gets misread as nasal deviation. This version averages the
    midpoint of the face edges with the midpoint of the eye corners (when
    available) -- two independent estimates of the true vertical midline --
    which substantially reduces sensitivity to small head tilts since both
    eye and face-edge midpoints shift together under roll but the averaging
    cancels noise from any single landmark pair being slightly off.

    Args:
        left_face, right_face: face edge landmarks (always required).
        left_eye_outer, right_eye_outer, left_eye_inner, right_eye_inner:
            eye corner landmarks. If any are missing/None, falls back to the
            face-edge-only midline.

    Returns:
        x-coordinate of the estimated midline.
    """
    face_mid_x = midpoint(left_face, right_face)[0]

    eye_points = [left_eye_outer, right_eye_outer, left_eye_inner, right_eye_inner]
    if all(p is not None for p in eye_points):
        eye_mid_x = (
            left_eye_outer[0] + right_eye_outer[0]
            + left_eye_inner[0] + right_eye_inner[0]
        ) / 4.0
        return (face_mid_x + eye_mid_x) / 2.0

    return face_mid_x


def distance_to_midline(point, midline_x):
    """
    Signed distance from a point to the vertical midline.
    Positive = right of midline, Negative = left of midline.

    Args:
        point: (x, y)
        midline_x: x-coordinate of midline.

    Returns:
        Signed horizontal distance in pixels.
    """
    return point[0] - midline_x


def angle_from_vertical(p1, p2):
    """
    Angle of the line from p1 to p2 from the vertical (y-axis).
    Vertical = 0 degrees. Tilt right = positive, tilt left = negative.

    Args:
        p1: Upper point (e.g., nose bridge)
        p2: Lower point (e.g., nose tip)

    Returns:
        Angle in degrees (-90 to 90).
    """
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]

    if abs(dy) < 1e-6:
        return 90.0 if dx >= 0 else -90.0

    # Angle from vertical: atan2(dx, dy) gives angle from y-axis
    angle_rad = math.atan2(dx, dy)
    return math.degrees(angle_rad)


def nostril_width(outer, inner):
    """
    Width of a nostril (horizontal distance from outer to inner landmark).

    Args:
        outer: Outer nostril landmark
        inner: Inner nostril landmark

    Returns:
        Width in pixels.
    """
    return abs(outer[0] - inner[0])
