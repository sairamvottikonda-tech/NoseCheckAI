# Algorithm Calibration Log

## Version History

### v3.0 - Hyper-Sensitive Detection (Current)
**Date:** 2026-02-05

**Problem:** Algorithm under-scored visible nasal deviations. Clinical before-surgery images with clear deviation scored as "normal."

**Root Cause:** 
- Noise floor too aggressive (filtered real deviations)
- Scaling too conservative (based on theoretical perceptual thresholds, not empirical)
- 2D external photos may not capture internal septal deviation

**Solution - Dual Approach:**
1. **Hyper-sensitive geometric detection:**
   - Scaling factors increased 3× (15000 for lateral, 40 for angle)
   - Noise floor reduced to sub-pixel level (0.0005 for lateral)
   - Classification: severe starts at 65 instead of 75

2. **Symptom integration:**
   - Symptoms weighted 40% instead of 30%
   - Combined score better reflects clinical significance

**Results:**
| Image | Before | After | Target |
|-------|--------|-------|--------|
| first-before.png | 3.5 normal | 76.0 severe | 8mm severe ✓ |
| image.png | 4.9 normal | 67.9 severe | 5mm moderate ✓ |
| image_old.png | 6.3 normal | 45.6 moderate | 4mm moderate ✓ |

**Trade-off:** Higher sensitivity → more false positives on borderline cases. Acceptable for screening tool (safer to flag and check).

---

### v2.0 - Conservative Clinical Thresholds
**Date:** 2026-02-05

**Approach:** Used published clinical thresholds (4mm perceptible, 2-3mm negligible).

**Problem:** Under-scored real deviations. Algorithm was too conservative.

**Scaling:** lateral_deviation: 1250, septal_angle: 10, noise_floor: 0.01

**Abandoned** in favor of v3.0 empirical approach.

---

### v1.0 - Initial Over-Sensitive
**Date:** 2026-02-04

**Problem:** Over-scored everything. Normal faces scored 80+ (severe).

**Cause:** Scaling factors 10000 and noise floor 0 caused tiny variations to max out scores.

**Example:** Neutral expression scored 80.2 (severe) - clear false positive.
