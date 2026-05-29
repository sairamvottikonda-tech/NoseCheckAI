# 3D Model Calibration Protocol

## Overview

This protocol uses 3D-printed nasal models with **known internal septal deviations** (Straight, C-Curve, S-Curve) to calibrate the NoseCheck algorithm. The goal is to correlate **external measurements** (visible in photos) with **internal deviation severity**.

---

## Model Types (Based on Clinical Classification)

### 1. Straight Septum (Normal - 0mm deviation)
- Internal septum is vertical and centered
- Minimal nasal obstruction
- **Expected external appearance:** Symmetric nose tip, straight bridge
- **Target score:** 0-25 (Normal)

### 2. C-Curve Septum (Mild-Moderate - 2-5mm deviation)
- Internal septum curves to one side
- Moderate nasal obstruction on one side
- **Expected external appearance:** May show subtle tip deviation or nostril asymmetry
- **Target score:** 25-50 (Mild-Moderate)

### 3. S-Curve Septum (Moderate-Severe - 5-10mm deviation)
- Internal septum curves in S-shape
- Severe obstruction, alternating sides
- **Expected external appearance:** Visible tip deviation, bridge curvature, nostril asymmetry
- **Target score:** 50-75+ (Moderate-Severe)

---

## Phase 1: Model Preparation

### Materials Needed:
- 3D printer (FDM recommended - school owned)
- PLA filament (skin-tone or white)
- 3D model files for:
  - Straight septum nose
  - C-curve septum nose (2mm, 5mm deviation variants)
  - S-curve septum nose (8mm, 10mm deviation variants)

### 3D Model Sources:
1. **Design custom models** in Fusion 360/Blender based on the cross-section diagram
2. **Use existing models** from medical libraries (e.g., NIH 3D Print Exchange)
3. **Commission models** with known deviation measurements

### Print Settings:
- Layer height: 0.2mm (balance between quality and speed)
- Infill: 20% (sufficient for photography, lightweight)
- Support: Yes (for nostril overhangs)
- Surface finish: Sand lightly for realistic appearance

---

## Phase 2: Photography Setup

### Equipment:
- **Smartphone camera** (same device for all photos)
- **Tripod or phone stand** (fixed position)
- **Lighting:** 2-3 soft white lights, evenly distributed
- **Background:** Neutral (gray or blue), non-reflective
- **Ruler or scale marker** (for size reference)

### Photo Station Setup:

```
         [Camera/Phone on tripod]
                  ↓
         [50-70cm distance]
                  ↓
    [Light]  [Model]  [Light]
       ↖      on       ↗
         stand/base
```

### Photography Protocol:

#### For Each Model:
1. **Position model** on stable base at eye level with camera
2. **Frontal view** (primary):
   - Camera perpendicular to face
   - Model centered in frame
   - Tip of nose at center
   - Capture 3-5 photos

3. **Distance calibration**:
   - Place ruler next to model in first photo
   - Measure face width in mm for normalization

4. **Consistency checklist**:
   - ✓ Same lighting for all models
   - ✓ Same camera settings (auto or manual - but consistent)
   - ✓ Same distance (50-70cm)
   - ✓ Same background
   - ✓ Focus on nose tip

5. **File naming convention:**
   ```
   straight_0mm_001.jpg
   c_curve_2mm_001.jpg
   c_curve_5mm_001.jpg
   s_curve_8mm_001.jpg
   s_curve_10mm_001.jpg
   ```

---

## Phase 3: Metadata Documentation

Create `data/calibration_models/metadata.csv`:

```csv
filename,known_deviation_mm,model_type,septum_shape,expected_classification
straight_0mm_001.jpg,0,normal,straight,normal
straight_0mm_002.jpg,0,normal,straight,normal
c_curve_2mm_001.jpg,2,mild,c-curve,mild
c_curve_2mm_002.jpg,2,mild,c-curve,mild
c_curve_5mm_001.jpg,5,moderate,c-curve,moderate
c_curve_5mm_002.jpg,5,moderate,c-curve,moderate
s_curve_8mm_001.jpg,8,severe,s-curve,severe
s_curve_8mm_002.jpg,8,severe,s-curve,severe
s_curve_10mm_001.jpg,10,severe,s-curve,severe
s_curve_10mm_002.jpg,10,severe,s-curve,severe
```

**Key fields:**
- `filename`: Photo filename
- `known_deviation_mm`: Maximum internal deviation measured on model
- `model_type`: normal/mild/moderate/severe
- `septum_shape`: straight/c-curve/s-curve
- `expected_classification`: What the algorithm should classify it as

---

