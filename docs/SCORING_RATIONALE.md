# NoseCheck Scoring Rationale

This document explains how the deviation score is calibrated to align with clinical and perceptual thresholds used in real-world DNS assessment.

## Research Basis

- **Clinically negligible**: Deviations below 2–3 mm are considered negligible for cosmetic/clinical purposes.
- **Perceptual threshold**: Nasal tip deviation of ~4 mm is when deviation becomes perceptually noticeable.
- **Normal variation**: ~32% of people without nasal deviation still have some facial asymmetry; minor asymmetry is common.

## Scaling Factors

Raw metrics are converted to a 0–100 scale so that **perceptible** deviation maps to roughly 50:

| Metric | Perceptible threshold | Scale factor | Notes |
|--------|------------------------|--------------|-------|
| Lateral deviation | ~4% face width (~4 mm) | 1250 | Tip distance from midline |
| Septal angle | ~5° | 10 | Bridge–tip angle from vertical |
| Nostril asymmetry | ~33% ratio | 150 | Left vs right width difference |
| Bridge straightness | ~4% face width | 1250 | Bridge deviation from midline |

## Noise Floor

Small values below the noise floor are treated as zero to reduce impact of landmark jitter:

- Lateral/bridge: 1% face width
- Septal angle: 1°
- Nostril asymmetry: 5% ratio

## Classification Bands

- **Normal (0–30)**: Minimal asymmetry, within typical variation.
- **Mild (30–50)**: Slight asymmetry; may warrant monitoring.
- **Moderate (50–70)**: Perceptible deviation; consider ENT evaluation.
- **Severe (70–100)**: Clear deviation; recommend ENT consultation.

## References

- Measurement tools for nasal septal deviation (systematic review)
- Discriminative thresholds in facial asymmetry (nasal tip ~4 mm)
- 2D photography for nasal anthropometry reliability
