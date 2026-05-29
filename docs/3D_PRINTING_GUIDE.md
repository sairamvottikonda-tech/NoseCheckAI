# 3D Printing Guide for NoseCheck Calibration Models

## Overview

Create physical nasal models with known internal septal deviations (Straight, C-Curve, S-Curve) for calibrating the NoseCheck algorithm.

---

## Model Specifications

Based on the removable septum cross-section diagram, you need to create:

### Model Set 1: Straight Septum (Normal)
- **Internal deviation:** 0mm
- **Septum shape:** Vertical, centered
- **External appearance:** Symmetric nose
- **Quantity:** 1 model
- **Purpose:** Baseline for "normal" classification

### Model Set 2: C-Curve Septum (Mild to Moderate)
- **C-Curve 2mm deviation:**
  - Internal septum curves to one side
  - Deviation at midpoint: ~2mm from center
  - External: Subtle asymmetry
  - Target classification: **Mild**

- **C-Curve 5mm deviation:**
  - More pronounced curve
  - Deviation at midpoint: ~5mm
  - External: Visible asymmetry
  - Target classification: **Moderate**

### Model Set 3: S-Curve Septum (Moderate to Severe)
- **S-Curve 8mm deviation:**
  - Septum curves in S-shape
  - Maximum deviation: ~8mm
  - External: Clear asymmetry
  - Target classification: **Moderate-Severe**

- **S-Curve 10mm deviation:**
  - Severe S-curve
  - Maximum deviation: 10mm
  - External: Obvious deviation
  - Target classification: **Severe**

**Total models needed:** 5 minimum (1 straight + 2 C-curve + 2 S-curve)

---

## 3D Model Design Options

### Option A: Design from Scratch (CAD)

**Software:** Fusion 360, Blender, TinkerCAD

**Design approach:**
1. Start with **base nose shell** (outer appearance - identical for all)
2. Model **internal cavity** with nasal septum
3. Create **variants** with different septum curves:
   - Straight: centerline vertical
   - C-curve 2mm: offset 2mm at midpoint
   - C-curve 5mm: offset 5mm at midpoint
   - S-curve 8-10mm: S-shaped curve with max deviation

**Key features:**
- Realistic nose proportions (~30-40mm wide, 40-50mm tall)
- Removable or visible septum for verification
- Flat base for stable placement
- Measurement markers on base

### Option B: Modify Existing Models

**Sources:**
- **NIH 3D Print Exchange:** Medical anatomy models
- **Thingiverse:** Search "nasal anatomy" or "nose model"
- **GrabCAD:** Engineering/medical models
- **MorphoSource:** Academic anatomical models

**Modification:**
- Import base nose model
- Add/modify internal septum with controlled deviations
- Export variants (straight, C-curve, S-curve)

### Option C: Commission Models

**Contact:**
- Medical model companies
- University medical illustration departments
- 3D modeling freelancers (Fiverr, Upwork)

**Specifications to provide:**
- Cross-section diagram (your reference image)
- Deviation measurements (0mm, 2mm, 5mm, 8mm, 10mm)
- Size requirements (~life-size, 30-40mm width)
- File format: STL

---

## 3D Printing Settings

### Printer Type:
- **FDM** (Fused Deposition Modeling) - school printer
- PLA or PETG filament

### Print Settings:
```
Material: PLA (easier) or PETG (more durable)
Color: White, skin-tone, or gray (avoid translucent)
Layer height: 0.15-0.2mm (balance quality/speed)
Infill: 15-20% (sufficient for photos)
Print speed: 40-60 mm/s (slower = better surface)
Supports: Yes (for nostril undercuts)
Build plate adhesion: Brim or raft
Nozzle temp: 200-220°C (PLA) / 230-250°C (PETG)
Bed temp: 60°C (PLA) / 80°C (PETG)
```

### Orientation on Build Plate:
- Print nose **facing UP** (nostrils down)
- Requires support for nostril cavities
- Or print **on side** (reduces supports but may need more post-processing)

### Post-Processing:
1. **Remove supports** carefully (especially nostrils)
2. **Light sanding** (200-400 grit) for smoother surface
3. Optional: **Paint** with skin-tone acrylic (makes it look more realistic for MediaPipe)
4. Optional: **Add facial features** (simple painted eyes, eyebrows) if MediaPipe struggles with bare nose

---

## Verification After Printing

### Physical Measurements:
For each model, measure and document:
- **Nose width** at widest point (mm)
- **Nose height** from bridge to tip (mm)
- **Septum deviation** at max point (use calipers if accessible)
- Compare with CAD design specifications

