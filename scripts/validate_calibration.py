#!/usr/bin/env python3
"""
Validate NoseCheck calibration accuracy.

Reads calibration_results.csv and metadata.csv, computes correlation
between known physical deviation (mm) and predicted deviation score,
and reports R-squared and per-image accuracy.

Reports separate R-squared for 3D models vs CT-validated entries
and severity category accuracy.

Usage:
    python scripts/validate_calibration.py

Target: R-squared > 0.85
"""

import csv
import sys
from pathlib import Path

_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_root))

from src.analysis.statistics import linear_regression, rmse as compute_rmse, category_accuracy

CALIBRATION_DIR = _root / "data" / "calibration_models"
RESULTS_PATH = CALIBRATION_DIR / "calibration_results.csv"
METADATA_PATH = CALIBRATION_DIR / "metadata.csv"


def load_results():
    """Load calibration results CSV."""
    if not RESULTS_PATH.exists():
        return []
    with open(RESULTS_PATH, newline="") as f:
        return list(csv.DictReader(f))


def load_metadata():
    """Load calibration metadata CSV keyed by filename."""
    if not METADATA_PATH.exists():
        return {}
    with open(METADATA_PATH, newline="") as f:
        return {row["filename"]: row for row in csv.DictReader(f)}


def _classify_mm(mm):
    """Classify deviation in mm to severity category."""
    if mm <= 2:
        return "normal"
    if mm <= 5:
        return "mild"
    if mm <= 8:
        return "moderate"
    return "severe"


def _report_regression(label, known_mm, actual_scores):
    """Compute and print regression stats for a group of entries."""
    if len(known_mm) < 2:
        print(f"\n  {label}: Not enough data (need >= 2, have {len(known_mm)})")
        return

    reg = linear_regression(known_mm, actual_scores)
    r_sq = reg["r_squared"]
    target = 0.85
    status = "PASS" if r_sq >= target else "NEEDS TUNING"
    print(f"\n  {label} ({len(known_mm)} entries):")
    print(f"    R-squared:  {r_sq:.4f}  (target >= {target})  [{status}]")
    print(f"    Pearson r:  {reg['r']:.4f}")
    print(f"    Linear fit: score = {reg['slope']:.2f} * mm + {reg['intercept']:.2f}")

    predicted = [reg["slope"] * m + reg["intercept"] for m in known_mm]
    err = compute_rmse(actual_scores, predicted)
    print(f"    RMSE:       {err:.2f}")


def main():
    results = load_results()
    metadata = load_metadata()

    if not results:
        print("No calibration results found.")
        print("Run  python scripts/calibration_workflow.py  first.")
        return

    all_mm = []
    all_scores = []
    model_3d_mm = []
    model_3d_scores = []
    ct_mm = []
    ct_scores = []
    clinical_mm = []
    clinical_scores = []

    expected_classes = []
    actual_classes = []

    pass_count = 0
    fail_count = 0
    skip_count = 0

    print(f"{'Filename':<25} {'Known mm':>8} {'Score':>6} {'Expected':>12} {'Type':>10} {'Status':>8}")
    print("-" * 75)

    for row in results:
        filename = row.get("filename", "")
        status = row.get("status", "")

        if status in ("skipped", "no_face"):
            skip_count += 1
            print(f"{filename:<25} {'---':>8} {'---':>6} {'---':>12} {'---':>10} {status:>8}")
            continue

        try:
            mm = float(row.get("known_deviation_mm", 0))
            score = float(row.get("actual_score", 0))
        except (ValueError, TypeError):
            skip_count += 1
            continue

        exp_min = float(row.get("expected_score_min", 0))
        exp_max = float(row.get("expected_score_max", 100))
        in_range = row.get("score_in_range", "False") == "True"

        model_type = row.get("model_type", "")
        data_source = row.get("data_source", "")
        if not data_source and filename in metadata:
            data_source = metadata[filename].get("data_source", "")
        if not model_type and filename in metadata:
            model_type = metadata[filename].get("model_type", "")

        # Determine group
        if data_source:
            group_label = "ct_val"
        elif model_type == "3d_model":
            group_label = "3d"
        else:
            group_label = "clinical"

        all_mm.append(mm)
        all_scores.append(score)

        if group_label == "3d":
            model_3d_mm.append(mm)
            model_3d_scores.append(score)
        elif group_label == "ct_val":
            ct_mm.append(mm)
            ct_scores.append(score)
        else:
            clinical_mm.append(mm)
            clinical_scores.append(score)

        # Severity accuracy tracking
        exp_class = row.get("expected_classification", "")
        act_class = row.get("actual_classification", "")
        if not exp_class:
            exp_class = _classify_mm(mm)
        if exp_class and act_class:
            expected_classes.append(exp_class)
            actual_classes.append(act_class)

        label = "PASS" if in_range else "FAIL"
        if in_range:
            pass_count += 1
        else:
            fail_count += 1

        print(f"{filename:<25} {mm:>8.1f} {score:>6.1f} [{exp_min:.0f}-{exp_max:.0f}]{' ':>2} {group_label:>10} {label:>8}")

    print("-" * 75)

    # Overall R-squared
    print("\n" + "=" * 50)
    print("CORRELATION ANALYSIS")
    print("=" * 50)
    _report_regression("Overall (all entries)", all_mm, all_scores)
    _report_regression("3D Models only", model_3d_mm, model_3d_scores)
    _report_regression("CT-Validated only", ct_mm, ct_scores)
    if clinical_mm:
        _report_regression("Clinical photos only", clinical_mm, clinical_scores)

    # Severity category accuracy
    print("\n" + "=" * 50)
    print("SEVERITY CATEGORY ACCURACY")
    print("=" * 50)

    if expected_classes and actual_classes:
        cat_result = category_accuracy(expected_classes, actual_classes)
        overall_acc = cat_result["overall_accuracy"] * 100
        print(f"\n  Overall: {cat_result['correct']}/{cat_result['n']} correct ({overall_acc:.0f}%)")
        print(f"\n  {'Category':<12} {'Correct':>8} {'Total':>6} {'Accuracy':>10}")
        print(f"  {'-'*38}")
        for cat_name in ["normal", "mild", "moderate", "severe"]:
            info = cat_result["per_category"].get(cat_name)
            if info:
                pct = info["accuracy"] * 100
                print(f"  {cat_name.capitalize():<12} {info['correct']:>8} {info['total']:>6} {pct:>9.0f}%")
    else:
        print("\n  No severity data available.")

    # Summary
    print(f"\n{'='*50}")
    accuracy = pass_count / (pass_count + fail_count) * 100 if (pass_count + fail_count) > 0 else 0
    print(f"Score range accuracy: {pass_count}/{pass_count+fail_count} in expected range ({accuracy:.0f}%)")
    print(f"Skipped: {skip_count} (missing file or no face detected)")

    if fail_count > 0:
        print("\nFailed images need attention - consider:")
        print("  1. Retaking photos under better conditions")
        print("  2. Adjusting scaling_factors in config.py")
        print("  3. Updating expected_score ranges in metadata.csv")


if __name__ == "__main__":
    main()
