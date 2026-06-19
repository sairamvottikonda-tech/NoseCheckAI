# NoseCheck Scoring Rationale

This document explains how the deviation score is calibrated to align with clinical and perceptual thresholds used in real-world DNS assessment.

> **⚠️ Note on the "Research Basis" below:** these figures (2-3mm negligible, ~4mm perceptible, ~32% normal asymmetry) are commonly cited *approximations* in facial-asymmetry literature, but they are not yet linked to specific peer-reviewed sources in this document. Before presenting this methodology to a clinician or in any research context, replace the vague reference list at the bottom with actual citations (author, year, journal) for each claim, or remove claims that can't be sourced. As written, "systematic review" with no author/year is not a usable citation and would weaken your credibility if questioned.

## Research Basis (needs citations -- see note above)

- **Clinically negligible**: Deviations below 2–3 mm are considered negligible for cosmetic/clinical purposes.
- **Perceptual threshold**: Nasal tip deviation of ~4 mm is when deviation becomes perceptually noticeable.
- **Normal variation**: ~32% of people without nasal deviation still have some facial asymmetry; minor asymmetry is common.

## Scaling Factors

Raw metrics are converted to a 0–100 scale so that **perceptible** deviation maps to roughly 50.

**These are the values actually implemented in `config.py` (`SCORING["scaling_factors"]`)** — previous versions of this document listed different numbers (1250 / 150) that no longer matched the code; this table has been corrected to match:

| Metric | Perceptible threshold | Scale factor (config.py) | Notes |
|--------|------------------------|---------------------------|-------|
| Lateral deviation | ~2% face width (~2mm) maps to ~30 | 1500 | Tip distance from midline |
| Septal angle | ~5° maps to ~45 | 10 | Bridge–tip angle from vertical |
| Nostril asymmetry | ~15% ratio maps to ~26 | 200 | Left vs right width difference |
| Bridge straightness | same scale as lateral deviation | 1500 | Bridge deviation from midline |

## Noise Floor

Small values below the noise floor are treated as zero to reduce impact of landmark jitter. **Values below match `config.py` (`SCORING["noise_floor"]`):**

- Lateral/bridge: 0.3% face width (~0.4mm) — subclinical
- Septal angle: 0.5° — measurement noise
- Nostril asymmetry: 2% ratio — normal variation

## Classification Bands

**These match `config.py` (`SCORING["classification_thresholds"]`):**

- **Normal (0–25)**: Minimal asymmetry, within typical variation.
- **Mild (25–45)**: Slight asymmetry; may warrant monitoring.
- **Moderate (45–65)**: Perceptible deviation; consider ENT evaluation.
- **Severe (65–100)**: Clear deviation; recommend ENT consultation.

These thresholds are used consistently across both the photo-only score
(`src/scoring/score_calculator.py`) and the combined visual+symptom score
shown on the `/result` page — both now read from this single
`classification_thresholds` definition in `config.py`, so a given numeric
score always maps to the same severity label everywhere in the app.

## References

**Currently unsourced — see warning at top of document.** Each of these
needs to be replaced with a real citation before this document is shown to
a clinician or used in any publication/abstract:

- Measurement tools for nasal septal deviation (systematic review) — *author/year/journal needed*
- Discriminative thresholds in facial asymmetry (nasal tip ~4 mm) — *author/year/journal needed*
- 2D photography for nasal anthropometry reliability — *author/year/journal needed*

