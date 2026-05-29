"""
Symptom questionnaire module for NoseCheck.

Loads questions from config, accepts responses, and computes symptom sub-score.
"""

import sys
from pathlib import Path

_project_root = Path(__file__).resolve().parent.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

try:
    import config
    QUESTIONNAIRE_CONFIG = config.QUESTIONNAIRE
except ImportError:
    QUESTIONNAIRE_CONFIG = {
        "symptoms": [
            "Nasal obstruction (one or both sides)",
            "Mouth breathing (during day/night)",
            "Difficulty breathing through nose",
            "Frequent congestion",
            "Headaches or facial pressure",
            "Reduced sense of smell",
            "Sleep difficulties/snoring",
            "Nosebleeds",
        ],
        "rating_scale": {0: "None", 1: "Mild", 2: "Moderate", 3: "Severe"},
    }


def get_questions():
    """
    Get symptom questions and rating scale from config.

    Returns:
        List of dicts with keys: id, text, scale.
    """
    symptoms = QUESTIONNAIRE_CONFIG["symptoms"]
    scale = QUESTIONNAIRE_CONFIG["rating_scale"]
    return [
        {"id": i, "text": s, "scale": scale}
        for i, s in enumerate(symptoms)
    ]


def compute_symptom_score(responses):
    """
    Compute symptom sub-score (0-100) from responses.

    Args:
        responses: List of integers 0-3 for each symptom (None/mild/moderate/severe).

    Returns:
        Symptom score 0-100. Higher = more symptoms.
    """
    if not responses:
        return 0.0
    # Normalize: max sum = 3 * num_symptoms, so score = (sum / (3 * n)) * 100
    n = len(responses)
    max_sum = 3 * n
    total = sum(min(3, max(0, int(r))) for r in responses[:n])
    return 100 * total / max_sum if max_sum > 0 else 0.0


def combine_scores(visual_score: float, symptom_score: float, visual_weight: float = None) -> float:
    """
    Combine visual deviation score and symptom score with adaptive weighting.
    
    When symptoms are severe (>60), they get more weight since internal deviation
    may not be visible externally but causes significant clinical issues.

    Args:
        visual_score: Deviation score 0-100 from image analysis.
        symptom_score: Symptom score 0-100 from questionnaire.
        visual_weight: Weight for visual (0-1). If None, adapts based on symptom severity.

    Returns:
        Combined score 0-100.
    """
    # Adaptive weighting based on symptom severity
    if visual_weight is None:
        if symptom_score >= 75:  # Severe symptoms - weight them heavily
            visual_weight = 0.35  # 35% visual, 65% symptoms
        elif symptom_score >= 60:  # Moderate-severe symptoms
            visual_weight = 0.45  # 45% visual, 55% symptoms
        elif symptom_score >= 40:  # Moderate symptoms
            visual_weight = 0.55  # 55% visual, 45% symptoms
        else:  # Mild or no symptoms
            visual_weight = 0.65  # 65% visual, 35% symptoms
    
    symptom_weight = 1.0 - visual_weight
    combined = visual_weight * visual_score + symptom_weight * symptom_score
    
    # When both visual and symptoms are elevated, boost slightly (clinical correlation)
    if visual_score > 35 and symptom_score > 60:
        boost = min(5, (visual_score - 35) * 0.1)  # Small boost for correlation
        combined = min(100, combined + boost)
    
    return combined
