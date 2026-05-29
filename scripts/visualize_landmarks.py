#!/usr/bin/env python3
"""
Visualize detected landmarks on an image.

Usage:
    python scripts/visualize_landmarks.py <image_path> [output_path]
    python scripts/visualize_landmarks.py data/calibration_models/image.png
"""

import sys
from pathlib import Path

_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_root))

from src.image_processing.image_loader import load_image
from src.landmark_detection.detector import detect_landmarks
from src.analysis.visualizations import visualize_landmarks


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/visualize_landmarks.py <image_path> [output_path]")
        sys.exit(1)

    image_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2]) if len(sys.argv) > 2 else image_path.parent / f"{image_path.stem}_landmarks{image_path.suffix}"

    img = load_image(image_path)
    if img is None:
        print(f"Failed to load {image_path}")
        sys.exit(1)

    landmarks = detect_landmarks(img)
    if landmarks is None:
        print("No face/landmarks detected")
        sys.exit(1)

    visualize_landmarks(img, landmarks, output_path)
    print(f"Saved: {output_path}")


if __name__ == "__main__":
    main()
