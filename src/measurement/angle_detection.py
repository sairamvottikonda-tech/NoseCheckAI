"""
Camera angle detection and compensation for NoseCheck.

Detects if the camera is tilted (upward/downward/sideways) and adjusts
measurements accordingly for more accurate scoring.
"""

import math
import numpy as np


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
    # Get key landmarks for angle estimation
    nose_bridge_y = landmarks['nose_bridge'][1]
    nose_tip_y = landmarks['nose_tip'][1]
    
    # Estimate vertical tilt from nose bridge-to-tip ratio
    # In frontal view: tip is below bridge (typical face proportions)
    # In upward tilt: tip appears closer to bridge (foreshortening)
    nose_length = abs(nose_tip_y - nose_bridge_y)
    
    # Get face height estimate (for normalization)
    # Approximate face height from nose position
    # Typical nose is ~1/3 down from top of face
    
    # Estimate tilt from nostril visibility
    # In upward angle: nostrils more visible, wider apparent spacing
    left_nostril_inner = landmarks.get('left_nostril_inner', (0, 0))
    right_nostril_inner = landmarks.get('right_nostril_inner', (0, 0))
    nostril_span_y = abs(left_nostril_inner[1] - right_nostril_inner[1])
    
    # Heuristic: if nostrils are at very similar Y (small span), likely upward angle
    # If nostrils have Y-difference, more frontal
    
    # Estimate vertical tilt (rough heuristic)
    # Shorter apparent nose length + similar nostril Y → upward tilt
    # Use ratio of nose length to face width
    face_width = abs(landmarks['right_face_edge'][0] - landmarks['left_face_edge'][0])
    nose_to_face_ratio = nose_length / face_width if face_width > 0 else 0
    
    # Typical frontal nose_to_face_ratio: ~0.15-0.20
    # Upward tilt reduces this ratio (foreshortening)
    # Downward tilt increases it
    
    if nose_to_face_ratio < 0.12:
        vertical_tilt = 35  # Significant upward tilt (~30-40°)
    elif nose_to_face_ratio < 0.15:
        vertical_tilt = 20  # Moderate upward tilt (~15-25°)
    elif nose_to_face_ratio > 0.22:
        vertical_tilt = -20  # Downward tilt
    else:
        vertical_tilt = 0  # Approximately frontal
    
    # Check horizontal tilt from face edges symmetry
    left_x = landmarks['left_face_edge'][0]
    right_x = landmarks['right_face_edge'][0]
    face_center_x = (left_x + right_x) / 2
    
    nose_tip_x = landmarks['nose_tip'][0]
    horizontal_offset = abs(nose_tip_x - face_center_x) / face_width
    
    # If nose significantly off-center, face may be rotated
    if horizontal_offset > 0.05:
        horizontal_tilt = 15  # Rotated
    else:
        horizontal_tilt = 0  # Frontal
    
    # Quality score
    is_frontal = abs(vertical_tilt) < 15 and abs(horizontal_tilt) < 15
    
    # Quality decreases with angle deviation
    angle_deviation = math.sqrt(vertical_tilt**2 + horizontal_tilt**2)
    quality_score = max(0, 100 - angle_deviation * 2)
    
    return {
        'vertical_tilt': vertical_tilt,
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
        # Nearly frontal - no compensation needed
        return adjusted
    
    # Compensation factors based on tilt angle
    # These are approximate - would need empirical calibration
    tilt_rad = math.radians(abs(vertical_tilt))
    
    if vertical_tilt > 10:  # Upward tilt
        # Foreshortening correction: angles appear smaller, need to scale up
        angle_correction = 1.0 / math.cos(tilt_rad)  # Inverse foreshortening
        adjusted['septal_angle'] = measurements['septal_angle'] * angle_correction
        
        # Lateral deviation may be underestimated (compressed in vertical axis)
        # But not significantly affected in horizontal plane - minimal correction
        
        # Nostril asymmetry: upward angle shows nostrils more clearly
        # May need slight adjustment, but keep conservative
        
    elif vertical_tilt < -10:  # Downward tilt
        # Less common - minimal correction for now
        pass
    
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
    
    if horizontal > 15:
        warnings.append("Face appears rotated - Please face camera directly")
    
    if warnings:
        return "⚠️ Photo angle issue: " + "; ".join(warnings)
    
    return ""
