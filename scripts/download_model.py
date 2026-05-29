#!/usr/bin/env python3
"""Download MediaPipe Face Landmarker model for deployment."""
import os
import sys
import urllib.request
from pathlib import Path

# Project root (parent of scripts/)
ROOT = Path(__file__).resolve().parent.parent
MODEL_DIR = ROOT / "models"
MODEL_PATH = MODEL_DIR / "face_landmarker.task"
URL = "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task"

def main():
    if MODEL_PATH.exists():
        print(f"Model already exists: {MODEL_PATH}")
        return 0
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Downloading model to {MODEL_PATH}...")
    urllib.request.urlretrieve(URL, str(MODEL_PATH))
    print("Done.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
