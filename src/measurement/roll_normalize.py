"""
Roll normalization: rotate the image so the eyes are level, then re-run
landmark detection on the rotated image.

WHY THIS IS DIFFERENT FROM THE DISCARDED YAW CORRECTION:
An earlier attempt corrected for head YAW by manipulating the 3D landmark
cloud using MediaPipe's z-coordinates. Those are noisy monocular depth
estimates, and the correction made things worse (0.09 -> 1.29 deg error on
one test photo). It was removed.

This corrects ROLL (in-plane head tilt) by rotating the actual image
pixels -- an exact 2D operation with no depth estimation involved -- and
then re-running full landmark detection on the rotated image. This is a
fundamentally more reliable operation.

MEASURED EFFECT (2026-08-07):
  Within-person reproducibility (5 repeat photos of one face):
      raw SD 0.00158 -> roll-normalized SD 0.00081  (~2x improvement)
  Grade correlation (35 graded photos):
      raw rho +0.609 (p=0.0001) -> roll-normalized rho +0.642 (p<0.0001)

Both metrics improved. This is retained as a preprocessing step, applied
before the existing yaw pose-gate (which still checks the ROTATED image,
since yaw is a 3D quantity roll correction does not address).
"""

import cv2
import numpy as np
import mediapipe as mp

L_EYE_IDX = 33
R_EYE_IDX = 263


def normalize_roll(image: np.ndarray, landmarker) -> tuple:
    """
    Detects landmarks, computes roll from eye-corner positions, and
    returns the image rotated so the eyes are level, along with the
    landmarks re-detected on the rotated image.

    Args:
        image: BGR image (already preprocessed/resized)
        landmarker: an initialized MediaPipe FaceLandmarker instance

    Returns:
        (rotated_image, result) where result is the MediaPipe detection
        result on the ROTATED image. Returns (image, None) if no face is
        detected on the first pass.
    """
    h, w = image.shape[:2]
    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    first = landmarker.detect(mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb))

    if not first.face_landmarks:
        return image, None

    fl = first.face_landmarks[0]
    le = np.array([fl[L_EYE_IDX].x * w, fl[L_EYE_IDX].y * h])
    re = np.array([fl[R_EYE_IDX].x * w, fl[R_EYE_IDX].y * h])
    roll = float(np.degrees(np.arctan2(re[1] - le[1], re[0] - le[0])))

    center = tuple(((le + re) / 2).astype(float))
    M = cv2.getRotationMatrix2D(center, roll, 1.0)
    rotated = cv2.warpAffine(
        image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE
    )

    rgb2 = cv2.cvtColor(rotated, cv2.COLOR_BGR2RGB)
    second = landmarker.detect(mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb2))

    if not second.face_landmarks:
        # Rotation pushed the face out of frame or detection failed on the
        # rotated image; fall back to the original, unrotated result.
        return image, first

    return rotated, second