### Visual Inspection:
- Check **surface quality** (smooth, no major layer lines)
- Verify **symmetry** of outer shell (should be identical for all)
- Confirm **septum position** (if visible/removable)
- Take **reference photos** from multiple angles for documentation

### Documentation:
Create a record for each model:
```
Model ID: C-Curve-2mm-v1
Print date: 2026-02-XX
Internal septum deviation: 2mm (measured)
External dimensions: 38mm W × 45mm H
Surface finish: Sanded, unpainted
Notes: Nostrils clear, surface smooth
```

---

## Photography Protocol for Models

### Setup Requirements:
- **Tripod or phone stand** (must be fixed for all shots)
- **2-3 LED lights** (daylight white, ~5000K)
- **Neutral background** (gray cardboard or blue poster board)
- **Ruler/scale** (for first calibration photo)
- **Level surface** for model placement

### Lighting Setup:
```
    [Light]            [Light]
       \                 /
        \               /
         \             /
          \           /
       [Phone on Tripod]
              |
              | 50-70cm
              |
              ↓
          [Model]
          on stand
```

**Key points:**
- Lights at **45° angles** from front
- Equal brightness (use same bulbs)
- No harsh shadows on nose
- Avoid reflections on plastic

### Camera Settings:
Mark the tripod position and use **consistent** settings:
- **Distance:** 60cm (measure and mark)
- **Height:** Model at camera center (use level)
- **Focus:** Manual focus on nose tip (if available)
- **Exposure:** Auto or manual (but consistent across all models)
- **No flash:** Use continuous lights only

### Per-Model Protocol:
1. **Place model** on marked position
2. **Check framing:** Nose fills 50-70% of frame
3. **Verify angle:** Camera perpendicular (use angle app or level)
4. **Take 5 photos:**
   - 3 with model perfectly centered
   - 2 with slight variations (±5° rotation) for robustness testing
5. **Review immediately:** Sharp focus, no motion blur, even lighting
6. **Label photos:** `straight_0mm_001.jpg`, `straight_0mm_002.jpg`, etc.

### Quality Checklist:
- [ ] Focus sharp on nose area
- [ ] No motion blur
- [ ] Even lighting (no harsh shadows)
- [ ] No glare or reflections
- [ ] Model perpendicular to camera
- [ ] Consistent framing across all models
- [ ] File size > 200KB (sufficient resolution)

---

## Organizing Your Calibration Dataset

### Folder Structure:
```
data/calibration_models/
├── metadata.csv
├── straight_septum/
│   ├── straight_0mm_001.jpg
│   ├── straight_0mm_002.jpg
│   └── straight_0mm_003.jpg
├── c_curve/
│   ├── c_curve_2mm_001.jpg
│   ├── c_curve_2mm_002.jpg
│   ├── c_curve_5mm_001.jpg
│   └── c_curve_5mm_002.jpg
└── s_curve/
    ├── s_curve_8mm_001.jpg
    ├── s_curve_8mm_002.jpg
    ├── s_curve_10mm_001.jpg
    └── s_curve_10mm_002.jpg
```

Or simpler (flat structure):
```
data/calibration_models/
├── metadata.csv
├── straight_0mm_001.jpg
├── straight_0mm_002.jpg
├── c_curve_2mm_001.jpg
└── ... (all photos at top level)
```

### metadata.csv Format:
```csv
filename,known_deviation_mm,model_type,septum_shape,expected_classification,print_date,notes
straight_0mm_001.jpg,0,normal,straight,normal,2026-02-10,PLA white sanded
straight_0mm_002.jpg,0,normal,straight,normal,2026-02-10,Same model
c_curve_2mm_001.jpg,2,mild,c-curve,mild,2026-02-11,PLA measured 2.1mm
c_curve_5mm_001.jpg,5,moderate,c-curve,moderate,2026-02-11,PLA measured 4.8mm
s_curve_8mm_001.jpg,8,severe,s-curve,severe,2026-02-12,PLA measured 8.2mm
s_curve_10mm_001.jpg,10,severe,s-curve,severe,2026-02-12,PLA measured 10.3mm
```

---

## Running Calibration

### Step 1: Initial Run
```bash
cd /Users/lakshmanvemuru/nosecheck
source venv/bin/activate
python scripts/calibration_workflow.py
```

**Expected output:**
```
straight_0mm: known=0mm, score=5-15, class=normal
c_curve_2mm: known=2mm, score=25-40, class=mild
c_curve_5mm: known=5mm, score=40-60, class=moderate
s_curve_8mm: known=8mm, score=60-75, class=severe
s_curve_10mm: known=10mm, score=75-90, class=severe
```

