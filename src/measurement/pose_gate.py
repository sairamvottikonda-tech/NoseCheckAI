"""
Head pose gate for photo quality.

WHAT THIS DOES:
Rejects photos where the head is turned far enough that a straight nose
will project off the 2D facial midline, corrupting any midline-referenced
measurement.

EVIDENCE (measured on real photos, 2026-08-02):
The same nose, same person, same pre-surgery period, photographed twice:
    presurgery_test.png      yaw -11.97 deg  ->  deviation angle 5.45 deg
    clinical_presurgery.png  yaw  -3.39 deg  ->  deviation angle 0.09 deg
A 60x difference in measured deviation, driven by head rotation rather
than anatomy.

Across 14 photos with yaw under ~3.5 deg, no relationship between yaw and
measured deviation was detectable (r = -0.13). So the corruption is
specific to larger head turns, not a gradual effect present in every photo.
The threshold below is set accordingly.

WHAT THIS DELIBERATELY DOES NOT DO:
An earlier version attempted to de-rotate landmarks using MediaPipe's 3D
coordinates and measure anyway. That was removed after testing: on a photo
with only 3.4 deg of yaw, "correction" changed the measured angle from
0.09 to 1.29 deg -- a 14x shift introduced by the correction itself.
MediaPipe's z values are relative monocular depth estimates and are too
noisy to support de-rotation at this precision. Rejecting a bad photo is
honest; silently transforming it is not.
"""

import numpy as np


# Beyond this, projection error from head turn is large enough to
# invalidate midline-referenced measurements.
MAX_YAW_DEG = 8.0

# Advisory only -- measurement is still usable, but worth flagging.
ADVISORY_YAW_DEG = 4.0


def extract_pose(transformation_matrix: np.ndarray) -> dict:
    """Roll, pitch, yaw in degrees from MediaPipe's 4x4 transform matrix."""
    R = transformation_matrix[:3, :3]
    pitch = float(np.degrees(np.arctan2(-R[2, 1], R[2, 2])))
    yaw = float(np.degrees(np.arctan2(
        R[2, 0], np.sqrt(R[2, 1] ** 2 + R[2, 2] ** 2)
    )))
    roll = float(np.degrees(np.arctan2(R[1, 0], R[0, 0])))
    return {"roll": round(roll, 2), "pitch": round(pitch, 2), "yaw": round(yaw, 2)}


def check_pose(transformation_matrix: np.ndarray) -> dict:
    """
    Returns:
        dict with pose angles, 'accepted' bool, 'advisory' bool, 'message'.
    """
    pose = extract_pose(transformation_matrix)
    yaw = abs(pose["yaw"])

    if yaw > MAX_YAW_DEG:
        return {
            **pose,
            "accepted": False,
            "advisory": False,
            "message": (
                f"Your head is turned about {yaw:.0f}\u00b0 to the side. At this "
                f"angle, a perfectly straight nose can look deviated in a photo, "
                f"so this image can't be measured reliably. Please retake it "
                f"looking straight at the camera."
            ),
        }

    if yaw > ADVISORY_YAW_DEG:
        return {
            **pose,
            "accepted": True,
            "advisory": True,
            "message": (
                f"Slight head turn detected ({yaw:.0f}\u00b0). Result is usable, but "
                f"a straight-on photo will be more accurate."
            ),
        }

    return {**pose, "accepted": True, "advisory": False, "message": ""}


if __name__ == "__main__":
    # Values measured from real photos during development
    samples = [
        (np.array([[ 0.978, 0.033, -0.207, 0],
                   [-0.034, 0.999, -0.002, 0],
                   [ 0.207, 0.009,  0.978, 0],
                   [ 0,     0,      0,     1]]), "high yaw, expect reject"),
    ]
    for m, desc in samples:
        r = check_pose(m)
        print(f"{desc}: yaw={r['yaw']}, accepted={r['accepted']}")
        if r["message"]:
            print(f"   -> {r['message']}")
