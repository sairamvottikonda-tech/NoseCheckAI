# 3D Model Calibration Procedure

A step-by-step guide for calibrating NoseCheck using 3D-printed nasal models with known septal deviations.

---

## Overview

This procedure uses 3D-printed nasal models with **known internal septal deviations** to validate and tune the NoseCheck algorithm. By comparing NoseCheck's output against known ground truth, you can measure accuracy and adjust scaling factors.

**What you need:**
- 3D-printed nasal models (Straight, C-curve, S-curve)
- Smartphone or camera
- Photos of each model
- This repository with calibration scripts

---

## Phase 1: Model Preparation

### Model Types

| Septum Type | Deviation (mm) | Target Score | Target Class |
|-------------|----------------|--------------|--------------|
| Straight | 0 | 0–25 | Normal |
| C-curve (mild) | 2–4 | 25–50 | Mild |
| C-curve (moderate) | 4–6 | 40–65 | Moderate |
| S-curve (severe) | 6–10 | 55–85 | Severe |

### Print Settings (FDM)

- Layer height: 0.2 mm
- Infill: 20%
- Supports: Yes (for nostril overhangs)
- Surface: Sand lightly for realistic appearance

---

## Phase 2: Photography

### Setup

- **Camera:** Smartphone on tripod, 50–70 cm from model
- **Lighting:** 2–3 soft white lights, evenly distributed
- **Background:** Neutral (gray or blue), non-reflective
- **Consistency:** Same distance, lighting, and camera settings for all models

### For Each Model

1. Position model at eye level, centered in frame
2. Camera perpendicular to face (frontal view)
3. Capture 3–5 photos
4. Use consistent naming, e.g.:
   - `straight_0mm_001.jpg`
   - `c_curve_2mm_001.jpg`
   - `s_curve_8mm_001.jpg`

---

## Phase 3: Edit metadata.csv

Place all photos in `data/calibration_models/` and add **one row per photo** to `data/calibration_models/metadata.csv`.

### Column Reference

| Column | Description | Example |
|--------|-------------|---------|
| `filename` | Exact photo filename | `straight_0mm_001.jpg` |
| `known_deviation_mm` | Known septal deviation in mm | `0`, `2`, `5`, `8` |
| `model_type` | `3d_model` or `clinical` | `3d_model` |
| `septum_shape` | `straight`, `c_curve`, `s_curve` | `straight` |
| `expected_classification` | Expected severity | `normal`, `mild`, `moderate`, `severe` |
| `expected_score_min` | Minimum acceptable NoseCheck score | `0` |
| `expected_score_max` | Maximum acceptable NoseCheck score | `25` |
| `data_source` | Optional (e.g. `ct_val`) | Leave empty for 3D models |
| `notes` | Optional description | `3D printed straight septum` |

### Example metadata.csv

```csv
filename,known_deviation_mm,model_type,septum_shape,expected_classification,expected_score_min,expected_score_max,data_source,notes
straight_0mm_001.jpg,0,3d_model,straight,normal,0,25,,Straight septum
c_curve_2mm_001.jpg,2,3d_model,c_curve,mild,25,45,,C-curve mild
c_curve_5mm_001.jpg,5,3d_model,c_curve,moderate,40,65,,C-curve moderate
s_curve_8mm_001.jpg,8,3d_model,s_curve,severe,55,85,,S-curve severe
```

**Important:** The `filename` in each row must exactly match the file in `data/calibration_models/`.

---

## Phase 4: Run Calibration Workflow

### Step 1: Run the calibration script

```bash
cd /path/to/nosecheck
source venv/bin/activate
python scripts/calibration_workflow.py
```

### What it does

- Loads each photo listed in `metadata.csv`
- Runs NoseCheck (landmark detection → measurements → score)
- Compares actual score to expected range (PASS/FAIL)
- Writes results to `data/calibration_models/calibration_results.csv`

### Example output

```
  Analyzing straight_0mm_001.jpg... OK  score=12.3 (normal)  expected=[0-25]
  Analyzing c_curve_2mm_001.jpg... !!  score=18.5 (normal)  expected=[25-45]
  ...

Calibration Results: 3 passed, 1 failed, 0 skipped
Results saved to: data/calibration_models/calibration_results.csv
```

---

## Phase 5: Run Validation (Accuracy Metrics)

```bash
python scripts/validate_calibration.py
```

### Metrics reported

| Metric | Description |
|-------|-------------|
| **R²** | Correlation between known deviation (mm) and NoseCheck score |
| **Score range accuracy** | % of photos whose score falls within expected range |
| **Category accuracy** | % of photos correctly classified (normal/mild/moderate/severe) |
| **Per-category accuracy** | Correct/total for each severity class |

### Target metrics

- **R² ≥ 0.75** — Strong correlation
- **Category accuracy ≥ 80%** — Reliable classification
- **Score range accuracy** — As high as possible

---

## Phase 6: Tune If Needed

If R² < 0.75 or accuracy is low, adjust scaling factors in `config.py`:

```python
"scaling_factors": {
    "lateral_deviation": 5000,   # Increase if under-scoring
    "septal_angle": 25,
    "nostril_asymmetry": 300,
    "bridge_straightness": 5000,
}
```

### Tuning guide

| Problem | Action |
|---------|--------|
| All models score too low (e.g. severe < 65) | Increase all factors by 50% |
| All models score too high (e.g. straight > 25) | Decrease all factors by 30% |
| Some correct, some wrong | Adjust individual metric weights |

Re-run `calibration_workflow.py` and `validate_calibration.py` after each change.

---

## Quick Reference

| Step | Action |
|------|--------|
| 1 | Place photos in `data/calibration_models/` |
| 2 | Edit `data/calibration_models/metadata.csv` (one row per photo) |
| 3 | Run `python scripts/calibration_workflow.py` |
| 4 | Run `python scripts/validate_calibration.py` |
| 5 | If needed, tune `config.py` and repeat steps 3–4 |

---

## Troubleshooting

### MediaPipe doesn't detect face on 3D models

3D plastic models may lack realistic facial features. Options:
- Paint eyes/eyebrows on the model
- Use photos of real faces with known clinical diagnoses instead

### All models score "Normal"

- Scaling factors too conservative
- Increase `lateral_deviation` and `septal_angle` in `config.py`

### Straight model scores "Severe"

- Scaling factors too aggressive
- Decrease all factors by ~50%

### No correlation between known and calculated

- External appearance may not reflect internal deviation
- Use symptom questionnaire as primary screening
- Use models to validate detection quality, not absolute scoring

---

## Important Note

External 2D measurements may not correlate strongly with internal septal deviation. C-curve and S-curve septums can have identical external appearance. NoseCheck is a **screening aid**, not a diagnostic device. Symptoms are crucial for DNS screening.

---

## Related Documentation

- `docs/3D_MODEL_CALIBRATION_PROTOCOL.md` — Full protocol with model design, print settings, and validation criteria
- `docs/3D_PRINTING_GUIDE.md` — 3D printing details
- `config.py` — Scaling factors and scoring configuration
