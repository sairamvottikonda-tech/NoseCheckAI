"""
Camera angle detection and compensation for NoseCheck.

Detects if the camera is tilted (upward/downward/sideways) and adjusts
measurements accordingly for more accurate scoring.
"""

import math


def detect_camera_tilt(landmarks: dict) -> dict:
    """
    Detect camera tilt angle from facial landmarks.

    Uses eye positions, nose bridge, and face edges to estimate
    whether camera is level, tilted up, or tilted down.

    Args:
        landmarks: Dict of facial landmark positions (x, y).

    Returns:
        Dict with:
          - vertical_tilt: degrees from horizontal (positive = upward tilt)
          - horizontal_tilt: degrees (positive = right tilt)
          - is_frontal: bool (True if within acceptable range)
          - quality_score: 0-100 (100 = perfect frontal)
    """
    nose_bridge_y = landmarks['nose_bridge'][1]
    nose_tip_y = landmarks['nose_tip'][1]
    nose_length = abs(nose_tip_y - nose_bridge_y)

    face_width = abs(landmarks['right_face_edge'][0] - landmarks['left_face_edge'][0])
    nose_to_face_ratio = nose_length / face_width if face_width > 0 else 0

    # FIXED (previously a 4-bucket lookup table that assigned every photo
    # with nose_to_face_ratio > 0.22 the SAME hardcoded -20 degree value,
    # regardless of how far above 0.22 the ratio actually was -- confirmed
    # bug: every single test photo in one debugging session produced
    # vertical_tilt=-20 exactly, which is not plausible for genuinely
    # different photos/people, and revealed the code was bucketing rather
    # than computing a continuous angle).
    #
    # Continuous estimate: deviation from an assumed-frontal baseline ratio
    # (~0.18, the old code's implicit frontal range midpoint) scaled to
    # degrees. This is still an approximate heuristic -- not empirically
    # calibrated against real angle-labeled photos -- but it no longer
    # collapses every steep-angle photo to an identical fixed value, which
    # was actively causing systematic under-correction in
    # compensate_for_tilt() for downward-tilted photos.
    baseline_ratio = 0.18
    ratio_deviation = nose_to_face_ratio - baseline_ratio

    if ratio_deviation < 0:
        vertical_tilt = min(45, -ratio_deviation * 291.7)
    else:
        vertical_tilt = max(-45, -ratio_deviation * 200.0)

    # Check horizontal tilt (head yaw/roll) using the EYE LINE, not nose
    # position, to avoid confounding real nasal deviation with rotation.
    left_eye_outer = landmarks.get('left_eye_outer')
    right_eye_outer = landmarks.get('right_eye_outer')

    if left_eye_outer is not None and right_eye_outer is not None:
        eye_dx = right_eye_outer[0] - left_eye_outer[0]
        eye_dy = right_eye_outer[1] - left_eye_outer[1]
        horizontal_tilt = math.degrees(math.atan2(eye_dy, eye_dx)) if abs(eye_dx) > 1e-6 else 0.0
    else:
        left_x = landmarks['left_face_edge'][0]
        right_x = landmarks['right_face_edge'][0]
        face_center_x = (left_x + right_x) / 2
        nose_tip_x = landmarks['nose_tip'][0]
        horizontal_offset = abs(nose_tip_x - face_center_x) / face_width
        horizontal_tilt = 15.0 if horizontal_offset > 0.05 else 0.0

    is_frontal = abs(vertical_tilt) < 15 and abs(horizontal_tilt) < 15
    angle_deviation = math.sqrt(vertical_tilt**2 + horizontal_tilt**2)
    quality_score = max(0, 100 - angle_deviation * 2)

    return {
        'vertical_tilt': round(vertical_tilt, 2),
        'horizontal_tilt': horizontal_tilt,
        'is_frontal': is_frontal,
        'quality_score': quality_score,
        'nose_to_face_ratio': nose_to_face_ratio,
    }


def compensate_for_tilt(measurements: dict, tilt_info: dict) -> dict:
    """
    Adjust measurements to compensate for camera tilt.

    Upward tilt causes:
    - Foreshortening of nose (appears shorter)
    - Increased nostril visibility (appears wider)
    - Reduced apparent septal angle

    Args:
        measurements: Raw measurements from asymmetry_calculator.
        tilt_info: Output from detect_camera_tilt().

    Returns:
        Adjusted measurements dict.
    """
    adjusted = measurements.copy()

    vertical_tilt = tilt_info['vertical_tilt']

    if abs(vertical_tilt) < 10:
        return adjusted

    tilt_rad = math.radians(abs(vertical_tilt))

    if vertical_tilt > 10:  # Upward tilt
        angle_correction = 1.0 / math.cos(tilt_rad)
        adjusted['septal_angle'] = measurements['septal_angle'] * angle_correction

    elif vertical_tilt < -10:  # Downward tilt
        angle_correction = 1.0 / math.cos(tilt_rad)
        adjusted['septal_angle'] = measurements['septal_angle'] * angle_correction

    return adjusted


def get_angle_warning(tilt_info: dict) -> str:
    """
    Generate user-facing warning about photo angle.

    Args:
        tilt_info: Output from detect_camera_tilt().

    Returns:
        Warning message string (empty if angle is acceptable).
    """
    if tilt_info['is_frontal']:
        return ""

    vertical = tilt_info['vertical_tilt']
    horizontal = tilt_info['horizontal_tilt']

    warnings = []

    if vertical > 20:
        warnings.append(f"Camera tilted UPWARD ~{vertical:.0f}° - Please hold camera at eye level")
    elif vertical < -20:
        warnings.append(f"Camera tilted DOWNWARD ~{abs(vertical):.0f}° - Please hold camera at eye level")

    if abs(horizontal) > 15:
        warnings.append(f"Head appears tilted/rotated ~{abs(horizontal):.0f}° - Please face camera directly with head level")

    if warnings:
        return "⚠️ Photo angle issue: " + "; ".join(warnings)

    return ""
