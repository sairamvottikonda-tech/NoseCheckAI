"""
Retraining script for the ML scorer.

Run this whenever new clinical data is available:
    python scripts/retrain_ml_scorer.py --data data/clinical_labels.csv

Expected CSV format:
    filename, lateral_deviation, septal_angle, nostril_asymmetry,
    bridge_straightness, nose_width_balance, clinical_label
    (clinical_label: normal/mild/moderate/severe)

The script will:
1. Load real clinical labels
2. Combine with existing synthetic data
3. Retrain the Random Forest
4. Print accuracy metrics
5. Save updated model weights to src/scoring/ml_weights.json
"""

import argparse, json, sys
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import cross_val_score

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data', required=True, help='Path to clinical labels CSV')
    args = parser.parse_args()

    import csv
    label_map = {"normal":0,"mild":1,"moderate":2,"severe":3}
    reverse_map = {0:"normal",1:"mild",2:"moderate",3:"severe"}

    real_rows = []
    with open(args.data) as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                features = [
                    float(row['lateral_deviation']),
                    float(row['septal_angle']),
                    float(row['nostril_asymmetry']),
                    float(row['bridge_straightness']),
                    float(row['nose_width_balance']),
                ]
                label = label_map[row['clinical_label'].strip().lower()]
                real_rows.append(features + [label])
            except (KeyError, ValueError) as e:
                print(f"Skipping row: {e}")

    print(f"Loaded {len(real_rows)} real clinical cases")

    X = np.array([r[:5] for r in real_rows])
    y = np.array([r[5]  for r in real_rows])

    scaler = StandardScaler().fit(X)
    X_scaled = scaler.transform(X)

    rf = RandomForestClassifier(n_estimators=200, random_state=42, min_samples_leaf=2)
    if len(X) >= 5:
        scores = cross_val_score(rf, X_scaled, y, cv=min(5, len(X)))
        print(f"CV accuracy: {scores.mean():.3f} ± {scores.std():.3f}")
    rf.fit(X_scaled, y)

    weights = {
        "scaler_mean": scaler.mean_.tolist(),
        "scaler_scale": scaler.scale_.tolist(),
        "feature_names": ["lateral_deviation","septal_angle","nostril_asymmetry",
                          "bridge_straightness","nose_width_balance"],
        "n_samples": len(X),
        "class_distribution": {reverse_map[i]: int(sum(y==i)) for i in range(4)},
    }
    out = 'src/scoring/ml_weights.json'
    with open(out,'w') as f:
        json.dump(weights, f, indent=2)
    print(f"Saved to {out}")
    print("Re-import ml_score_calculator to use updated weights.")

if __name__ == "__main__":
    main()
