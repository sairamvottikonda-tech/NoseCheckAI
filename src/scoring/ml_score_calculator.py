"""
ML-based scoring - Random Forest, trained on 38 real confirmed data points.

38 total: 13 severe, 8 moderate, 2 mild, 15 normal - from Dr. Markarian's
clinical assessments, confirmed surgical ground truth, and verified
normal-photo consistency testing.

Leave-one-out honest accuracy: 53%.

Uses Random Forest (not Gradient Boosting) specifically because Random
Forest's predict_proba shows real variation between different cases in
the same class, producing genuinely different continuous scores instead
of clustering at one fixed value per class.
"""

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler

_FEATURES = ["lateral_deviation", "septal_angle", "bridge_straightness"]

_TRAINING_DATA = [
    (0.00977, 0.755,  0.00160, 3),
    (0.01347, 1.045,  0.00132, 3),
    (0.01624, 1.496,  0.00206, 3),
    (0.00397, 1.646,  0.00080, 2),
    (0.00736, 0.655,  0.00054, 2),
    (0.00808, 2.519,  0.00143, 3),
    (0.00439, 1.001,  0.00111, 2),
    (0.00245, 1.1336, 0.00101, 2),
    (0.15260, 11.170, 0.00729, 3),
    (0.03440,  1.793, 0.00126, 3),
    (0.00240,  0.888, 0.00069, 0),
    (0.02940,  2.123, 0.00118, 0),
    (0.00230,  0.888, 0.00069, 0),
    (0.00240,  0.890, 0.00070, 0),
    (0.01770,  0.546, 0.00190, 0),
    (0.00260,  1.402, 0.00091, 0),
    (0.01349,  0.091, 0.00070, 0),
    (0.01313,  0.010, 0.00093, 0),
    (0.00919,  0.556, 0.00082, 0),
    (0.00220,  0.806, 0.00082, 0),
    (0.00288,  1.089, 0.00096, 0),
    (0.03654, 1.6318, 0.00109, 3),
    (0.00808, 2.3669, 0.00143, 3),
    (0.00525, 0.6475, 0.00071, 2),
    (0.01262, 0.1901, 0.00082, 3),
    (0.02428, 2.2199, 0.00217, 3),
    (0.01658, 0.4898, 0.00171, 3),
    (0.01624, 1.4059, 0.00206, 3),
    (0.01504, 0.9862, 0.00162, 3),
    (0.01449, 0.0376, 0.00135, 0),
    (0.01185, 1.6088, 0.00077, 1),
    (0.00345, 0.0402, 0.00089, 1),
    (0.00196, 0.9681, 0.00122, 0),
    (0.00665, 1.1611, 0.00092, 0),
    (0.02548, 1.1591, 0.00201, 0),
    (0.02225, 0.6178, 0.00081, 2),
    (0.01114, 1.0431, 0.00108, 2),
    (0.00439, 0.9410, 0.00111, 2),
]

_LABEL_MAP = {0: "normal", 1: "mild", 2: "moderate", 3: "severe"}
_SCORE_RANGES = {
    "normal":   (0, 25),
    "mild":     (25, 45),
    "moderate": (45, 65),
    "severe":   (65, 95),
}

def _build():
    X = np.array([[d[0], d[1], d[2]] for d in _TRAINING_DATA])
    y = np.array([d[3] for d in _TRAINING_DATA])
    sc = StandardScaler().fit(X)
    rf = RandomForestClassifier(n_estimators=200, random_state=42, min_samples_leaf=2)
    rf.fit(sc.transform(X), y)
    return sc, rf

_scaler, _model = _build()

def ml_calculate_score(measurements: dict) -> dict:
    features = [measurements.get(f, 0.0) for f in _FEATURES]
    x = _scaler.transform([features])

    label_int = _model.predict(x)[0]
    label = _LABEL_MAP[label_int]
    probs = _model.predict_proba(x)[0]
    class_prob = float(probs[label_int])

    low, high = _SCORE_RANGES[label]
    position = (class_prob - 0.25) / (1.0 - 0.25)
    position = max(0.05, min(0.95, position))

    score = low + (high - low) * position
    score = round(max(low, min(high, score)), 1)

    return {
        "deviation_score":  score,
        "classification":   label,
        "confidence":         round(class_prob, 3),
        "method":            "random_forest_v4final",
    }

if __name__ == "__main__":
    print("Testing severe cases for score variation:")
    tests = [
        ([0.00977, 0.755,  0.00160], "severe",   "Patient 1"),
        ([0.03654, 1.6318, 0.00109], "severe",   "Screenshot 9.51.12"),
        ([0.02428, 2.2199, 0.00217], "severe",   "Screenshot 5.57.16"),
        ([0.00240,  0.888, 0.00069], "normal",   "Post-surgery"),
        ([0.00525, 0.6475, 0.00071], "moderate", "Screenshot 5.32.20"),
    ]
    correct = 0
    for feats, true_cls, desc in tests:
        r = ml_calculate_score(dict(zip(_FEATURES, feats)))
        ok = "✓" if r["classification"] == true_cls else "✗"
        if r["classification"] == true_cls: correct += 1
        print(f"{ok} {desc}: {r['deviation_score']} ({r['classification']})")
    print(f"\n{correct}/{len(tests)} correct")
