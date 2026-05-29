"""
Visualization utilities for NoseCheck analysis.

Generates plots for validation and calibration.
"""

import sys
from pathlib import Path
from typing import Dict, List, Optional, Union

import cv2
import numpy as np

_project_root = Path(__file__).resolve().parent.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))


def visualize_landmarks(
    image: np.ndarray,
    landmarks: Dict[str, tuple],
    output_path: Optional[Union[str, Path]] = None,
) -> np.ndarray:
    """
    Draw nasal landmarks and facial midline on image for debugging.

    Args:
        image: BGR image (e.g., from cv2.imread).
        landmarks: Dict from detector.detect_landmarks().
        output_path: If provided, save annotated image here.

    Returns:
        Annotated image as numpy array.
    """
    img = image.copy()
    h, w = img.shape[:2]

    left = landmarks.get("left_face_edge")
    right = landmarks.get("right_face_edge")
    if left and right:
        mid_x = int((left[0] + right[0]) / 2)
        cv2.line(img, (mid_x, 0), (mid_x, h), (0, 255, 255), 2)

    colors = {
        "nose_tip": (0, 255, 0),
        "nose_bridge": (255, 0, 0),
        "left_nostril_outer": (255, 255, 0),
        "left_nostril_inner": (255, 255, 0),
        "right_nostril_outer": (0, 255, 255),
        "right_nostril_inner": (0, 255, 255),
        "left_face_edge": (128, 128, 128),
        "right_face_edge": (128, 128, 128),
    }
    for name, pt in landmarks.items():
        x, y = int(pt[0]), int(pt[1])
        color = colors.get(name, (255, 255, 255))
        cv2.circle(img, (x, y), 5, color, 2)
        cv2.putText(img, name, (x + 8, y), cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)

    if "nose_bridge" in landmarks and "nose_tip" in landmarks:
        pt1 = (int(landmarks["nose_bridge"][0]), int(landmarks["nose_bridge"][1]))
        pt2 = (int(landmarks["nose_tip"][0]), int(landmarks["nose_tip"][1]))
        cv2.line(img, pt1, pt2, (255, 0, 255), 2)

    if output_path:
        cv2.imwrite(str(output_path), img)
    return img


def plot_deviation_vs_score(
    known_deviations: List[float],
    calculated_scores: List[float],
    output_path: Union[str, Path],
):
    """
    Plot physical deviation (mm) vs calculated score.
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.scatter(known_deviations, calculated_scores, s=80, alpha=0.8)

    if len(known_deviations) >= 2:
        z = np.polyfit(known_deviations, calculated_scores, 1)
        p = np.poly1d(z)
        x_line = np.linspace(min(known_deviations), max(known_deviations), 100)
        ax.plot(x_line, p(x_line), "r--", alpha=0.7, label="Fit")

    ax.set_xlabel("Known physical deviation (mm)")
    ax.set_ylabel("Calculated deviation score")
    ax.set_title("Calibration: Physical Deviation vs Calculated Score")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)


def save_validation_report(
    results: List[dict],
    r_squared: float,
    rmse: float,
    output_path: Union[str, Path],
):
    """Save a text validation report."""
    lines = [
        "NoseCheck Calibration Validation Report",
        "=" * 50,
        "",
        f"r-squared (correlation): {r_squared:.4f}",
        f"RMSE: {rmse:.2f}",
        "",
        "Per-model results:",
        "-" * 40,
    ]
    for r in results:
        lines.append(
            f"  {r.get('filename', '?')}: known={r.get('known_deviation_mm')}mm, "
            f"score={r.get('deviation_score')}, class={r.get('classification')}"
        )
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


# --- CT Validation plots ---

SEVERITY_COLORS = {
    "normal": "#4CAF50",
    "mild": "#FFC107",
    "moderate": "#FF9800",
    "severe": "#F44336",
}


def plot_severity_distribution(
    ct_counts: Dict[str, int],
    nc_counts: Dict[str, int],
    output_path: Union[str, Path],
):
    """
    Side-by-side bar chart comparing severity distributions
    from CT data vs NoseCheck classifications.
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    categories = ["mild", "moderate", "severe"]
    ct_vals = [ct_counts.get(c, 0) for c in categories]
    nc_vals = [nc_counts.get(c, 0) for c in categories]

    x = np.arange(len(categories))
    width = 0.35

    fig, ax = plt.subplots(figsize=(8, 5))
    bars1 = ax.bar(x - width / 2, ct_vals, width, label="CT Ground Truth",
                   color="#5C6BC0", alpha=0.85)
    bars2 = ax.bar(x + width / 2, nc_vals, width, label="NoseCheck",
                   color="#26A69A", alpha=0.85)

    ax.set_xlabel("Severity Category")
    ax.set_ylabel("Count")
    ax.set_title("Severity Distribution: CT vs NoseCheck")
    ax.set_xticks(x)
    ax.set_xticklabels([c.capitalize() for c in categories])
    ax.legend()
    ax.grid(True, alpha=0.2, axis="y")

    for bar in bars1:
        h = bar.get_height()
        if h > 0:
            ax.text(bar.get_x() + bar.get_width() / 2, h + 0.2,
                    str(int(h)), ha="center", va="bottom", fontsize=10)
    for bar in bars2:
        h = bar.get_height()
        if h > 0:
            ax.text(bar.get_x() + bar.get_width() / 2, h + 0.2,
                    str(int(h)), ha="center", va="bottom", fontsize=10)

    fig.tight_layout()
    fig.savefig(str(output_path), dpi=150)
    plt.close(fig)


