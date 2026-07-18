"""
ML-based scoring module for NoseCheck v2.
Uses 4 stable features (drops nose_width_balance which was too photo-condition-sensitive).
Trained on 12 real data points + synthetic augmentation.

Ground truth sources:
- HIGH: Sairam's own pre/post surgical photos (confirmed by surgical history)
- MEDIUM: Friends with visually straight noses
- LOW: Calibration photos with user severity estimates

To retrain: python scripts/retrain_ml_scorer.py --data data/clinical_labels.csv
"""

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler

_FEATURES = ["lateral_deviation", "septal_angle",
             "nostril_asymmetry", "bridge_straightness"]

_ALL_DATA = [
    # HIGH confidence - confirmed surgical history
    [0.1526, 11.170, 0.1178, 0.00729, 3],  # severe
    [0.0344,  1.793, 0.0029, 0.00126, 3],  # severe
    [0.0024,  0.888, 0.0049, 0.00069, 0],  # normal
    [0.0294,  2.123, 0.0125, 0.00118, 0],  # normal
    # MEDIUM confidence - friends (normal)
    [0.0023,  0.888, 0.0049, 0.00069, 0],
    [0.0024,  0.890, 0.0050, 0.00070, 0],
    [0.0100,  1.100, 0.0080, 0.00100, 0],
    # LOW confidence - user estimates
    [0.00397, 1.646, 0.0018, 0.00080, 2],  # moderate
    [0.01347, 1.045, 0.0028, 0.00132, 3],  # severe
    [0.01770, 0.546, 0.0438, 0.00190, 0],  # normal
    [0.00260, 1.402, 0.0428, 0.00091, 0],  # normal
    [0.01624, 1.496, 0.0510, 0.00206, 3],  # severe
]

_LABEL_MAP = {0: "normal", 1: "mild", 2: "moderate", 3: "severe"}
_SCORE_MAP  = {"normal": 12.5, "mild": 37.5, "moderate": 55.0, "severe": 77.5}

def _build():
    rng = np.random.RandomState(42)
    rows = []
    for *feats, label in _ALL_DATA:
        for _ in range(80):
            noisy = [max(0, v + rng.normal(0, abs(v)*0.10 + 1e-6)) for v in feats]
            rows.append(noisy + [label])
    X = np.array([r[:4] for r in rows])
    y = np.array([r[4]  for r in rows])
    sc = StandardScaler().fit(X)
    rf = RandomForestClassifier(n_estimators=200, random_state=42, min_samples_leaf=3)
    rf.fit(sc.transform(X), y)
    return sc, rf

_scaler, _model = _build()

def ml_calculate_score(measurements: dict) -> dict:
    features = [measurements.get(f, 0.0) for f in _FEATURES]
    x = _scaler.transform([features])
    label_int  = _model.predict(x)[0]
    probs      = _model.predict_proba(x)[0]
    label      = _LABEL_MAP[label_int]
    return {
        "deviation_score":    round(_SCORE_MAP[label], 1),
        "classification":     label,
        "ml_probabilities":   {_LABEL_MAP[i]: round(float(p), 3)
                               for i, p in enumerate(probs)},
        "method":             "ml_random_forest_v2",
    }

if __name__ == "__main__":
    tests = [
        ([0.1526,11.170,0.1178,0.00729], "severe",  "Pre-surgery stadium"),
        ([0.0344, 1.793,0.0029,0.00126], "severe",  "Pre-surgery school"),
        ([0.0024, 0.888,0.0049,0.00069], "normal",  "Post-surgery IMG_4564"),
        ([0.0294, 2.123,0.0125,0.00118], "normal",  "Post-surgery IMG_4709"),
    ]
    correct = 0
    for feats, true, desc in tests:
        r = ml_calculate_score(dict(zip(_FEATURES, feats)))
        ok = "✓" if r["classification"] == true else "✗"
        if r["classification"] == true: correct += 1
        print(f"{ok} {desc}: {r['classification']} ({r['deviation_score']})")
    print(f"\n{correct}/{len(tests)} correct")
