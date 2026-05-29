"""
Measurement Module

Calculates quantitative asymmetry measurements from landmarks.

Key Metrics:
- Lateral deviation: Distance from nose tip to facial midline
- Septal angle: Angle of nasal septum from vertical
- Nostril asymmetry: Left vs. right nostril size/shape differences
- Bridge alignment: Straightness of nasal bridge

Components:
- asymmetry_calculator: Calculate all asymmetry metrics
- geometry_utils: Geometric calculations (distances, angles, areas)
- normalization: Normalize measurements by face size
"""

__all__ = [
    "asymmetry_calculator",
    "geometry_utils",
    "normalization",
]
