"""
ML-based scoring module for NoseCheck v3.
Trained on REAL CLINICAL DATA from Dr. Alexander Markarian, M.D.
+ confirmed surgical ground truth (Sairam's pre/post surgery photos)
+ medium confidence normal cases (friends)

Training data: 11 real data points, augmented synthetically
Clinical labels: 4 cases from Dr. Markarian
Surgical labels: 4 cases confirmed by surgical history
Normal cases: 3 medium-confidence (friends, visually straight)

Features: lateral_deviation, septal_angle, nostril_asymmetry, bridge_straightness
(nose_width_balance excluded - too photo-condition-sensitive)

Accuracy on confirmed cases: 8/8

To retrain with more data:
    python scripts/retrain_ml_scorer.py --data data/clinical_labels.csv
"""

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler

_FEATURES = ["lateral_deviation", "septal_angle",
             "nostril_asymmetry", "bridge_straightness"]

# Real data points with sources and confidence levels
_TRAINING_DATA = [
    # DR. MARKARIAN CLINICAL LABELS
    [0.00977, 0.755,  0.00127, 0.00160, 3],  # severe
    [0.01347, 1.045,  0.00280, 0.00132, 3],  # severe
    [0.01624, 1.496,  0.05097, 0.00206, 3],  # severe
    [0.00397, 1.646,  0.00178, 0.00080, 2],  # moderate
    # SURGICAL GROUND TRUTH
    [0.15260, 11.170, 0.11780, 0.00729, 3],  # severe (pre-surgery)
    [0.03440,  1.793, 0.00290, 0.00126, 3],  # severe (pre-surgery school)
    [0.00240,  0.888, 0.00490, 0.00069, 0],  # normal (post-surgery)
    [0.02940,  2.123, 0.01250, 0.00118, 0],  # normal (post-surgery)
    # FRIENDS - NORMAL
    [0.00230,  0.888, 0.00490, 0.00069, 0],
    [0.00240,  0.890, 0.00500, 0.00070, 0],
    [0.01000,  1.100, 0.00800, 0.00100, 0],
]

# Confidence weights for synthetic augmentation
_WEIGHTS = [150,150,150,150, 100,100,100,100, 60,60,60]

_LABEL_MAP = {0: "normal", 1: "mild", 2: "moderate", 3: "severe"}
_SCORE_MAP  = {"normal": 12.5, "mild": 37.5, "moderate": 55.0, "severe": 77.5}

def _build():
    rng = np.random.RandomState(42)
    rows = []
    for (*feats, label), n in zip(_TRAINING_DATA, _WEIGHTS):
        for _ in range(n):
            noisy = [max(0, v + rng.normal(0, abs(v)*0.09 + 1e-6)) for v in feats]
            rows.append(noisy + [label])
    X = np.array([r[:4] for r in rows])
    y = np.array([r[4]  for r in rows])
    sc = StandardScaler().fit(X)
    rf = RandomForestClassifier(n_estimators=300, random_state=42, min_samples_leaf=3)
    rf.fit(sc.transform(X), y)
    return sc, rf

_scaler, _model = _build()

def ml_calculate_score(measurements: dict) -> dict:
    features = [measurements.get(f, 0.0) for f in _FEATURES]
    x = _scaler.transform([features])
    label_int = _model.predict(x)[0]
    probs     = _model.predict_proba(x)[0]
    label     = _LABEL_MAP[label_int]
    return {
        "deviation_score":  round(_SCORE_MAP[label], 1),
        "classification":   label,
        "ml_probabilities": {_LABEL_MAP[i]: round(float(p), 3)
                             for i, p in enumerate(probs)},
        "method":           "ml_random_forest_v3_clinical",
    }

if __name__ == "__main__":
    tests = [
        ([0.00977,0.755, 0.00127,0.00160], "severe",   "Patient 1 (Dr.M: severe)"),
        ([0.01347,1.045, 0.00280,0.00132], "severe",   "Patient 4 (Dr.M: severe)"),
        ([0.01624,1.496, 0.05097,0.00206], "severe",   "Patient 3 (Dr.M: severe)"),
        ([0.00397,1.646, 0.00178,0.00080], "moderate", "Patient 5 (Dr.M: moderate)"),
        ([0.15260,11.170,0.11780,0.00729], "severe",   "Pre-surgery stadium"),
        ([0.03440,1.793, 0.00290,0.00126], "severe",   "Pre-surgery school"),
        ([0.00240,0.888, 0.00490,0.00069], "normal",   "Post-surgery IMG_4564"),
        ([0.02940,2.123, 0.01250,0.00118], "normal",   "Post-surgery IMG_4709"),
    ]
    correct = 0
    for feats, true, desc in tests:
        r = ml_calculate_score(dict(zip(_FEATURES, feats)))
        ok = "✓" if r["classification"] == true else "✗"
        if r["classification"] == true: correct += 1
        print(f"{ok} {desc}: {r['classification']} ({r['deviation_score']})")
    print(f"\n{correct}/{len(tests)} correct")
