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

    Returns the x-coordinate of the midline (constant vertical line).
    """
    mid = midpoint(left_face, right_face)
    return mid[0]


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
