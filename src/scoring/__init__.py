"""
Deviation Scoring Module

Generates a single normalized deviation score combining multiple measurements.

Approach:
- Weighted combination of asymmetry metrics
- Calibration using known 3D model deviations (none, mild, moderate, severe)
- Score normalization (0-100 scale)
- Classification (normal, mild, moderate, severe)

Components:
- score_calculator: Calculate final deviation score
- calibration_manager: Store and use calibration data from 3D models
- classifier: Classify severity based on score
"""

__all__ = [
    "score_calculator",
    "calibration_manager",
    "classifier",
]
