"""
CT validation logic for NoseCheck.

Loads ground truth data, runs paired or distribution validation,
and generates summary dictionaries for reporting.
"""

import csv
import sys
from pathlib import Path
from typing import Callable, Dict, List, Optional

_root = Path(__file__).resolve().parent.parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from src.analysis.statistics import (
    category_accuracy,
    descriptive_stats,
    linear_regression,
    pearson_r,
    r_squared,
    rmse,
)

CT_DATA_DIR = _root / "data" / "ct_validation"
CT_CSV_PATH = CT_DATA_DIR / "ct_ground_truth.csv"

SEVERITY_THRESHOLDS_MM = {"mild": (0, 2), "moderate": (2, 5), "severe": (5, float("inf"))}


def classify_by_mm(deviation_mm: float) -> str:
    """Classify severity from millimeter deviation."""
    if deviation_mm <= 2:
        return "mild"
    if deviation_mm <= 5:
        return "moderate"
    return "severe"


def classify_by_score(score: float) -> str:
    """Classify severity from NoseCheck 0-100 score."""
    if score < 25:
        return "normal"
    if score < 45:
        return "mild"
    if score < 65:
        return "moderate"
    return "severe"


def load_ct_ground_truth(csv_path: Optional[Path] = None) -> List[Dict]:
    """
    Load and validate ct_ground_truth.csv.

    Returns list of dicts with patient_id, ct_source, max_deviation_mm, severity_ct.
    """
    path = csv_path or CT_CSV_PATH
    if not path.exists():
        return []

    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                row["max_deviation_mm"] = float(row.get("max_deviation_mm", 0))
            except (ValueError, TypeError):
                continue

            if row.get("deviation_angle_deg"):
                try:
                    row["deviation_angle_deg"] = float(row["deviation_angle_deg"])
                except (ValueError, TypeError):
                    row["deviation_angle_deg"] = None
            else:
                row["deviation_angle_deg"] = None

            if not row.get("severity_ct"):
                row["severity_ct"] = classify_by_mm(row["max_deviation_mm"])

            row["has_photo"] = bool(row.get("photo_filename", "").strip())
            rows.append(row)

    return rows


def run_paired_validation(
    ground_truth: List[Dict],
    pipeline_fn: Callable,
    photo_dir: Optional[Path] = None,
) -> Dict:
    """
    Run NoseCheck on photos paired with CT data.

    For each entry with a photo_filename, runs pipeline_fn(photo_path)
    and collects (deviation_mm, nosecheck_score) pairs.
    """
    pdir = photo_dir or CT_DATA_DIR
    paired_entries = [e for e in ground_truth if e.get("has_photo")]

    if not paired_entries:
        return {"n_paired": 0, "results": [], "stats": {}}

    deviations_mm = []
    scores = []
    expected_cats = []
    actual_cats = []
    details = []

    for entry in paired_entries:
        photo_path = pdir / entry["photo_filename"]
        if not photo_path.exists():
            details.append({
                "patient_id": entry["patient_id"],
                "status": "photo_missing",
                "photo_filename": entry["photo_filename"],
            })
            continue

        result = pipeline_fn(str(photo_path))
        if result is None:
            details.append({
                "patient_id": entry["patient_id"],
                "status": "no_face_detected",
                "photo_filename": entry["photo_filename"],
            })
            continue

        nc_score = result.get("deviation_score", 0)
        nc_class = result.get("classification", classify_by_score(nc_score))
        mm = entry["max_deviation_mm"]

        deviations_mm.append(mm)
        scores.append(nc_score)
        expected_cats.append(entry["severity_ct"])
        actual_cats.append(nc_class)

        details.append({
            "patient_id": entry["patient_id"],
            "status": "success",
            "deviation_mm": mm,
            "nosecheck_score": nc_score,
            "ct_severity": entry["severity_ct"],
            "nosecheck_severity": nc_class,
            "match": entry["severity_ct"] == nc_class,
            "photo_filename": entry["photo_filename"],
        })

    stats = {}
    if len(deviations_mm) >= 2:
        reg = linear_regression(deviations_mm, scores)
        predicted = [reg["slope"] * d + reg["intercept"] for d in deviations_mm]
        stats = {
            "pearson_r": reg["r"],
            "r_squared": reg["r_squared"],
            "slope": reg["slope"],
            "intercept": reg["intercept"],
            "p_value": reg["p_value_approx"],
            "rmse": rmse(scores, predicted),
            "n": len(deviations_mm),
        }

    cat_stats = {}
    if expected_cats:
        cat_stats = category_accuracy(expected_cats, actual_cats)

    return {
        "n_paired": len(deviations_mm),
        "results": details,
        "stats": stats,
        "category_stats": cat_stats,
        "deviations_mm": deviations_mm,
        "scores": scores,
        "expected_categories": expected_cats,
        "actual_categories": actual_cats,
    }


