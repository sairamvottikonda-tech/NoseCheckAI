# Known Limitations

This document tracks known limitations of the current scoring approach, based on real testing against photos with estimated (non-clinical) severity. Last updated after a debugging session that included real landmark visualization and calibration testing.

## Summary

The app reliably detects faces, processes real phone photos correctly (including portrait orientation, EXIF rotation, and varied lighting), and produces a deviation score and severity classification. However, **the severity scoring has not yet been validated against real clinical measurements**, and testing against 5 photos with rough visual severity estimates suggests it may currently under-detect some real-world deviations.

## What's been verified

- Image processing pipeline (aspect ratio, EXIF orientation, grayscale/RGBA handling) is correct and tested.
- Camera rotation detection no longer gets confounded with actual nasal deviation.
- Bridge-curve measurement now checks multiple points along the bridge, not just two endpoints, so C-curve/S-curve deviations that bend mid-bridge are measurable (previously they were not).
- Severity classification thresholds are consistent across the photo-only and combined visual+symptom scoring paths.

## What's NOT yet verified

- **Scoring sensitivity / scaling factors are unvalidated.** A real test against 5 photos with estimated severity showed poor correlation (R² ≈ 0.10–0.14) between the tool's score and visual severity estimates. Increasing scaling factors uniformly was tested and made category accuracy *worse*, not better — meaning this isn't a simple "turn up the sensitivity" fix.
- **The geometric (landmark-based) measurement approach may not capture all forms of visible nasal asymmetry.** Direct visual inspection of detected landmarks on a photo with an apparently visible deviation showed the bridge-to-tip landmark points sitting close to the computed facial midline — suggesting the visible asymmetry in that photo may be related to nose width/shape/contour rather than centerline position, which this tool does not currently measure.
- No testing has been done against real clinical measurements (CT scans, caliper measurements, or in-person clinical assessment) for any photo in this repository. All "expected" severity values in `data/calibration_models/metadata.csv` are either explicitly-labeled placeholder examples or rough self-reported visual estimates, not clinical ground truth.

## What would resolve this

Real clinical ground truth — ideally from a licensed clinician's in-person assessment of patients (with appropriate consent and without identifiable data leaving the clinical setting) — compared against this tool's output for the same patients. Until that exists, treat all severity classifications from this tool as provisional and unvalidated.