## Phase 4: Calibration Workflow

### Step 1: Batch Processing
```bash
cd /Users/lakshmanvemuru/nosecheck
source venv/bin/activate
python scripts/calibration_workflow.py
```

This will:
- Load all calibration images
- Run detection pipeline on each
- Calculate deviation scores
- Compare with known deviations
- Generate calibration report

### Step 2: Analysis

Review output:
```
straight_0mm: known=0mm, score=X, class=Y
c_curve_2mm: known=2mm, score=X, class=Y
...
```

### Step 3: Correlation Analysis

Run validation to compute:
- **r² (correlation)**: How well scores correlate with known deviation
- **RMSE**: Root mean square error between predicted and actual
- **Classification accuracy**: % correctly classified by severity

```bash
python scripts/validate_calibration.py
```

Generates:
- Scatter plot: Known deviation (mm) vs Calculated score
- Correlation metrics
- Classification confusion matrix

### Step 4: Tune Scaling Factors

If correlation is poor (<0.7), adjust in `config.py`:

```python
"scaling_factors": {
    "lateral_deviation": 5000,   # Increase if under-scoring
    "septal_angle": 25,          # Increase if under-scoring
    "nostril_asymmetry": 300,    
    "bridge_straightness": 5000,
}
```

**Tuning strategy:**
- If S-curve (10mm) scores < 65 → Increase all factors by 50%
- If Straight (0mm) scores > 25 → Decrease all factors by 30%
- Iterate until good correlation

---

## Phase 5: Validation Criteria

### Target Metrics:
- **r² ≥ 0.75**: Strong correlation between known and calculated deviation
- **Classification accuracy ≥ 80%**: Correctly bins normal/mild/moderate/severe
- **CV < 15%**: Coefficient of variation for repeated photos of same model

### Expected Results:

| Model Type | Known Deviation | Target Score | Target Class |
|------------|----------------|--------------|--------------|
| Straight | 0mm | 0-25 | Normal |
| C-curve mild | 2mm | 25-40 | Mild |
| C-curve moderate | 5mm | 40-60 | Moderate |
| S-curve severe | 8-10mm | 60-85 | Severe |

---

## Phase 6: Iterate and Refine

### If Results Don't Match Expectations:

1. **Check photography consistency**
   - Re-photograph with better lighting
   - Ensure models are identical position/angle

2. **Verify landmark detection**
   - Run visualization script to see detected landmarks
   - Ensure nose tip, bridge, nostrils detected correctly

3. **Adjust scoring algorithm**
   - If all models score too low → increase scaling factors
   - If all models score too high → decrease scaling factors
   - If some correct, some wrong → adjust individual metric weights

4. **Consider physical model accuracy**
   - Do 3D printed models actually show external deviation?
   - Measure physical model dimensions
   - Compare to cross-section diagram specifications

---

## Troubleshooting

### Problem: All models score "Normal"
**Solution:** 
- Scaling factors too conservative
- Increase lateral_deviation scale from 5000 → 10000
- Increase septal_angle scale from 25 → 40

### Problem: Straight model scores "Severe"
**Solution:**
- Scaling factors too aggressive
- Decrease all factors by 50%
- Check if noise floor is too low (filtering real data)

### Problem: No correlation between known and calculated
**Solution:**
- 3D models may not show external deviation proportional to internal
- Focus on symptom questionnaire as primary screening
- Use models to validate detection quality, not absolute scoring

### Problem: MediaPipe doesn't detect face on 3D models
**Solution:**
- 3D plastic models may not have realistic enough features
- Paint models with facial features (eyes, eyebrows)
- Use photos of real faces with known clinical diagnoses instead
- Or use model photos just to test landmark detection quality

---

## Documentation

After calibration, document:
1. Final scaling factors used
2. Correlation metrics achieved (r², RMSE)
3. Sample images with annotations
4. Known limitations discovered
5. Recommendations for real-world use

Save to: `data/results/calibration_report.pdf`

---

## Next Steps After Successful Calibration

1. **Test on real faces** with known clinical diagnoses
2. **Pilot study** with volunteers
3. **Compare** with ENT clinical assessment
4. **Refine** based on clinical feedback
5. **Deploy** for adolescent screening

---

## Important Notes

⚠️ **Limitation:** External measurements may not correlate strongly with internal septal deviation. The cross-section diagram shows that C-curve and S-curve septums can exist with **identical external appearance**. 

This is why:
- **Symptoms are crucial** for DNS screening
- Algorithm should combine visual + symptom scores
- Don't expect perfect correlation between external measurements and internal deviation
- The tool is a **screening aid**, not a diagnostic device
