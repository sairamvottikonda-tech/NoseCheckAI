"""
Proper 3D head pose (roll/pitch/yaw) detection using MediaPipe's actual
facial transformation matrix, replacing the earlier heuristic-based
tilt detection (which used a crude nose-to-face-ratio bucket/formula
that we found and disabled tonight after it produced false "tilted"
warnings on genuinely level photos).

This uses MediaPipe's real 3D rotation matrix output, which is a
legitimate, properly-grounded computation (not a heuristic guess).

Requires MediaPipe's FaceLandmarker to be configured with
output_facial_transformation_matrixes=True.
"""

import numpy as np


def compute_head_pose(transformation_matrix: np.ndarray) -> dict:
    """
    Extract roll, pitch, yaw in degrees from MediaPipe's 4x4 facial
    transformation matrix.

    Args:
        transformation_matrix: 4x4 numpy array from
            result.facial_transformation_matrixes[0]

    Returns:
        dict with 'roll', 'pitch', 'yaw' in degrees, and 'is_frontal'
        bool (True if all angles are within threshold).
    """
    rotation_matrix = transformation_matrix[:3, :3]

    pitch = np.degrees(np.arctan2(-rotation_matrix[2, 1], rotation_matrix[2, 2]))
    yaw = np.degrees(np.arctan2(
        rotation_matrix[2, 0],
        np.sqrt(rotation_matrix[2, 1]**2 + rotation_matrix[2, 2]**2)
    ))
    roll = np.degrees(np.arctan2(rotation_matrix[1, 0], rotation_matrix[0, 0]))

    MAX_ANGLE = 10.0  # degrees - more permissive than the 3.0 suggested,
                       # since real selfies rarely achieve <3 degrees and
                       # we don't want to over-reject usable photos
    is_frontal = abs(roll) <= MAX_ANGLE and abs(pitch) <= MAX_ANGLE and abs(yaw) <= MAX_ANGLE

    return {
        "roll": round(float(roll), 2),
        "pitch": round(float(pitch), 2),
        "yaw": round(float(yaw), 2),
        "is_frontal": bool(is_frontal),
    }


def get_pose_warning(pose: dict) -> str:
    """Generate user-facing warning if head pose is out of acceptable range."""
    if pose["is_frontal"]:
        return ""
    issues = []
    if abs(pose["roll"]) > 10:
        issues.append(f"head tilted {abs(pose['roll']):.0f}° - try to keep your head level")
    if abs(pose["pitch"]) > 10:
        issues.append(f"looking {'up' if pose['pitch'] > 0 else 'down'} {abs(pose['pitch']):.0f}° - try looking straight at the camera")
    if abs(pose["yaw"]) > 10:
        issues.append(f"head turned {abs(pose['yaw']):.0f}° - please face the camera directly")
    return "⚠️ Photo angle issue: " + "; ".join(issues)
