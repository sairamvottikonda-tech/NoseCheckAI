# CT Scan Validation Guide

## Overview

This guide explains how to validate NoseCheck's photo-based scoring against
CT scan ground truth. The goal is to answer:

> Does NoseCheck's external asymmetry score correlate with internal septal
> deviation as measured on CT scans?

A Pearson correlation > 0.6 and R-squared > 0.4 would demonstrate meaningful
clinical correlation for a screening tool.

## 1. Download CT Scan Datasets

### TCIA Head-Neck Cetuximab (Recommended)

- **URL**: https://www.cancerimagingarchive.net/collection/head-neck-cetuximab/
- **What**: Head/neck CT scans with nasal structures visible
- **Format**: DICOM
- **How to download**:
  1. Install NBIA Data Retriever from https://wiki.cancerimagingarchive.net/x/2QKPBQ
  2. Search for "Head-Neck-Cetuximab" collection
  3. Download 10-20 patients (axial CT series)
  4. Save to a local folder (not in the git repo)

### NasalSeg Dataset

- **URL**: https://github.com/YichiZhang98/NasalSeg
- **Data**: https://zenodo.org/records/10056005
- **What**: 130 annotated nasal CT scans with segmentation masks
- **Citation**: Zhang, Y., et al. (2024). NasalSeg: A Large-scale Nasal Cavity
  CT Dataset. Scientific Data.

### Mendeley Right Nasal Cavity

- **URL**: https://data.mendeley.com/datasets/73dzjb538x/1
- **What**: Pre-extracted 3D meshes of nasal cavities
- **Use**: Reference for nasal passage geometry

## 2. Install 3D Slicer

1. Download from https://www.slicer.org/ (free, open-source)
2. Install on your computer (Windows, Mac, or Linux)
3. Launch 3D Slicer

## 3. Load CT Scans

1. **File > Add Data** or drag DICOM folder into 3D Slicer
2. For DICOM files: use the **DICOM module** (top toolbar)
3. Import the patient folder, then load the CT series
4. Navigate to **Axial View** using the view layout buttons

## 4. Measure Septal Deviation

### Step-by-step Protocol

1. **Find the nasal septum**: Scroll through axial slices until you see
   the nasal cavity. The septum is the thin bone/cartilage dividing left
   and right nasal passages.

2. **Identify landmarks**:
   - **Anterior Nasal Spine (ANS)**: bony point at the bottom-front of
     the nasal opening
   - **Crista Galli**: midline bony projection at the top of the
     ethmoid bone (visible on higher slices)

3. **Draw the midline reference**: Use the **Ruler** tool (Markups module)
   to draw a line from ANS to crista galli. This is the "ideal" straight
   midline.

4. **Measure maximum displacement**: Find the axial slice where the
   septum deviates most from this midline. Use the ruler to measure the
   horizontal distance (in mm) from the midline to the point of maximum
   septal displacement.

5. **Record the measurement**: Note the slice number and deviation in mm.

### Classification

| Deviation (mm) | Severity |
|----------------|----------|
| 0 - 2          | Mild     |
| 2 - 5          | Moderate |
| 5+             | Severe   |

## 5. Render Frontal Face View (Option A - Paired Validation)

To create photos for NoseCheck to analyze:

1. In 3D Slicer, switch to **Volume Rendering** module
2. Set the rendering preset to **CT-Skin** (or CT-Bone for harder tissue)
3. Adjust the 3D view:
   - Rotate the model to a **frontal face view** (as if looking straight
     at the face)
   - Center the nose in the frame
4. **Capture screenshot**: File > Save Screenshot, or use your OS screenshot tool
5. Save as PNG in `data/ct_validation/` directory
6. Name it to match the patient_id (e.g., `P1_frontal.png`)

## 6. Record Data

Edit `data/ct_validation/ct_ground_truth.csv`:

```csv
patient_id,ct_source,max_deviation_mm,deviation_angle_deg,septum_shape,severity_ct,photo_filename,measurement_method,slice_number,notes
P1,TCIA-HN-Cetuximab,3.2,,c_curve,moderate,P1_frontal.png,midline_to_max_displacement,142,Clear C-curve deviation to the left
P2,TCIA-HN-Cetuximab,1.1,,straight,mild,,midline_to_max_displacement,98,Minimal deviation - CT only
```

- Leave `photo_filename` empty for CT-only entries (distribution validation)
- Fill `photo_filename` for entries where you rendered a frontal view (paired validation)

## 7. Run Validation

```bash
# Activate virtual environment
source venv/bin/activate

# Run CT validation
python scripts/validate_ct_correlation.py

# Or with a custom CSV path
python scripts/validate_ct_correlation.py --csv /path/to/custom.csv
```

### Output

The script produces:
- **Terminal summary**: Pearson r, R-squared, RMSE, per-category accuracy
- **Plots**: `data/ct_validation/regression_plot.png`, `score_boxplot.png`,
  `severity_distribution.png`
- **HTML report**: `data/ct_validation/validation_report.html` (self-contained,
  open in any browser)
- **Web route**: Visit `/validation` on the NoseCheck web app to view the report

### Interpreting Results

| Metric | Good | Acceptable | Poor |
|--------|------|------------|------|
| Pearson r | > 0.8 | 0.6 - 0.8 | < 0.6 |
| R-squared | > 0.6 | 0.4 - 0.6 | < 0.4 |
| RMSE | < 10 | 10 - 20 | > 20 |
| Category Accuracy | > 80% | 60 - 80% | < 60% |

## 8. Ethics and Citations

### Ethics Note

All CT datasets used in this validation are de-identified and publicly
available through established research repositories (TCIA, Zenodo,
Mendeley Data). No Institutional Review Board (IRB) approval is
required for secondary analysis of publicly available, de-identified data.

### Required Citations

**TCIA**:
Clark, K., et al. (2013). The Cancer Imaging Archive (TCIA): Maintaining
and Operating a Public Information Repository. Journal of Digital Imaging,
26(6), 1045-1057.

**NasalSeg**:
Zhang, Y., et al. (2024). A Large-scale Nasal Cavity CT Dataset with
Annotations for Nasal Structure Segmentation. Scientific Data.

**Mendeley**:
Right Nasal Cavity Dataset. Mendeley Data, V1.
doi: 10.17632/73dzjb538x.1
