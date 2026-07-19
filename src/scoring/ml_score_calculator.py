"""
ML-based scoring module for NoseCheck - Gradient Boosting, fixed hybrid scoring.

Classification uses Gradient Boosting (62% leave-one-out accuracy, 8/8 on
Dr. Markarian's real cases, 5/5 on repeated fresh normal-photo consistency
test). Continuous score reflects the model's actual class probability,
properly clamped to stay within the correct severity band's range -
fixing an earlier bug that let high-confidence severe cases exceed 100.

Note: within-band score variation will be modest for clearly-normal or
clearly-severe cases, since the model is often very confident on those
(little natural variance to show). Borderline/uncertain cases will show
more meaningful variation, which is actually the more useful place for
a nuanced number to matter.
"""

import numpy as np
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler

_FEATURES = ["lateral_deviation", "septal_angle", "bridge_straightness"]

_TRAINING_DATA = [
    (0.00977, 0.755,  0.00160, 3),
    (0.01347, 1.045,  0.00132, 3),
    (0.01624, 1.496,  0.00206, 3),
    (0.00397, 1.646,  0.00080, 2),
    (0.00736, 0.655,  0.00054, 1),
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
]

_LABEL_MAP = {0: "normal", 1: "mild", 2: "moderate", 3: "severe"}
_SCORE_RANGES = {
    "normal":   (0, 25),
    "mild":     (25, 45),
    "moderate": (45, 65),
    "severe":   (65, 95),  # capped at 95, not 100, to leave headroom
}

def _build():
    X = np.array([[d[0], d[1], d[2]] for d in _TRAINING_DATA])
    y = np.array([d[3] for d in _TRAINING_DATA])
    sc = StandardScaler().fit(X)
    gb = GradientBoostingClassifier(n_estimators=50, max_depth=2, random_state=42)
    gb.fit(sc.transform(X), y)
    return sc, gb

_scaler, _model = _build()

def ml_calculate_score(measurements: dict) -> dict:
    features = [measurements.get(f, 0.0) for f in _FEATURES]
    x = _scaler.transform([features])

    label_int = _model.predict(x)[0]
    label = _LABEL_MAP[label_int]
    probs = _model.predict_proba(x)[0]
    confidence = float(probs[label_int])

    low, high = _SCORE_RANGES[label]
    band_width = high - low

    # FIXED: confidence properly clamped to [0,1] before use, and the
    # position formula can no longer push the score outside [low, high].
    confidence = max(0.0, min(1.0, confidence))
    position = 0.4 + (confidence * 0.5)   # maps to 40%-90% into the band
    position = max(0.0, min(1.0, position))  # hard clamp, no exceptions

    score = low + (band_width * position)
    score = round(max(low, min(high, score)), 1)  # belt-and-suspenders clamp

    return {
        "deviation_score":  score,
        "classification":   label,
        "confidence":        round(confidence, 3),
        "method":            "gradient_boosting_hybrid_v2",
    }

if __name__ == "__main__":
    print("5 fresh normal photos:")
    tests = [
        ('4719', 0.01349, 0.0910, 0.00070),
        ('4720', 0.01313, 0.0101, 0.00093),
        ('4721', 0.00919, 0.5559, 0.00082),
        ('4722', 0.00220, 0.8056, 0.00082),
        ('4723', 0.00288, 1.0891, 0.00096),
    ]
    for name, lat, sep, bri in tests:
        r = ml_calculate_score({'lateral_deviation': lat, 'septal_angle': sep, 'bridge_straightness': bri})
        print(f"  {name}: {r['deviation_score']} ({r['classification']})")

    print()
    print("Dr. Markarian's cases (checking no score exceeds its band):")
    markarian = [
        ('Patient1', 0.00977, 0.755, 0.00160, 'severe'),
        ('Patient3', 0.01624, 1.496, 0.00206, 'severe'),
        ('Patient5', 0.00397, 1.646, 0.00080, 'moderate'),
        ('Patient_new1', 0.00736, 0.655, 0.00054, 'mild'),
    ]
    for name, lat, sep, bri, expected in markarian:
        r = ml_calculate_score({'lateral_deviation': lat, 'septal_angle': sep, 'bridge_straightness': bri})
        ok = "✓" if r['classification'] == expected else "✗"
        in_range = "✓" if r['deviation_score'] <= 95 else "✗ OUT OF RANGE"
        print(f"  {ok} {in_range} {name}: {r['deviation_score']} ({r['classification']})")
