"""
Symptom Questionnaire Module

Collects self-reported symptoms to complement visual analysis.

Symptom Checklist:
1. Nasal obstruction (one or both sides)
2. Mouth breathing (during day/night)
3. Difficulty breathing through nose
4. Frequent congestion
5. Headaches or facial pressure
6. Reduced sense of smell
7. Sleep difficulties/snoring
8. Nosebleeds

Scoring: Each symptom rated 0-3 (none, mild, moderate, severe)

Components:
- questionnaire: Symptom questions and scoring
- symptom_analyzer: Calculate symptom severity score
- combined_scorer: Combine visual + symptom scores
"""

__all__ = [
    "questionnaire",
    "symptom_analyzer",
    "combined_scorer",
]
