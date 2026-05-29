# CT Validation Ground Truth Data

## ct_ground_truth.csv Schema

| Column | Type | Required | Description |
|--------|------|----------|-------------|
| patient_id | string | Yes | Unique ID (e.g., P1, P2) |
| ct_source | string | Yes | Dataset origin (TCIA-HN-Cetuximab, NasalSeg-Zenodo, Mendeley) |
| max_deviation_mm | float | Yes | Maximum septal displacement from midline in mm |
| deviation_angle_deg | float | No | Angle between septum and vertical midline |
| septum_shape | string | No | straight, c_curve, s_curve |
| severity_ct | string | Yes | Clinical severity: mild (0-2mm), moderate (2-5mm), severe (5+mm) |
| photo_filename | string | No | Frontal photo/rendering in this directory (empty = CT-only entry) |
| measurement_method | string | Yes | How deviation was measured (midline_to_max_displacement) |
| slice_number | int | No | Axial slice number where max deviation was found |
| notes | string | No | Free text notes |

## Severity Classification

- **Mild**: 0-2 mm deviation
- **Moderate**: 2-5 mm deviation
- **Severe**: 5+ mm deviation

## Photo Pairing (Option A: 3D Slicer Rendering)

For paired validation, render a frontal face view from the CT scan:

1. In 3D Slicer, use Volume Rendering module
2. Set preset to "CT-Skin" or similar soft-tissue rendering
3. Rotate to frontal view (looking at the face straight on)
4. Screenshot/export as PNG
5. Save in this directory, set `photo_filename` in CSV
6. Run: `python scripts/validate_ct_correlation.py`