def plot_score_boxplot(
    scores_by_category: Dict[str, List[float]],
    output_path: Union[str, Path],
):
    """
    Box plot of NoseCheck scores grouped by CT severity category.
    Shows whether score ranges separate cleanly by category.
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    categories = ["mild", "moderate", "severe"]
    data = [scores_by_category.get(c, []) for c in categories]
    data = [d if d else [0] for d in data]

    fig, ax = plt.subplots(figsize=(8, 5))
    bp = ax.boxplot(data, labels=[c.capitalize() for c in categories],
                    patch_artist=True, widths=0.5)

    colors = [SEVERITY_COLORS.get(c, "#999") for c in categories]
    for patch, color in zip(bp["boxes"], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.6)

    ax.set_xlabel("CT Severity Category")
    ax.set_ylabel("NoseCheck Deviation Score (0-100)")
    ax.set_title("NoseCheck Score Distribution by CT Severity")
    ax.set_ylim(-5, 105)
    ax.grid(True, alpha=0.2, axis="y")

    fig.tight_layout()
    fig.savefig(str(output_path), dpi=150)
    plt.close(fig)


def plot_regression_with_ci(
    x: List[float],
    y: List[float],
    stats: Dict[str, float],
    output_path: Union[str, Path],
):
    """
    Scatter plot with regression line, R-squared annotation,
    and shaded 95% prediction interval.
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    fig, ax = plt.subplots(figsize=(8, 6))

    ax.scatter(x, y, s=80, alpha=0.8, zorder=5, edgecolors="white", linewidths=0.5)

    if len(x) >= 2:
        slope = stats.get("slope", 0)
        intercept = stats.get("intercept", 0)
        r_sq = stats.get("r_squared", 0)
        r_val = stats.get("pearson_r", stats.get("r", 0))

        x_arr = np.array(x)
        y_arr = np.array(y)
        x_line = np.linspace(min(x) - 0.5, max(x) + 0.5, 200)
        y_line = slope * x_line + intercept

        ax.plot(x_line, y_line, "r-", linewidth=2, alpha=0.8,
                label=f"y = {slope:.2f}x + {intercept:.2f}")

        # 95% prediction interval
        y_pred = slope * x_arr + intercept
        residuals = y_arr - y_pred
        se = np.sqrt(np.sum(residuals ** 2) / max(1, len(x) - 2))
        n = len(x)
        x_mean = np.mean(x_arr)
        ss_xx = np.sum((x_arr - x_mean) ** 2)

        if ss_xx > 0:
            margin = 1.96 * se * np.sqrt(1 + 1 / n + (x_line - x_mean) ** 2 / ss_xx)
            ax.fill_between(x_line, y_line - margin, y_line + margin,
                            alpha=0.15, color="red", label="95% prediction interval")

        eq_text = f"R = {r_val:.3f}\nR$^2$ = {r_sq:.3f}"
        p_val = stats.get("p_value", None)
        if p_val is not None:
            if p_val < 0.001:
                eq_text += "\np < 0.001"
            else:
                eq_text += f"\np = {p_val:.3f}"
        ax.text(0.05, 0.95, eq_text, transform=ax.transAxes,
                verticalalignment="top", fontsize=11,
                bbox=dict(boxstyle="round,pad=0.4", facecolor="wheat", alpha=0.8))

    ax.set_xlabel("CT Septal Deviation (mm)", fontsize=12)
    ax.set_ylabel("NoseCheck Deviation Score (0-100)", fontsize=12)
    ax.set_title("CT Deviation vs NoseCheck Score", fontsize=14)
    ax.legend(loc="lower right")
    ax.grid(True, alpha=0.2)
    ax.set_ylim(-5, 105)

    fig.tight_layout()
    fig.savefig(str(output_path), dpi=150)
    plt.close(fig)


