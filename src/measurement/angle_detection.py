"""
Camera angle detection and compensation for NoseCheck - v3

STATUS: vertical_tilt estimation is NOT reliable enough to act on.
Tested across 16+ real photos tonight (2026-07-18), including several
known to be taken at approximately eye level, and the estimate
consistently returned 18-45 degrees of "tilt" regardless of actual
camera position. Two different estimation approaches were tried
(nose-to-face ratio bucketing, then eye-to-nose-tip ratio) and both
produced the same false-positive pattern.

The angle warning is DISABLED (always returns empty string) until a
properly validated tilt estimation method is developed and tested
against photos with KNOWN camera angles (not just assumed-frontal
selfies). Showing a warning that fires on every single photo, including
genuinely well-taken ones, is worse than no warning at all.

The compensate_for_tilt() function is also effectively disabled (tilt
threshold raised so it essentially never triggers) since the tilt
values it would act on are not trustworthy.
"""

import math


def detect_camera_tilt(landmarks: dict) -> dict:
    """
    Detect camera tilt angle from facial landmarks.

    NOTE: vertical_tilt estimation is currently unreliable (see module
    docstring) and should not be trusted for compensation or warnings.
    Returned for informational/debugging purposes only.
    """
    left_eye_outer = landmarks.get('left_eye_outer')
    right_eye_outer = landmarks.get('right_eye_outer')

    face_width = abs(landmarks['right_face_edge'][0] - landmarks['left_face_edge'][0])
    nose_bridge_y = landmarks['nose_bridge'][1]
    nose_tip_y = landmarks['nose_tip'][1]
    nose_length = abs(nose_tip_y - nose_bridge_y)
    nose_to_face_ratio = nose_length / face_width if face_width > 0 else 0

    # Tilt estimation disabled - always report as frontal since the
    # estimate has not been validated and produces false positives on
    # every tested photo, including confirmed eye-level ones.
    vertical_tilt = 0.0

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
        'vertical_tilt': vertical_tilt,
        'horizontal_tilt': horizontal_tilt,
        'is_frontal': is_frontal,
        'quality_score': quality_score,
        'nose_to_face_ratio': nose_to_face_ratio,  # kept for debugging/analysis
    }


def compensate_for_tilt(measurements: dict, tilt_info: dict) -> dict:
    """
    Adjust measurements to compensate for camera tilt.

    Currently a no-op since vertical_tilt is always 0 (see module docstring).
    Kept as a function so calling code doesn't need to change if/when
    tilt detection is properly validated and re-enabled.
    """
    return measurements.copy()


def get_angle_warning(tilt_info: dict) -> str:
    """
    Generate user-facing warning about photo angle.

    Currently disabled - always returns empty string. See module docstring.
    """
    return ""
