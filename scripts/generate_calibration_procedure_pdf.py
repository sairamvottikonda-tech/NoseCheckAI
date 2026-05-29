#!/usr/bin/env python3
"""
Generate 3D Model Calibration Procedure PDF document.
Run: python scripts/generate_calibration_procedure_pdf.py
Output: docs/3D_Model_Calibration_Procedure.pdf
"""

from pathlib import Path

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import (
        SimpleDocTemplate,
        Paragraph,
        Spacer,
        Table,
        TableStyle,
    )
except ImportError:
    print("Installing reportlab...")
    import subprocess
    import sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "reportlab"])
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import (
        SimpleDocTemplate,
        Paragraph,
        Spacer,
        Table,
        TableStyle,
    )


def build_document():
    """Build the 3D Model Calibration Procedure PDF document."""
    project_root = Path(__file__).resolve().parent.parent
    output_path = project_root / "docs" / "3D_Model_Calibration_Procedure.pdf"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    doc = SimpleDocTemplate(str(output_path), pagesize=A4)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        name="CustomTitle",
        parent=styles["Heading1"],
        fontSize=18,
        spaceAfter=12,
    )
    h2_style = ParagraphStyle(
        name="CustomH2",
        parent=styles["Heading2"],
        fontSize=14,
        spaceBefore=14,
        spaceAfter=8,
    )
    h3_style = ParagraphStyle(
        name="CustomH3",
        parent=styles["Heading3"],
        fontSize=12,
        spaceBefore=10,
        spaceAfter=6,
    )
    body_style = styles["Normal"]

    story = []

    # --- Title ---
    story.extend([
        Paragraph("3D Model Calibration Procedure", title_style),
        Paragraph(
            "Step-by-step guide for calibrating NoseCheck using 3D-printed nasal models "
            "with known septal deviations.",
            body_style,
        ),
        Spacer(1, 0.3 * inch),
    ])

    # --- Overview ---
    story.extend([
        Paragraph("1. Overview", h2_style),
        Paragraph(
            "This procedure uses 3D-printed nasal models with known internal septal "
            "deviations to validate and tune the NoseCheck algorithm. By comparing "
            "NoseCheck's output against known ground truth, you can measure accuracy "
            "and adjust scaling factors.",
            body_style,
        ),
        Spacer(1, 0.2 * inch),
    ])

    # --- Phase 1: Model Preparation ---
    story.extend([
        Paragraph("2. Phase 1: Model Preparation", h2_style),
        Paragraph("Model types and target scores:", h3_style),
    ])

    model_data = [
        ["Septum Type", "Deviation (mm)", "Target Score", "Target Class"],
        ["Straight", "0", "0–25", "Normal"],
        ["C-curve (mild)", "2–4", "25–50", "Mild"],
        ["C-curve (moderate)", "4–6", "40–65", "Moderate"],
        ["S-curve (severe)", "6–10", "55–85", "Severe"],
    ]
    t1 = Table(model_data, colWidths=[1.5 * inch, 1.3 * inch, 1.4 * inch, 1.5 * inch])
    t1.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4472C4")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 9),
        ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#E7E6E6")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
    ]))
    story.extend([t1, Spacer(1, 0.15 * inch)])

    story.extend([
        Paragraph("Print settings (FDM): Layer height 0.2 mm, infill 20%, supports for nostril overhangs.", body_style),
        Spacer(1, 0.2 * inch),
    ])

    # --- Phase 2: Photography ---
    story.extend([
        Paragraph("3. Phase 2: Photography", h2_style),
        Paragraph(
            "Setup: Smartphone on tripod 50–70 cm from model; 2–3 soft lights; neutral background. "
            "For each model: position at eye level, frontal view, capture 3–5 photos. "
            "Use consistent naming: straight_0mm_001.jpg, c_curve_2mm_001.jpg, s_curve_8mm_001.jpg.",
            body_style,
        ),
        Spacer(1, 0.2 * inch),
    ])

    # --- Phase 3: metadata.csv ---
    story.extend([
        Paragraph("4. Phase 3: Edit metadata.csv", h2_style),
        Paragraph(
            "Place photos in data/calibration_models/ and add one row per photo to "
            "data/calibration_models/metadata.csv.",
            body_style,
        ),
        Spacer(1, 0.15 * inch),
        Paragraph("Column reference:", h3_style),
    ])

    col_data = [
        ["Column", "Description", "Example"],
        ["filename", "Exact photo filename", "straight_0mm_001.jpg"],
        ["known_deviation_mm", "Known deviation (mm)", "0, 2, 5, 8"],
        ["model_type", "3d_model or clinical", "3d_model"],
        ["septum_shape", "straight, c_curve, s_curve", "straight"],
        ["expected_classification", "Expected severity", "normal, mild, moderate, severe"],
        ["expected_score_min", "Min acceptable score", "0"],
        ["expected_score_max", "Max acceptable score", "25"],
    ]
    t2 = Table(col_data, colWidths=[1.8 * inch, 2.2 * inch, 2.2 * inch])
    t2.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4472C4")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#D9E2F3")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
    ]))
    story.extend([t2, Spacer(1, 0.2 * inch)])

    # --- Phase 4: Calibration Workflow ---
    story.extend([
        Paragraph("5. Phase 4: Run Calibration Workflow", h2_style),
        Paragraph("Commands:", h3_style),
        Paragraph(
            "cd /path/to/nosecheck<br/>"
            "source venv/bin/activate<br/>"
            "python scripts/calibration_workflow.py",
            body_style,
        ),
        Paragraph(
            "This loads each photo, runs NoseCheck, compares score to expected range, "
            "and writes results to calibration_results.csv.",
            body_style,
        ),
        Spacer(1, 0.2 * inch),
    ])

    # --- Phase 5: Validation ---
    story.extend([
        Paragraph("6. Phase 5: Run Validation", h2_style),
        Paragraph("python scripts/validate_calibration.py", body_style),
        Paragraph(
            "Reports: R² (correlation), score range accuracy, category accuracy, "
            "per-category accuracy. Target: R² ≥ 0.75, category accuracy ≥ 80%.",
            body_style,
        ),
        Spacer(1, 0.2 * inch),
    ])

    # --- Phase 6: Tuning ---
    story.extend([
        Paragraph("7. Phase 6: Tune If Needed", h2_style),
        Paragraph(
            "If R² &lt; 0.75, adjust scaling_factors in config.py. "
            "Scores too low → increase factors. Scores too high → decrease factors. "
            "Re-run calibration and validation after each change.",
            body_style,
        ),
        Spacer(1, 0.2 * inch),
    ])

    # --- Quick Reference ---
    story.extend([
        Paragraph("8. Quick Reference", h2_style),
    ])

    quick_data = [
        ["Step", "Action"],
        ["1", "Place photos in data/calibration_models/"],
        ["2", "Edit metadata.csv (one row per photo)"],
        ["3", "python scripts/calibration_workflow.py"],
        ["4", "python scripts/validate_calibration.py"],
        ["5", "If needed, tune config.py and repeat 3–4"],
    ]
    t3 = Table(quick_data, colWidths=[0.6 * inch, 5.4 * inch])
    t3.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4472C4")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#E7E6E6")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
    ]))
    story.extend([t3, Spacer(1, 0.2 * inch)])

    # --- Troubleshooting ---
    story.extend([
        Paragraph("9. Troubleshooting", h2_style),
        Paragraph(
            "• No face detected on 3D models: Paint eyes/eyebrows or use real-face photos.<br/>"
            "• All score Normal: Increase lateral_deviation and septal_angle in config.py.<br/>"
            "• Straight scores Severe: Decrease all scaling factors by ~50%.<br/>"
            "• No correlation: External appearance may not reflect internal deviation.",
            body_style,
        ),
        Spacer(1, 0.2 * inch),
    ])

    # --- Important Note ---
    story.extend([
        Paragraph("10. Important Note", h2_style),
        Paragraph(
            "External 2D measurements may not correlate strongly with internal septal deviation. "
            "NoseCheck is a screening aid, not a diagnostic device. Symptoms are crucial for DNS screening.",
            body_style,
        ),
    ])

    doc.build(story)
    return output_path


if __name__ == "__main__":
    out = build_document()
    print(f"Generated: {out}")