# --- Plan-specified aliases ---

def plot_severity_comparison(
    results: List[dict],
    output_path: Union[str, Path],
):
    """
    Grouped bar chart: CT severity vs NoseCheck classification for each patient.

    Accepts a list of per-patient result dicts (from run_paired_validation)
    and generates a grouped bar chart showing agreement/disagreement.
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    successful = [r for r in results if r.get("status") == "success"]
    if not successful:
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.text(0.5, 0.5, "No paired data available", ha="center", va="center",
                fontsize=14, transform=ax.transAxes)
        ax.set_title("Severity Comparison: CT vs NoseCheck")
        fig.tight_layout()
        fig.savefig(str(output_path), dpi=150)
        plt.close(fig)
        return

    categories = ["mild", "moderate", "severe"]
    cat_to_num = {"normal": 0, "mild": 1, "moderate": 2, "severe": 3}

    patients = [r.get("patient_id", f"P{i}") for i, r in enumerate(successful)]
    ct_vals = [cat_to_num.get(r.get("ct_severity", ""), 0) for r in successful]
    nc_vals = [cat_to_num.get(r.get("nosecheck_severity", ""), 0) for r in successful]

    x = np.arange(len(patients))
    width = 0.35

    fig, ax = plt.subplots(figsize=(max(8, len(patients) * 1.2), 5))
    bars1 = ax.bar(x - width / 2, ct_vals, width, label="CT Severity",
                   color="#5C6BC0", alpha=0.85)
    bars2 = ax.bar(x + width / 2, nc_vals, width, label="NoseCheck",
                   color="#26A69A", alpha=0.85)

    for i, (cv, nv) in enumerate(zip(ct_vals, nc_vals)):
        if cv != nv:
            ax.plot(i, max(cv, nv) + 0.3, "r*", markersize=10)

    ax.set_xlabel("Patient")
    ax.set_ylabel("Severity Level")
    ax.set_title("Severity Comparison: CT vs NoseCheck")
    ax.set_xticks(x)
    ax.set_xticklabels(patients, rotation=45 if len(patients) > 8 else 0, ha="right")
    ax.set_yticks([0, 1, 2, 3])
    ax.set_yticklabels(["Normal", "Mild", "Moderate", "Severe"])
    ax.legend()
    ax.grid(True, alpha=0.2, axis="y")

    fig.tight_layout()
    fig.savefig(str(output_path), dpi=150)
    plt.close(fig)


def plot_score_distribution(
    results: List[dict],
    output_path: Union[str, Path],
):
    """
    Box plot of NoseCheck scores grouped by CT severity category.

    Accepts per-patient result dicts and groups them by ct_severity.
    Wrapper around plot_score_boxplot with a results-based interface.
    """
    scores_by_cat = {}
    for r in results:
        if r.get("status") != "success":
            continue
        cat = r.get("ct_severity", "unknown")
        scores_by_cat.setdefault(cat, []).append(r.get("nosecheck_score", 0))

    plot_score_boxplot(scores_by_cat, output_path)