def run_distribution_validation(
    ct_data: List[Dict],
    calibration_data: Optional[List[Dict]] = None,
) -> Dict:
    """
    Compare severity distributions between CT ground truth and NoseCheck scoring.

    Works without paired photos -- compares proportion of mild/moderate/severe
    in the CT population against NoseCheck calibration results.
    """
    ct_cats = [e.get("severity_ct", classify_by_mm(e["max_deviation_mm"])) for e in ct_data]
    ct_dist = {}
    for cat in ["mild", "moderate", "severe"]:
        ct_dist[cat] = sum(1 for c in ct_cats if c == cat)

    nc_dist = {}
    if calibration_data:
        for cat in ["normal", "mild", "moderate", "severe"]:
            nc_dist[cat] = sum(1 for c in calibration_data if c.get("classification") == cat)

    ct_stats = descriptive_stats([e["max_deviation_mm"] for e in ct_data])

    return {
        "ct_distribution": ct_dist,
        "nosecheck_distribution": nc_dist,
        "ct_stats": ct_stats,
        "n_ct": len(ct_data),
        "n_nosecheck": len(calibration_data) if calibration_data else 0,
    }


def validate_ct_dataset(
    csv_path: Optional[Path] = None,
    run_pipeline_fn: Optional[Callable] = None,
    photo_dir: Optional[Path] = None,
) -> Dict:
    """
    End-to-end validation: load CSV, run NoseCheck on each photo, return
    structured results with statistics.

    Args:
        csv_path: Path to ct_ground_truth.csv (defaults to CT_CSV_PATH).
        run_pipeline_fn: Function that takes image path and returns result dict.
        photo_dir: Directory containing patient photos.

    Returns:
        Dict with ground_truth, paired results, stats, and details.
    """
    ground_truth = load_ct_ground_truth(csv_path)
    if not ground_truth:
        return {"ground_truth": [], "n_total": 0, "n_with_photo": 0, "paired": {}}

    n_with_photo = sum(1 for e in ground_truth if e.get("has_photo"))

    paired = {"n_paired": 0, "results": [], "stats": {}}
    if run_pipeline_fn and n_with_photo > 0:
        paired = run_paired_validation(ground_truth, run_pipeline_fn, photo_dir)

    return {
        "ground_truth": ground_truth,
        "n_total": len(ground_truth),
        "n_with_photo": n_with_photo,
        "paired": paired,
    }


def compare_severity_categories(
    ct_severity: List[str],
    nosecheck_classification: List[str],
) -> Dict:
    """
    Confusion-matrix style comparison between CT severity and NoseCheck
    classification.

    Returns dict with overall_accuracy, per_category breakdown, and
    a confusion_matrix dict mapping (expected, actual) pairs to counts.
    """
    acc = category_accuracy(ct_severity, nosecheck_classification)

    confusion = {}
    for exp, act in zip(ct_severity, nosecheck_classification):
        key = (exp, act)
        confusion[key] = confusion.get(key, 0) + 1

    acc["confusion_matrix"] = confusion
    return acc


def generate_validation_summary(
    paired: Dict,
    distribution: Optional[Dict] = None,
) -> Dict:
    """
    Combine paired and distribution validation into a single summary
    suitable for report rendering.

    Can be called with just paired results (distribution is optional).
    """
    summary = {
        "n_paired": paired.get("n_paired", 0),
    }

    if distribution:
        summary.update({
            "n_ct_total": distribution.get("n_ct", 0),
            "ct_distribution": distribution.get("ct_distribution", {}),
            "nosecheck_distribution": distribution.get("nosecheck_distribution", {}),
            "ct_stats": distribution.get("ct_stats", {}),
        })
    else:
        summary["n_ct_total"] = paired.get("n_paired", 0)

    if paired.get("stats"):
        summary.update({
            "pearson_r": paired["stats"].get("pearson_r", 0),
            "r_squared": paired["stats"].get("r_squared", 0),
            "slope": paired["stats"].get("slope", 0),
            "intercept": paired["stats"].get("intercept", 0),
            "rmse": paired["stats"].get("rmse", 0),
            "p_value": paired["stats"].get("p_value", 1.0),
        })

    if paired.get("category_stats"):
        summary["category_accuracy"] = paired["category_stats"]

    summary["paired_details"] = paired.get("results", [])

    return summary
