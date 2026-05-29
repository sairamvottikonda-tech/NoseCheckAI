"""
Data Management Module

Stores, organizes, and retrieves all experimental data.

Data Storage:
- SQLite database for structured data (measurements, scores, metadata)
- CSV exports for analysis in external tools
- JSON for configuration and calibration parameters

Components:
- database: SQLite database operations
- models: Data models (Model, Measurement, Score, etc.)
- export: Export to CSV/JSON for analysis

Database Schema:
- CalibrationModels: model_id, name, known_deviation_type, known_deviation_mm
- Images: image_id, model_id, filepath, capture_date, quality_score
- Landmarks: landmark_id, image_id, landmark_data (JSON)
- Measurements: measurement_id, image_id, lateral_dev, septal_angle, nostril_ratio, etc.
- Scores: score_id, measurement_id, deviation_score, classification, symptom_score
"""

__all__ = [
    "database",
    "models",
    "export",
]
