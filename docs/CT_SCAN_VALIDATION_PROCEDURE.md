# CT Scan Validation Procedure

A step-by-step guide for validating NoseCheck against CT scan ground truth.

---

## Overview

This procedure validates whether NoseCheck's photo-based scoring correlates with **internal septal deviation** measured on CT scans. The goal is to answer:

> Does NoseCheck's external asymmetry score correlate with internal septal deviation as measured on CT scans?

**Validation modes:**
- **Paired validation:** CT + frontal photo for same patient → correlation, category accuracy
- **Distribution validation:** CT-only entries (no photo) → severity distribution

**Target metrics:** Pearson r > 0.6, R² > 0.4 for meaningful clinical correlation.

---

## Phase 1: Download CT Scan Datasets

Use public, de-identified datasets:

| Dataset | URL | Content |
|---------|-----|---------|
| **TCIA Head-Neck Cetuximab** | cancerimagingarchive.net/collection/head-neck-cetuximab | Head/neck CT with nasal structures |
| **NasalSeg** | zenodo.org/records/10056005 | 130 annotated nasal CT scans |
| **Mendeley Right Nasal Cavity** | data.mendeley.com/datasets/73dzjb538x/1 | Nasal cavity meshes |

### TCIA Download Steps

1. Install [NBIA Data Retriever](https://wiki.cancerimagingarchive.net/x/2QKPBQ)
2. Search for "Head-Neck-Cetuximab" collection
3. Download 10–20 patients (axial CT series)
4. Save to a local folder (not in the git repo)

---

## Phase 2: Install 3D Slicer

1. Download from [slicer.org](https://www.slicer.org/) (free, open-source)
2. Install on your computer (Windows, Mac, or Linux)
3. Launch 3D Slicer

---

## Phase 3: Load CT Scans

1. **File > Add Data** or drag DICOM folder into 3D Slicer
2. For DICOM files: use the **DICOM module** (top toolbar)
3. Import the patient folder, then load the CT series
4. Navigate to **Axial View** using the view layout buttons

---

## Phase 4: Measure Septal Deviation

### Step-by-Step Protocol

1. **Find the nasal septum:** Scroll through axial slices until you see the nasal cavity. The septum is the thin bone/cartilage dividing left and right nasal passages.

2. **Identify landmarks:**
   - **Anterior Nasal Spine (ANS):** bony point at the bottom-front of the nasal opening
   - **Crista Galli:** midline bony projection at the top of the ethmoid bone (visible on higher slices)

3. **Draw the midline reference:** Use the **Ruler** tool (Markups module) to draw a line from ANS to crista galli. This is the "ideal" straight midline.

4. **Measure maximum displacement:** Find the axial slice where the septum deviates most from this midline. Use the ruler to measure the horizontal distance (in mm) from the midline to the point of maximum septal displacement.

5. **Record the measurement:** Note the slice number and deviation in mm.

### Severity Classification

| Deviation (mm) | Severity |
|----------------|----------|
| 0–2 | Mild |
| 2–5 | Moderate |
| 5+ | Severe |

---

## Phase 5: Render Frontal Face View (Paired Validation)

To create photos for NoseCheck to analyze:

1. In 3D Slicer, switch to **Volume Rendering** module
2. Set the rendering preset to **CT-Skin** (or CT-Bone for harder tissue)
3. Adjust the 3D view:
   - Rotate the model to a **frontal face view** (as if looking straight at the face)
   - Center the nose in the frame
4. **Capture screenshot:** File > Save Screenshot, or use your OS screenshot tool
5. Save as PNG in `data/ct_validation/` directory
6. Name it to match the patient_id (e.g., `P1_frontal.png`)

---

## Phase 6: Edit ct_ground_truth.csv

Edit `data/ct_validation/ct_ground_truth.csv`:

### Column Reference

| Column | Description | Example |
|--------|-------------|---------|
| `patient_id` | Unique patient identifier | `P1`, `P2` |
| `ct_source` | Dataset name | `TCIA-HN-Cetuximab`, `NasalSeg-Zenodo` |
| `max_deviation_mm` | Measured septal deviation in mm | `3.2`, `1.1` |
| `deviation_angle_deg` | Optional angle (degrees) | Leave empty |
| `septum_shape` | `straight`, `c_curve`, `s_curve` | `c_curve` |
| `severity_ct` | `mild`, `moderate`, `severe` | Auto-filled if empty |
| `photo_filename` | PNG filename for paired validation; leave empty for CT-only | `P1_frontal.png` |
| `measurement_method` | How deviation was measured | `midline_to_max_displacement` |
| `slice_number` | Axial slice where max deviation was measured | `142` |
| `notes` | Optional notes | `Clear C-curve deviation to the left` |

### Example ct_ground_truth.csv

```csv
patient_id,ct_source,max_deviation_mm,deviation_angle_deg,septum_shape,severity_ct,photo_filename,measurement_method,slice_number,notes
P1,TCIA-HN-Cetuximab,3.2,,c_curve,moderate,P1_frontal.png,midline_to_max_displacement,142,Clear C-curve deviation to the left
P2,TCIA-HN-Cetuximab,1.1,,straight,mild,,midline_to_max_displacement,98,Minimal deviation - CT only
```

- **Paired validation:** Fill `photo_filename` for entries where you rendered a frontal view
- **Distribution validation:** Leave `photo_filename` empty for CT-only entries

---

## Phase 7: Run Validation

```bash
cd /path/to/nosecheck
source venv/bin/activate
python scripts/validate_ct_correlation.py
```

**Custom CSV path:**
```bash
python scripts/validate_ct_correlation.py --csv /path/to/custom.csv
```

---

## Phase 8: Review Output

### What the Script Produces

| Output | Location | Content |
|--------|----------|---------|
| Terminal summary | Console | Pearson r, R², RMSE, per-category accuracy |
| Regression plot | `data/ct_validation/regression_plot.png` | CT deviation (mm) vs NoseCheck score |
| Box plot | `data/ct_validation/score_boxplot.png` | NoseCheck score by CT severity |
| Distribution chart | `data/ct_validation/severity_distribution.png` | Severity distribution |
| HTML report | `data/ct_validation/validation_report.html` | Self-contained report (open in browser) |
| Web route | `/validation` on NoseCheck app | View report in browser |

### Interpreting Results

| Metric | Good | Acceptable | Poor |
|--------|------|------------|------|
| Pearson r | > 0.8 | 0.6–0.8 | < 0.6 |
| R² | > 0.6 | 0.4–0.6 | < 0.4 |
| RMSE | < 10 | 10–20 | > 20 |
| Category Accuracy | > 80% | 60–80% | < 60% |

---

## Quick Reference

| Step | Action |
|------|--------|
| 1 | Download CT data (TCIA, NasalSeg, etc.) |
| 2 | Install 3D Slicer |
| 3 | Load CT scans, measure septal deviation (mm) |
| 4 | Render frontal view, save PNG in `data/ct_validation/` |
| 5 | Edit `data/ct_validation/ct_ground_truth.csv` |
| 6 | Run `python scripts/validate_ct_correlation.py` |
| 7 | Review terminal output, plots, and HTML report |

---

## Ethics and Citations

### Ethics Note

All CT datasets used in this validation are de-identified and publicly available through established research repositories (TCIA, Zenodo, Mendeley Data). No Institutional Review Board (IRB) approval is required for secondary analysis of publicly available, de-identified data.

### Required Citations

**TCIA:** Clark, K., et al. (2013). The Cancer Imaging Archive (TCIA): Maintaining and Operating a Public Information Repository. Journal of Digital Imaging, 26(6), 1045-1057.

**NasalSeg:** Zhang, Y., et al. (2024). A Large-scale Nasal Cavity CT Dataset with Annotations for Nasal Structure Segmentation. Scientific Data.

**Mendeley:** Right Nasal Cavity Dataset. Mendeley Data, V1. doi: 10.17632/73dzjb538x.1

---

## Related Documentation

- `docs/CT_VALIDATION_GUIDE.md` — Full guide with dataset details and measurement protocol
- `src/analysis/validation.py` — Validation logic
- `scripts/validate_ct_correlation.py` — Validation runner