### Step 2: Correlation Check
```bash
python scripts/validate_calibration.py
```

**Target metrics:**
- r² ≥ 0.70 (strong correlation)
- RMSE < 15 (low error)
- All models classified correctly

### Step 3: Adjust if Needed

**If straight model scores > 25:**
→ Algorithm too sensitive, decrease scaling factors

**If S-curve model scores < 60:**
→ Algorithm too conservative, increase scaling factors

**If no correlation (random scores):**
→ External appearance may not match internal deviation
→ Focus on symptom-based screening instead

---

## Expected Results vs Reality

### Best Case: Strong Correlation
```
Known 0mm  → Score 10  (normal)   ✓
Known 2mm  → Score 30  (mild)     ✓
Known 5mm  → Score 50  (moderate) ✓
Known 8mm  → Score 70  (severe)   ✓
Known 10mm → Score 85  (severe)   ✓

r² = 0.85 (excellent correlation)
```

### Realistic Case: Moderate Correlation
```
Known 0mm  → Score 15  (normal)   ✓
Known 2mm  → Score 25  (mild)     ✓
Known 5mm  → Score 40  (moderate) ≈
Known 8mm  → Score 55  (moderate) ≈
Known 10mm → Score 65  (severe)   ✓

r² = 0.65 (moderate correlation)
```

**Interpretation:** External measurements capture some but not all internal deviation. Symptoms essential.

### Worst Case: No Correlation
```
All models score 20-40 (mostly normal/mild)

r² = 0.15 (no correlation)
```

**Interpretation:** External appearance doesn't correlate with internal septum position. The diagram's note "**Outer nose shell identical for all**" is literally true - external photos can't distinguish internal deviation.

**Solution:** Rely on **symptom-based screening** (already implemented with 40-65% symptom weighting).

---

## 3D Model Resources

### Free STL Files:
- Search "nasal anatomy" on Thingiverse
- NIH 3D Print Exchange (medical models)
- Search "deviated septum model" on GrabCAD

### Paid Options:
- TurboSquid (3D models marketplace)
- CGTrader (medical 3D models)
- Commission custom models (~$50-150 for set)

### School Resources:
- Check if medical/biology department has anatomical models
- Ask biomedical engineering department
- Contact medical illustration program

---

## Alternative: Use Clinical Photos

If 3D printing is delayed or models don't show external deviation:

**Option:** Use **clinical before/after photos** from published research:
- Download from medical journals (with attribution)
- Use photos from rhinoplasty studies
- Contact local ENT for anonymized clinical images

**Advantage:** Real faces with diagnosed deviation
**Disadvantage:** May not have precise mm measurements

---

## Timeline Integration

From your original 3-week plan:

### Week 1 (Days 1-7):
- Days 1-2: Finalize CAD designs
- Days 3-5: 3D print models (printer runs overnight)
- Days 6-7: Post-process, photography

### Week 2 (Days 8-14):
- Day 8: Run calibration_workflow.py
- Days 9-10: Adjust scaling factors
- Days 11-12: Validate and test
- Days 13-14: Refine algorithm

### Week 3 (Days 15-21):
- Test on volunteer photos
- Document results
- Prepare research presentation

---

## Troubleshooting

### Problem: Models don't look realistic enough for MediaPipe
**Solution:**
- Paint eyes and eyebrows on the face area
- Add texture (light sanding, primer coat)
- Use photos of models held by a person (partial face visible)

### Problem: External appearance identical for all models
**Expected!** The diagram shows this. Solutions:
- Document that external photos alone insufficient
- Emphasize symptom questionnaire importance
- Use models to validate landmark detection quality only

### Problem: Print quality poor (layer lines visible)
**Solutions:**
- Reduce layer height to 0.1mm (slower but smoother)
- Sand with progressively finer grits (200→400→800)
- Apply primer/filler and sand smooth
- Use resin printer for higher quality (if available)

---

## Success Criteria

Your calibration is successful if:

✅ **Repeatability:** Same model photographed 5× gives similar scores (CV < 15%)
✅ **Monotonic relationship:** Higher deviation → higher score (even if not perfectly linear)
✅ **Classification accuracy:** Models sorted correctly by severity (normal < mild < moderate < severe)
✅ **Angle detection:** Algorithm warns when photos are tilted > 20°
✅ **Documentation:** Results documented with photos, metrics, and analysis

Even with **moderate correlation (r² = 0.5-0.7)**, the system is useful if combined with symptom assessment!
