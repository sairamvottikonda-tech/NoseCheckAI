"""
Multi-pass landmark detection for NoseCheck.

Runs MediaPipe detection multiple times at slightly different image scales
and averages the results. This reduces the run-to-run measurement noise
we observed (same photo producing different lateral_deviation/septal_angle
on separate runs), by smoothing out MediaPipe's detection jitter rather
than trusting a single potentially-noisy pass.

Usage:
    from stable_detector import detect_landmarks_stable
    landmarks, confidence = detect_landmarks_stable(image)
"""

import sys
sys.path.insert(0, '.')
import cv2
import numpy as np

from src.landmark_detection.detector import detect_landmarks


def _resize_image(image, scale_factor):
    h, w = image.shape[:2]
    new_h, new_w = int(h * scale_factor), int(w * scale_factor)
    return cv2.resize(image, (new_w, new_h))


def detect_landmarks_stable(image, n_passes=3):
    """
    Run landmark detection multiple times at slightly different scales
    and return averaged landmarks plus a confidence score based on
    how much the passes agreed with each other.

    Args:
        image: Input image as NumPy array.
        n_passes: Number of detection passes to run (default 3).

    Returns:
        (averaged_landmarks, confidence_dict) or (None, None) if detection
        fails on all passes. confidence_dict contains 'agreement_score'
        (0-100, higher = more consistent across passes) and
        'max_deviation_px' (largest single-landmark disagreement in pixels).
    """
    scales = [1.0, 0.95, 1.05][:n_passes]
    all_results = []

    for scale in scales:
        scaled_image = _resize_image(image, scale) if scale != 1.0 else image
        landmarks = detect_landmarks(scaled_image)
        if landmarks is not None:
            # Rescale landmark coordinates back to original image scale
            if scale != 1.0:
                landmarks = {k: (x / scale, y / scale) for k, (x, y) in landmarks.items()}
            all_results.append(landmarks)

    if not all_results:
        return None, None

    if len(all_results) == 1:
        # Only one successful pass - can't measure agreement, low confidence
        return all_results[0], {"agreement_score": 33.0, "max_deviation_px": None, "n_successful_passes": 1}

    # Average landmarks across all successful passes
    all_keys = all_results[0].keys()
    averaged = {}
    max_deviation = 0.0

    for key in all_keys:
        xs = [r[key][0] for r in all_results if key in r]
        ys = [r[key][1] for r in all_results if key in r]
        if not xs:
            continue
        avg_x, avg_y = np.mean(xs), np.mean(ys)
        averaged[key] = (avg_x, avg_y)

        # Track max deviation from the average across passes (for this landmark)
        for x, y in zip(xs, ys):
            dev = np.sqrt((x - avg_x)**2 + (y - avg_y)**2)
            max_deviation = max(max_deviation, dev)

    # Agreement score: 100 = perfect agreement, decreases as deviation grows
    # A 5px max deviation on a ~250px-wide face is considered high confidence;
    # 20px+ deviation is considered low confidence (landmark placement unstable)
    agreement_score = max(0, min(100, 100 - (max_deviation / 0.20)))

    confidence = {
        "agreement_score": round(agreement_score, 1),
        "max_deviation_px": round(max_deviation, 2),
        "n_successful_passes": len(all_results),
    }

    return averaged, confidence


if __name__ == "__main__":
    from src.image_processing.image_loader import load_image
    from src.image_processing.preprocessor import preprocess

    if len(sys.argv) < 2:
        print("Usage: python stable_detector.py path/to/photo.png")
        sys.exit(1)

    path = sys.argv[1]
    image = load_image(path)
    processed = preprocess(image)

    landmarks, confidence = detect_landmarks_stable(processed, n_passes=3)

    if landmarks is None:
        print("FAILED: no face detected in any pass")
        sys.exit(1)

    print(f"Agreement score: {confidence['agreement_score']}/100")
    print(f"Max deviation across passes: {confidence['max_deviation_px']}px")
    print(f"Successful passes: {confidence['n_successful_passes']}")
    print()
    if confidence['agreement_score'] < 60:
        print("⚠️  LOW CONFIDENCE - landmark placement was unstable across passes.")
        print("    This measurement may be unreliable. Consider retaking photo.")
    else:
        print("✓ Landmark detection was consistent across passes.")
    print()
    print("Averaged landmarks:")
    for k, v in landmarks.items():
        print(f"  {k}: ({v[0]:.1f}, {v[1]:.1f})")
