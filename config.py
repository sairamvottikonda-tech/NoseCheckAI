"""
Configuration file for NoseCheck

This module contains all configuration parameters for the NoseCheck system.
"""

import os
from pathlib import Path

# Project root directory
ROOT_DIR = Path(__file__).parent

# Data directories
DATA_DIR = ROOT_DIR / "data"
IMAGES_DIR = DATA_DIR / "images"
RESULTS_DIR = DATA_DIR / "results"
CALIBRATION_DIR = DATA_DIR / "calibration_models"

# Create directories if they don't exist
for directory in [DATA_DIR, IMAGES_DIR, RESULTS_DIR, CALIBRATION_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Database configuration
DATABASE_PATH = DATA_DIR / "nosecheck.db"

# Image processing parameters
IMAGE_PROCESSING = {
    "target_width": 640,
    "target_height": 480,
    "normalize_lighting": False,  # CLAHE can hurt face detection in harsh lighting
    "blur_threshold": 100.0,
    "min_face_confidence": 0.5,
}

# Landmark detection parameters
# Lower thresholds (0.5) improve detection under challenging conditions:
# - Harsh/uneven lighting (shadows, overexposure)
# - Non-neutral expressions (smile, etc.)
LANDMARK_DETECTION = {
    "model_selection": 1,
    "min_detection_confidence": 0.5,   # Was 0.9 - too strict for real-world photos
    "min_tracking_confidence": 0.5,    # Was 0.9 - allows faces in difficult lighting
    "static_image_mode": True,
}

# Key nasal landmark indices (MediaPipe Face Mesh)
NASAL_LANDMARKS = {
    "nose_tip": 1,
    "nose_bridge": 168,
    "left_nostril_outer": 129,
    "left_nostril_inner": 203,
    "right_nostril_outer": 358,
    "right_nostril_inner": 423,
    "left_face_edge": 234,
    "right_face_edge": 454,
    # Eye corners: used together with face edges to compute a midline that's
    # robust to head roll/yaw, instead of relying on face-edge midpoint alone
    # (which shifts noticeably whenever the head isn't held dead-level).
    "left_eye_outer": 33,
    "right_eye_outer": 263,
    "left_eye_inner": 133,
    "right_eye_inner": 362,
}

# Measurement parameters
MEASUREMENT = {
    "face_width_landmarks": (234, 454),  # Used for normalization
    "normalize_by_face_width": True,
}

# Scoring parameters - clinically grounded (see docs/SCORING_RATIONALE.md)
# Research: 2-3mm deviation = negligible; ~4mm = perceptible; 32% of normals have some asymmetry
#
# Calibration rationale (face width ~130mm):
#   lateral_deviation: 0.015 (~2mm) = borderline normal → score ~22
#   septal_angle:      2° = normal variation → score ~15
#   nostril_asymmetry: 0.10 ratio = normal → score ~16
#   bridge_straightness: same as lateral
#
# ⚠️ UNRESOLVED CALIBRATION DISCREPANCY (flagged during code review, not yet fixed):
# docs/ALGORITHM_CALIBRATION_LOG.md describes a "v3.0" calibration
# (lateral/bridge scaling=15000, septal_angle scaling=40, lateral noise_floor=0.0005)
# that the log says was empirically validated against real clinical
# before-surgery photos with known deviations (8mm -> 76.0 severe,
# 5mm -> 67.9 severe, 4mm -> 45.6 moderate). The values actually set below
# (scaling=1500, noise_floor=0.003) are ~10x more conservative than that
# and produce much lower scores for the same deviations (8mm -> ~35 mild,
# 4mm -> ~17 normal in isolated testing) -- meaning this build may be
# systematically UNDER-scoring real-world deviation severity right now.
# It's unclear from the repo history whether reverting away from v3.0 was
# intentional (e.g. v3.0 caused false positives on normal faces, which the
# log itself flags as a tradeoff) or accidental. THIS NEEDS TO BE RESOLVED
# WITH REAL TEST DATA before relying on this tool's severity classifications,
# ideally using the ground-truth patient data from the planned clinical
# validation study rather than guessing at scaling factors again.
SCORING = {
    "weights": {
        "lateral_deviation": 0.4,
        "septal_angle": 0.3,
        "nostril_asymmetry": 0.2,
        "bridge_straightness": 0.1,
    },
    "classification_thresholds": {
        "normal": (0, 25),
        "mild": (25, 45),
        "moderate": (45, 65),
        "severe": (65, 100),
    },
    # Clinically-calibrated scaling factors
    # Maps normalised measurements → 0-100 score band
    #   0.02 face-width lateral → 30  (mild)
    #   5° septal angle         → 45  (moderate boundary)
    #   0.20 nostril ratio      → 36  (mild)
    "scaling_factors": {
        "lateral_deviation": 1500,   # 0.02 → 30, 0.04 → 60
        "septal_angle": 10,          # 3° → 25, 5° → 45, 8° → 75
        "nostril_asymmetry": 200,    # 0.15 → 26, 0.30 → 56
        "bridge_straightness": 1500, # same as lateral
    },
    # Noise floor: measurements below these values are treated as zero
    # Prevents sub-pixel jitter and normal micro-asymmetry from inflating scores
    "noise_floor": {
        "lateral_deviation": 0.003,    # 0.3% face width (~0.4mm) - subclinical
        "septal_angle": 0.5,           # 0.5° measurement noise
        "nostril_asymmetry": 0.02,     # 2% ratio - normal variation
        "bridge_straightness": 0.003,  # same as lateral
    },
}

# Questionnaire parameters
QUESTIONNAIRE = {
    "symptoms": [
        "Nasal obstruction (one or both sides)",
        "Mouth breathing (during day/night)",
        "Difficulty breathing through nose",
        "Frequent congestion",
        "Headaches or facial pressure",
        "Reduced sense of smell",
        "Sleep difficulties/snoring",
        "Nosebleeds",
    ],
    "rating_scale": {
        0: "None",
        1: "Mild",
        2: "Moderate",
        3: "Severe",
    },
}

# Visualization parameters
VISUALIZATION = {
    "landmark_color": (0, 255, 0),  # Green in BGR
    "landmark_radius": 2,
    "line_color": (255, 0, 0),  # Blue in BGR
    "line_thickness": 1,
    "font_scale": 0.5,
    "font_color": (255, 255, 255),  # White in BGR
}

# Flask web app configuration
FLASK_CONFIG = {
    "host": "0.0.0.0",
    "port": 5001,  # 5000 often used by macOS AirPlay Receiver
    "debug": True,
    "upload_folder": IMAGES_DIR,
    "allowed_extensions": {"png", "jpg", "jpeg"},
    "max_content_length": 16 * 1024 * 1024,  # 16 MB max upload size
}

# Logging configuration
LOGGING = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": ROOT_DIR / "nosecheck.log",
}
