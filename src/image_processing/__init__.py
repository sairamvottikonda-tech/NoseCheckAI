"""
Image Processing Module

Handles smartphone photo capture, standardization, and preprocessing.

Components:
- image_loader: Load and validate images
- preprocessor: Standardize images (resize, normalize lighting)
- quality_checker: Detect blur, check framing
- calibration: Handle distance/scale calibration
"""

__all__ = [
    "image_loader",
    "preprocessor",
    "quality_checker",
    "calibration",
]
