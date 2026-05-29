#!/usr/bin/env python3
"""
Generate CT Scan Validation Procedure PDF document.
Run: python scripts/generate_ct_validation_pdf.py
Output: docs/CT_Scan_Validation_Procedure.pdf
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
    """Build the CT Scan Validation Procedure PDF document."""
    project_root = Path(__file__).resolve().parent.parent
    output_path = project_root / "docs" / "CT_Scan_Validation_Procedure.pdf"
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
        Paragraph("CT Scan Validation Procedure", title_style),
        Paragraph(
            "Step-by-step guide for validating NoseCheck against CT scan ground truth.",
            body_style,
        ),
        Spacer(1, 0.3 * inch),
    ])

    # --- Overview ---
    story.extend([
        Paragraph("1. Overview", h2_style),
        Paragraph(
            "This procedure validates whether NoseCheck's photo-based scoring correlates "
            "with internal septal deviation measured on CT scans. Paired validation: CT + "
            "frontal photo for same patient. Distribution validation: CT-only entries. "
            "Target: Pearson r &gt; 0.6, R² &gt; 0.4.",
            body_style,
        ),
        Spacer(1, 0.2 * inch),
    ])

    # --- Phase 1: Download CT ---
    story.extend([
        Paragraph("2. Phase 1: Download CT Scan Datasets", h2_style),
    ])

    dataset_data = [
        ["Dataset", "Content"],
        ["TCIA Head-Neck Cetuximab", "Head/neck CT with nasal structures"],
        ["NasalSeg (Zenodo)", "130 annotated nasal CT scans"],
        ["Mendeley Right Nasal Cavity", "Nasal cavity meshes"],
    ]
    t1 = Table(dataset_data, colWidths=[2.2 * inch, 3.8 * inch])
    t1.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4472C4")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#E7E6E6")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
    ]))
    story.extend([t1, Spacer(1, 0.15 * inch)])

    story.extend([
        Paragraph(
            "TCIA: Install NBIA Data Retriever, search Head-Neck-Cetuximab, download 10–20 patients. "
            "Save outside git repo.",
            body_style,
        ),
        Spacer(1, 0.2 * inch),
    ])

    # --- Phase 2 & 3: 3D Slicer ---
    story.extend([
        Paragraph("3. Phase 2–3: Install 3D Slicer and Load CT", h2_style),
        Paragraph(
            "Download from slicer.org. Load DICOM: File &gt; Add Data or drag folder. "
            "Use DICOM module, load CT series, switch to Axial View.",
            body_style,
        ),
        Spacer(1, 0.2 * inch),
    ])

    # --- Phase 4: Measure Septal Deviation ---
    story.extend([
        Paragraph("4. Phase 4: Measure Septal Deviation", h2_style),
        Paragraph(
            "1) Find nasal septum in axial slices. 2) Identify ANS and crista galli. "
            "3) Draw midline (Ruler tool) from ANS to crista galli. 4) Find slice where "
            "septum deviates most; measure horizontal distance (mm) to max displacement. "
            "5) Record slice number and deviation.",
            body_style,
        ),
        Spacer(1, 0.15 * inch),
        Paragraph("Severity: 0–2 mm = Mild; 2–5 mm = Moderate; 5+ mm = Severe", body_style),
        Spacer(1, 0.2 * inch),
    ])

    # --- Phase 5: Render Frontal View ---
    story.extend([
        Paragraph("5. Phase 5: Render Frontal Face View", h2_style),
        Paragraph(
            "Volume Rendering module, preset CT-Skin. Rotate to frontal view, center nose. "
            "File &gt; Save Screenshot. Save PNG in data/ct_validation/, name as P1_frontal.png.",
            body_style,
        ),
        Spacer(1, 0.2 * inch),
    ])

    # --- Phase 6: ct_ground_truth.csv ---
    story.extend([
        Paragraph("6. Phase 6: Edit ct_ground_truth.csv", h2_style),
        Paragraph("Key columns: patient_id, ct_source, max_deviation_mm, septum_shape, severity_ct, photo_filename, slice_number, notes.", body_style),
        Paragraph(
            "Fill photo_filename for paired validation; leave empty for CT-only.",
            body_style,
        ),
        Spacer(1, 0.2 * inch),
    ])

    # --- Phase 7: Run Validation ---
    story.extend([
        Paragraph("7. Phase 7: Run Validation", h2_style),
        Paragraph(
            "source venv/bin/activate<br/>"
            "python scripts/validate_ct_correlation.py",
            body_style,
        ),
        Paragraph(
            "Optional: --csv /path/to/custom.csv",
            body_style,
        ),
        Spacer(1, 0.2 * inch),
    ])

    # --- Phase 8: Output ---
    story.extend([
        Paragraph("8. Phase 8: Review Output", h2_style),
        Paragraph(
            "Terminal: Pearson r, R², RMSE, category accuracy. Plots: regression_plot.png, "
            "score_boxplot.png, severity_distribution.png. HTML: validation_report.html. "
            "Web: /validation route.",
            body_style,
        ),
        Spacer(1, 0.15 * inch),
        Paragraph("Interpretation:", h3_style),
    ])

    interp_data = [
        ["Metric", "Good", "Acceptable", "Poor"],
        ["Pearson r", "> 0.8", "0.6–0.8", "< 0.6"],
        ["R²", "> 0.6", "0.4–0.6", "< 0.4"],
        ["RMSE", "< 10", "10–20", "> 20"],
        ["Category Accuracy", "> 80%", "60–80%", "< 60%"],
    ]
    t2 = Table(interp_data, colWidths=[1.5 * inch, 1.3 * inch, 1.3 * inch, 1.1 * inch])
    t2.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4472C4")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#D9E2F3")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
    ]))
    story.extend([t2, Spacer(1, 0.2 * inch)])

    # --- Quick Reference ---
    story.extend([
        Paragraph("9. Quick Reference", h2_style),
    ])

    quick_data = [
        ["Step", "Action"],
        ["1", "Download CT data (TCIA, NasalSeg)"],
        ["2", "Install 3D Slicer"],
        ["3", "Load CT, measure septal deviation (mm)"],
        ["4", "Render frontal view, save PNG in data/ct_validation/"],
        ["5", "Edit data/ct_validation/ct_ground_truth.csv"],
        ["6", "python scripts/validate_ct_correlation.py"],
        ["7", "Review terminal, plots, HTML report"],
    ]
    t3 = Table(quick_data, colWidths=[0.5 * inch, 5.5 * inch])
    t3.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4472C4")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#E7E6E6")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
    ]))
    story.extend([t3, Spacer(1, 0.2 * inch)])

    # --- Ethics ---
    story.extend([
        Paragraph("10. Ethics and Citations", h2_style),
        Paragraph(
            "Datasets are de-identified and public; no IRB required. Cite TCIA, NasalSeg, "
            "and Mendeley as appropriate. See docs/CT_VALIDATION_GUIDE.md for full citations.",
            body_style,
        ),
    ])

    doc.build(story)
    return output_path


if __name__ == "__main__":
    out = build_document()
    print(f"Generated: {out}")
