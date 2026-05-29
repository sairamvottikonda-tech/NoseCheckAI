#!/usr/bin/env python3
"""
Calibration Workflow for NoseCheck.

Runs the analysis pipeline on all calibration model images and records
raw metrics, normalized scores, and classifications alongside known
ground-truth deviations.

Usage:
    python scripts/calibration_workflow.py

Output:
    data/calibration_models/calibration_results.csv
"""

import csv
import sys
from pathlib import Path

_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_root))

from src.image_processing.image_loader import load_image
from src.image_processing.preprocessor import preprocess
from src.landmark_detection.detector import detect_landmarks
from src.measurement.asymmetry_calculator import calculate, normalize_for_score
from src.measurement.angle_detection import (
    detect_camera_tilt,
    compensate_for_tilt,
)
from src.scoring.score_calculator import calculate_score

CALIBRATION_DIR = _root / "data" / "calibration_models"
METADATA_PATH = CALIBRATION_DIR / "metadata.csv"
RESULTS_PATH = CALIBRATION_DIR / "calibration_results.csv"


def load_metadata():
    """Load calibration metadata CSV."""
    entries = []
    with open(METADATA_PATH, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            entries.append(row)
    return entries


def run_single(image_path: str):
    """Run pipeline on one image, return result dict or None."""
    image = load_image(image_path)
    if image is None:
        return None

    processed = preprocess(image)
    lm = detect_landmarks(processed)

    if lm is None:
        import cv2
        h, w = image.shape[:2]
        scale = min(1.0, 960 / max(h, w))
        if scale < 1.0:
            resized = cv2.resize(image, (int(w * scale), int(h * scale)))
        else:
            resized = image
        lm = detect_landmarks(resized)

    if lm is None:
        return None

    tilt = detect_camera_tilt(lm)
    measurements = calculate(lm)
    if not tilt["is_frontal"]:
        measurements = compensate_for_tilt(measurements, tilt)
    result = calculate_score(measurements)
    result["camera_angle"] = tilt
    return result


def main():
    metadata = load_metadata()
    if not metadata:
        print("No calibration metadata found.")
        return

    fieldnames = [
        "filename",
        "known_deviation_mm",
        "model_type",
        "data_source",
        "expected_classification",
        "expected_score_min",
        "expected_score_max",
        "actual_score",
        "actual_classification",
        "score_in_range",
        "lateral_deviation",
        "septal_angle",
        "nostril_asymmetry",
        "bridge_straightness",
        "camera_quality",
        "status",
    ]

    results = []
    passed = 0
    failed = 0
    skipped = 0

    for entry in metadata:
        filename = entry["filename"]
        image_path = CALIBRATION_DIR / filename
        data_source = entry.get("data_source", "")

        if not image_path.exists():
            print(f"  SKIP  {filename} (file not found)")
            results.append({
                "filename": filename,
                "known_deviation_mm": entry.get("known_deviation_mm", ""),
                "model_type": entry.get("model_type", ""),
                "data_source": data_source,
                "expected_classification": entry.get("expected_classification", ""),
                "expected_score_min": entry.get("expected_score_min", ""),
                "expected_score_max": entry.get("expected_score_max", ""),
                "status": "skipped",
            })
            skipped += 1
            continue

        print(f"  Analyzing {filename}...", end=" ")
        result = run_single(str(image_path))

        if result is None:
            print("FAIL (no face detected)")
            results.append({
                "filename": filename,
                "known_deviation_mm": entry.get("known_deviation_mm", ""),
                "model_type": entry.get("model_type", ""),
                "data_source": data_source,
                "expected_classification": entry.get("expected_classification", ""),
                "expected_score_min": entry.get("expected_score_min", ""),
                "expected_score_max": entry.get("expected_score_max", ""),
                "status": "no_face",
            })
            failed += 1
            continue

        score = result["deviation_score"]
        cls = result["classification"]
        raw = result.get("raw_metrics", {})
        exp_min = float(entry.get("expected_score_min", 0))
        exp_max = float(entry.get("expected_score_max", 100))
        in_range = exp_min <= score <= exp_max
        quality = result.get("camera_angle", {}).get("quality_score", "")

        status = "PASS" if in_range else "FAIL"
        symbol = "OK" if in_range else "!!"
        print(f"{symbol}  score={score:.1f} ({cls})  expected=[{exp_min:.0f}-{exp_max:.0f}]")

        results.append({
            "filename": filename,
            "known_deviation_mm": entry.get("known_deviation_mm", ""),
            "model_type": entry.get("model_type", ""),
            "data_source": data_source,
            "expected_classification": entry.get("expected_classification", ""),
            "expected_score_min": exp_min,
            "expected_score_max": exp_max,
            "actual_score": round(score, 1),
            "actual_classification": cls,
            "score_in_range": in_range,
            "lateral_deviation": round(raw.get("lateral_deviation", 0), 6),
            "septal_angle": round(raw.get("septal_angle", 0), 2),
            "nostril_asymmetry": round(raw.get("nostril_asymmetry", 0), 4),
            "bridge_straightness": round(raw.get("bridge_straightness", 0), 6),
            "camera_quality": quality,
            "status": status,
        })

        if in_range:
            passed += 1
        else:
            failed += 1

    with open(RESULTS_PATH, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(results)

    print(f"\n{'='*50}")
    print(f"Calibration Results: {passed} passed, {failed} failed, {skipped} skipped")
    print(f"Results saved to: {RESULTS_PATH}")


if __name__ == "__main__":
    main()
