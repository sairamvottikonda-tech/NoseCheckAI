# Adaptive Scoring System

## Overview

NoseCheck uses **adaptive weighting** to combine visual deviation scores with symptom scores. The weighting adjusts based on symptom severity to properly reflect clinical significance.

## Why Adaptive Weighting?

External 2D photos may not capture:
- Internal septal deviation
- Turbinate hypertrophy
- Functional airway obstruction

When patients have severe symptoms despite normal/mild external appearance, the **symptoms are clinically more significant** than visual symmetry.

## Weighting Logic

| Symptom Score | Visual Weight | Symptom Weight | Use Case |
|---------------|---------------|----------------|----------|
| 0-40 | 65% | 35% | Few/mild symptoms → trust visual more |
| 40-60 | 55% | 45% | Moderate symptoms → balanced |
| 60-75 | 45% | 55% | Significant symptoms → weight them more |
| **75-100** | **35%** | **65%** | **Severe symptoms → clinical priority** |

## Example Cases

### Case 1: Symmetric Appearance + Severe Symptoms
- Visual score: 15 (normal appearance)
- Symptom score: 80 (severe breathing issues)
- Adaptive weights: 35% visual, 65% symptoms
- **Combined: 0.35×15 + 0.65×80 = 57.3 (MODERATE)**
- Recommendation: ENT evaluation (symptoms indicate pathology)

### Case 2: Mild Asymmetry + Few Symptoms
- Visual score: 40 (mild asymmetry)
- Symptom score: 20 (minimal symptoms)
- Adaptive weights: 65% visual, 35% symptoms
- **Combined: 0.65×40 + 0.35×20 = 33 (MILD)**
- Recommendation: Monitor

### Case 3: Moderate Asymmetry + Severe Symptoms
- Visual score: 40 (mild asymmetry)
- Symptom score: 79 (severe symptoms)
- Adaptive weights: 35% visual, 65% symptoms
- **Combined: 0.35×40 + 0.65×79 = 66.3 (SEVERE)**
- Recommendation: ENT consultation strongly advised

## Clinical Rationale

This approach aligns with medical practice:
- **Symptomatic DNS** (even if externally subtle) → requires treatment
- **Asymptomatic visible deviation** → may not require intervention
- **Both visual + symptoms** → highest clinical priority

The adaptive system ensures that **functional impairment** (symptoms) is properly weighted in the screening decision, not just cosmetic appearance.

## Implementation

See `src/questionnaire/questionnaire.py` → `combine_scores()` function.
