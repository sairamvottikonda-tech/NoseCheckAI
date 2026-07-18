"""
ML-based scoring module for NoseCheck.

Replaces the hand-tuned weighted sum with a Random Forest trained on:
- 2 confirmed severe cases (real debug_pipeline measurements, surgical ground truth)
- 1 confirmed normal case (real debug_pipeline measurements, surgical ground truth)
- Synthetic mild/moderate cases (interpolated between confirmed anchors)

IMPORTANT: Mild and moderate predictions should be treated as provisional
until Dr. Markarian's clinical data is used to retrain with real labels.
Severe and Normal predictions have real ground truth support.

To retrain with real data:
    python scripts/retrain_ml_scorer.py --data data/clinical_labels.csv
"""

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler

# ── TRAINING DATA ─────────────────────────────────────────────────────────────
_NORMAL_ANCHOR = [0.0024, 0.888, 0.0049, 0.00069, 0.0172]
_SEVERE_ANCHOR = [0.1526, 11.170, 0.1178, 0.00729, 1.2592]
_SEVERE_ANCHOR2 = [0.0344, 1.793, 0.0029, 0.00126, 0.3140]

def _interpolate(a, b, factor):
    return [a[i] + (b[i]-a[i])*factor for i in range(len(a))]

def _generate(base, label_int, n=150, noise=0.10, seed=42):
    rng = np.random.RandomState(seed)
    rows = []
    for _ in range(n):
        noisy = [max(0, v + rng.normal(0, abs(v)*noise + 1e-6)) for v in base]
        rows.append(noisy + [label_int])
    return rows

def _build_training_data():
    mild_anchor     = _interpolate(_NORMAL_ANCHOR, _SEVERE_ANCHOR, 0.25)
    moderate_anchor = _interpolate(_NORMAL_ANCHOR, _SEVERE_ANCHOR, 0.55)

    rows = (
        _generate(_NORMAL_ANCHOR,  0, n=200, noise=0.12) +  # normal
        _generate(mild_anchor,     1, n=200, noise=0.15) +  # mild
        _generate(moderate_anchor, 2, n=200, noise=0.15) +  # moderate
        _generate(_SEVERE_ANCHOR,  3, n=150, noise=0.12) +  # severe
        _generate(_SEVERE_ANCHOR2, 3, n=150, noise=0.12)    # severe variant
    )
    X = np.array([r[:5] for r in rows])
    y = np.array([r[5]  for r in rows])
    return X, y

# ── MODEL (trained once at import time) ───────────────────────────────────────
_X, _y = _build_training_data()
_scaler = StandardScaler().fit(_X)
_X_scaled = _scaler.transform(_X)
_model = RandomForestClassifier(n_estimators=200, random_state=42,
                                 min_samples_leaf=3)
_model.fit(_X_scaled, _y)

_LABEL_MAP = {0: "normal", 1: "mild", 2: "moderate", 3: "severe"}
_FEATURES   = ["lateral_deviation", "septal_angle", "nostril_asymmetry",
               "bridge_straightness", "nose_width_balance"]

# ── PUBLIC API ─────────────────────────────────────────────────────────────────
def ml_calculate_score(measurements: dict) -> dict:
    """
    Score nasal asymmetry using the trained Random Forest classifier.

    Args:
        measurements: dict from asymmetry_calculator.calculate(), must include
                      lateral_deviation, septal_angle, nostril_asymmetry,
                      bridge_straightness, nose_width_balance.

    Returns:
        dict with keys: deviation_score (0-100), classification, ml_probabilities,
                        method ('ml_random_forest').
    """
    features = [measurements.get(f, 0.0) for f in _FEATURES]
    x = _scaler.transform([features])
    label_int = _model.predict(x)[0]
    probs = _model.predict_proba(x)[0]

    # Map classification back to a 0-100 score for UI compatibility
    score_map = {"normal": 12.5, "mild": 37.5, "moderate": 55.0, "severe": 77.5}
    classification = _LABEL_MAP[label_int]
    deviation_score = score_map[classification]

    return {
        "deviation_score": round(deviation_score, 1),
        "classification": classification,
        "ml_probabilities": {
            "normal":   round(float(probs[0]), 3),
            "mild":     round(float(probs[1]), 3),
            "moderate": round(float(probs[2]), 3),
            "severe":   round(float(probs[3]), 3),
        },
        "method": "ml_random_forest",
    }


if __name__ == "__main__":
    # Quick self-test
    test_cases = [
        ({"lateral_deviation":0.1526,"septal_angle":11.170,"nostril_asymmetry":0.1178,
          "bridge_straightness":0.00729,"nose_width_balance":1.2592}, "severe", "Stadium pre-surgery"),
        ({"lateral_deviation":0.0344,"septal_angle":1.793,"nostril_asymmetry":0.0029,
          "bridge_straightness":0.00126,"nose_width_balance":0.3140}, "severe", "School pre-surgery"),
        ({"lateral_deviation":0.0024,"septal_angle":0.888,"nostril_asymmetry":0.0049,
          "bridge_straightness":0.00069,"nose_width_balance":0.0172}, "normal", "Post-surgery"),
    ]
    print("Self-test:")
    for m, expected, desc in test_cases:
        result = ml_calculate_score(m)
        ok = "✓" if result["classification"] == expected else "✗"
        print(f"  {ok} {desc}: {result['classification']} ({result['deviation_score']}) "
              f"[expected {expected}]")
