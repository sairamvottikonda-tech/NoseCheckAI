#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CT Validation Runner for NoseCheck.

Orchestrates the full CT-to-photo validation pipeline:
1. Loads ct_ground_truth.csv
2. Runs NoseCheck on paired photos (3D Slicer renderings)
3. Computes Pearson r, R-squared, RMSE, category accuracy
4. Generates publication-ready plots
5. Produces a self-contained HTML research report
6. Prints a formatted terminal summary

Usage:
    python scripts/validate_ct_correlation.py
    python scripts/validate_ct_correlation.py --csv path/to/custom.csv
"""

import argparse
import base64
import csv
import datetime
import sys
from pathlib import Path

_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_root))

from src.analysis.statistics import descriptive_stats, linear_regression
from src.analysis.validation import (
    CT_CSV_PATH,
    CT_DATA_DIR,
    generate_validation_summary,
    load_ct_ground_truth,
    run_distribution_validation,
    run_paired_validation,
)
from src.analysis.visualizations import (
    plot_regression_with_ci,
    plot_score_boxplot,
    plot_severity_distribution,
)


def _pipeline_fn(image_path: str):
    """Run the NoseCheck analysis pipeline on a single image."""
    from src.app import run_pipeline
    return run_pipeline(image_path)


def _load_calibration_results():
    """Load existing calibration results if available."""
    cal_csv = _root / "data" / "calibration_models" / "calibration_results.csv"
    if not cal_csv.exists():
        return []
    with open(cal_csv, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _img_to_base64(path: Path) -> str:
    """Read an image file and return base64-encoded string."""
    if not path.is_file():
        return ""
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def _sanitize(value) -> str:
    """Replace NaN/None with em-dash for display."""
    if value is None:
        return "—"
    s = str(value)
    if s.lower() in ("nan", "none", ""):
        return "—"
    return s


def _severity_color(severity: str) -> str:
    """Return inline color style for a severity label."""
    colors_map = {"mild": "#4CAF50", "moderate": "#FF9800", "severe": "#F44336", "normal": "#4CAF50"}
    c = colors_map.get(severity.lower(), "#888")
    return f"<span style='color:{c};font-weight:bold'>{severity.capitalize()}</span>"


def _metric_badge(value: float, thresholds: tuple) -> str:
    """Return a badge span based on good/acceptable/poor thresholds.

    thresholds = (good_threshold, acceptable_threshold, higher_is_better)
    """
    good_t, ok_t, higher_better = thresholds
    if higher_better:
        if value >= good_t:
            return "<span class='badge badge-good'>Good</span>"
        if value >= ok_t:
            return "<span class='badge badge-ok'>Acceptable</span>"
        return "<span class='badge badge-poor'>Poor</span>"
    else:
        if value <= good_t:
            return "<span class='badge badge-good'>Good</span>"
        if value <= ok_t:
            return "<span class='badge badge-ok'>Acceptable</span>"
        return "<span class='badge badge-poor'>Poor</span>"


def generate_html_report(summary: dict, plot_paths: dict, output_path: Path,
                         ground_truth: list = None, simulated: bool = False):
    """Generate a self-contained HTML research report from template.

    Args:
        summary: Validation summary dict.
        plot_paths: Dict mapping plot names to Path objects.
        output_path: Where to write the HTML.
        ground_truth: Full list of CT entries (for the complete patient table).
        simulated: If True, show a warning that scores are simulated.
    """
    template_path = _root / "templates" / "validation_report.html"
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    scatter_b64 = _img_to_base64(plot_paths.get("regression", Path()))
    boxplot_b64 = _img_to_base64(plot_paths.get("boxplot", Path()))
    dist_b64 = _img_to_base64(plot_paths.get("distribution", Path()))

    def _img_tag(b64: str, alt: str) -> str:
        if b64:
            return f"<img src='data:image/png;base64,{b64}' alt='{alt}'>"
        return f"<p>No {alt} (need paired data)</p>"

    # Build patient rows — include both paired results and CT-only entries
    paired_lookup = {}
    for d in summary.get("paired_details", []):
        pid = d.get("patient_id", "")
        if pid:
            paired_lookup[pid] = d

    patient_rows = ""
    all_entries = ground_truth or []

    if all_entries:
        for entry in all_entries:
            pid = entry.get("patient_id", "")
            ct_source = _sanitize(entry.get("ct_source", ""))
            mm = entry.get("max_deviation_mm", 0)
            ct_sev = _sanitize(entry.get("severity_ct", ""))
            notes = _sanitize(entry.get("notes", ""))

            paired = paired_lookup.get(pid)
            if paired and paired.get("status") == "success":
                nc_score = paired.get("nosecheck_score", 0)
                nc_sev = paired.get("nosecheck_severity", "")
                match = paired.get("match", False)
                cls = "match" if match else "mismatch"
                match_text = "Match" if match else "Mismatch"
                patient_rows += (
                    f"<tr class='{cls}'>"
                    f"<td>{pid}</td>"
                    f"<td>{ct_source}</td>"
                    f"<td>{mm:.1f}</td>"
                    f"<td>{_severity_color(ct_sev)}</td>"
                    f"<td>{nc_score:.1f}</td>"
                    f"<td>{_severity_color(nc_sev)}</td>"
                    f"<td>{match_text}</td>"
                    f"<td>{notes}</td>"
                    f"</tr>\n"
                )
            elif paired and paired.get("status") in ("photo_missing", "no_face_detected"):
                patient_rows += (
                    f"<tr class='skip'>"
                    f"<td>{pid}</td>"
                    f"<td>{ct_source}</td>"
                    f"<td>{mm:.1f}</td>"
                    f"<td>{_severity_color(ct_sev)}</td>"
                    f"<td colspan='3'>{paired['status']}</td>"
                    f"<td>{notes}</td>"
                    f"</tr>\n"
                )
            else:
                patient_rows += (
                    f"<tr class='ct-only'>"
                    f"<td>{pid}</td>"
                    f"<td>{ct_source}</td>"
                    f"<td>{mm:.1f}</td>"
                    f"<td>{_severity_color(ct_sev)}</td>"
                    f"<td>—</td><td>—</td><td>—</td>"
                    f"<td>{notes if notes != '—' else 'CT-only'}</td>"
                    f"</tr>\n"
                )
    else:
        for d in summary.get("paired_details", []):
            if d.get("status") != "success":
                patient_rows += (
                    f"<tr class='skip'><td>{d.get('patient_id','')}</td>"
                    f"<td colspan='7'>{d.get('status','')}: "
                    f"{_sanitize(d.get('photo_filename',''))}</td></tr>\n"
                )
                continue
            cls = "match" if d.get("match") else "mismatch"
            match_text = "Match" if d.get("match") else "Mismatch"
            patient_rows += (
                f"<tr class='{cls}'>"
                f"<td>{d.get('patient_id','')}</td>"
                f"<td>—</td>"
                f"<td>{d.get('deviation_mm', 0):.1f}</td>"
                f"<td>{_severity_color(d.get('ct_severity',''))}</td>"
                f"<td>{d.get('nosecheck_score', 0):.1f}</td>"
                f"<td>{_severity_color(d.get('nosecheck_severity',''))}</td>"
                f"<td>{match_text}</td>"
                f"<td>—</td>"
                f"</tr>\n"
            )

    if not patient_rows:
        patient_rows = "<tr><td colspan='8'>No data available</td></tr>"

    # Category accuracy rows
    cat_rows = ""
    cat_acc = summary.get("category_accuracy", {})
    for cat_name, info in cat_acc.get("per_category", {}).items():
        pct = info["accuracy"] * 100
        cat_rows += (
            f"<tr><td>{cat_name.capitalize()}</td>"
            f"<td>{info['correct']}/{info['total']}</td>"
            f"<td>{pct:.0f}%</td></tr>\n"
        )
    if not cat_rows:
        cat_rows = "<tr><td colspan='3'>No paired data</td></tr>"

    overall_pct = cat_acc.get("overall_accuracy", 0) * 100
    overall_detail = f"{cat_acc.get('correct', 0)}/{cat_acc.get('n', 0)}"

    # Metric values and badges
    pearson_r_val = summary.get("pearson_r", 0)
    r_squared_val = summary.get("r_squared", 0)
    rmse_val = summary.get("rmse", 0)

    simulated_html = ""
    if simulated:
        simulated_html = (
            "<div class='warn'>&#9888;&#65039; NoseCheck scores are "
            "<strong>simulated</strong> for pipeline testing. "
            "Replace with real photo scores before publication.</div>"
        )

    replacements = {
        "{{timestamp}}": timestamp,
        "{{n_ct_total}}": str(summary.get("n_ct_total", 0)),
        "{{n_paired}}": str(summary.get("n_paired", 0)),
        "{{pearson_r}}": f"{pearson_r_val:.3f}",
        "{{pearson_r_badge}}": _metric_badge(abs(pearson_r_val), (0.8, 0.6, True)),
        "{{r_squared}}": f"{r_squared_val:.3f}",
        "{{r_squared_badge}}": _metric_badge(r_squared_val, (0.6, 0.4, True)),
        "{{rmse}}": f"{rmse_val:.1f}",
        "{{rmse_badge}}": _metric_badge(rmse_val, (10, 20, False)),
        "{{p_value}}": f"{summary.get('p_value', 1.0):.4f}",
        "{{slope}}": f"{summary.get('slope', 0):.2f}",
        "{{intercept}}": f"{summary.get('intercept', 0):.2f}",
        "{{scatter_plot}}": _img_tag(scatter_b64, "Regression plot"),
        "{{boxplot}}": _img_tag(boxplot_b64, "Box plot"),
        "{{distribution_chart}}": _img_tag(dist_b64, "Distribution chart"),
        "{{category_rows}}": cat_rows,
        "{{overall_accuracy_pct}}": f"{overall_pct:.0f}%",
        "{{overall_accuracy_detail}}": overall_detail,
        "{{accuracy_badge}}": _metric_badge(overall_pct, (80, 60, True)),
        "{{patient_rows}}": patient_rows,
        "{{simulated_warning}}": simulated_html,
    }

    html = template_path.read_text(encoding="utf-8")
    for placeholder, value in replacements.items():
        html = html.replace(placeholder, value)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)


def print_terminal_summary(summary: dict):
    """Print formatted validation results to terminal."""
    print("\n" + "=" * 60)
    print("  CT Validation Results")
    print("=" * 60)

    n_total = summary.get("n_ct_total", 0)
    n_paired = summary.get("n_paired", 0)
    n_skip = n_total - n_paired
    print(f"\n  Patients analyzed:  {n_paired} / {n_total}  ({n_skip} CT-only, no photo)")

    if summary.get("pearson_r") is not None:
        print(f"  Pearson r:          {summary['pearson_r']:.4f}")
        print(f"  R-squared:          {summary['r_squared']:.4f}")
        print(f"  RMSE:               {summary['rmse']:.1f} (score units)")
        print(f"  Linear fit:         score = {summary['slope']:.2f} * deviation_mm + {summary['intercept']:.2f}")

        p = summary.get("p_value", 1.0)
        if p < 0.001:
            print(f"  p-value:            < 0.001")
        else:
            print(f"  p-value:            {p:.4f}")

    cat_acc = summary.get("category_accuracy", {})
    if cat_acc.get("per_category"):
        print(f"\n  Per-Category Accuracy:")
        for cat_name, info in cat_acc["per_category"].items():
            pct = info["accuracy"] * 100
            print(f"    {cat_name.capitalize():<12} {info['correct']}/{info['total']} correct ({pct:.0f}%)")
        overall = cat_acc.get("overall_accuracy", 0) * 100
        print(f"    {'Overall':<12} {cat_acc.get('correct',0)}/{cat_acc.get('n',0)} ({overall:.0f}%)")

    # Show CT distribution
    ct_dist = summary.get("ct_distribution", {})
    if ct_dist:
        print(f"\n  CT Severity Distribution:")
        for cat in ["mild", "moderate", "severe"]:
            print(f"    {cat.capitalize():<12} {ct_dist.get(cat, 0)}")

    print("\n" + "=" * 60)


def main():
    parser = argparse.ArgumentParser(description="NoseCheck CT Validation")
    parser.add_argument("--csv", type=str, default=None,
                        help="Path to ct_ground_truth.csv")
    parser.add_argument("--simulated", action="store_true",
                        help="Mark scores as simulated in the report")
    args = parser.parse_args()

    csv_path = Path(args.csv) if args.csv else CT_CSV_PATH

    print(f"Loading CT ground truth from: {csv_path}")
    ct_data = load_ct_ground_truth(csv_path)

    if not ct_data:
        print(f"\nNo CT data found at {csv_path}")
        print("To get started:")
        print("  1. Download CT scans from TCIA or NasalSeg")
        print("  2. Measure septal deviation in 3D Slicer")
        print("  3. Record measurements in data/ct_validation/ct_ground_truth.csv")
        print("  4. For paired validation: render frontal views from CT and save as photos")
        print("\nSee docs/CT_VALIDATION_GUIDE.md for detailed instructions.")
        return

    print(f"  Found {len(ct_data)} entries")
    paired_count = sum(1 for e in ct_data if e.get("has_photo"))
    print(f"  {paired_count} with photos, {len(ct_data) - paired_count} CT-only")

    # Run paired validation (entries with photos)
    print("\nRunning paired validation...")
    paired_results = run_paired_validation(ct_data, _pipeline_fn)

    # Run distribution validation
    calibration_data = _load_calibration_results()
    dist_results = run_distribution_validation(ct_data, calibration_data)

    # Generate summary
    summary = generate_validation_summary(paired_results, dist_results)

    # Generate plots
    plot_paths = {}
    output_dir = CT_DATA_DIR

    if paired_results.get("n_paired", 0) >= 2:
        reg_path = output_dir / "regression_plot.png"
        plot_regression_with_ci(
            paired_results["deviations_mm"],
            paired_results["scores"],
            paired_results.get("stats", {}),
            reg_path,
        )
        plot_paths["regression"] = reg_path
        print(f"  Saved: {reg_path}")

        # Build scores grouped by CT severity for boxplot
        scores_by_cat = {}
        for d in paired_results.get("results", []):
            if d.get("status") == "success":
                cat = d.get("ct_severity", "unknown")
                scores_by_cat.setdefault(cat, []).append(d["nosecheck_score"])

        box_path = output_dir / "score_boxplot.png"
        plot_score_boxplot(scores_by_cat, box_path)
        plot_paths["boxplot"] = box_path
        print(f"  Saved: {box_path}")

    if dist_results.get("ct_distribution"):
        dist_path = output_dir / "severity_distribution.png"
        nc_dist = dist_results.get("nosecheck_distribution", {})
        plot_severity_distribution(
            dist_results["ct_distribution"],
            nc_dist,
            dist_path,
        )
        plot_paths["distribution"] = dist_path
        print(f"  Saved: {dist_path}")

    # Generate HTML report
    report_path = output_dir / "validation_report.html"
    generate_html_report(summary, plot_paths, report_path,
                         ground_truth=ct_data, simulated=args.simulated)
    print(f"\n  Report: {report_path}")

    # Terminal summary
    print_terminal_summary(summary)


if __name__ == "__main__":
    main()
