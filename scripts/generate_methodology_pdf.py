#!/usr/bin/env python3
"""
Generate NoseCheck Methodology PDF document.
Run: python scripts/generate_methodology_pdf.py
Output: docs/NoseCheck_Methodology.pdf
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
    """Build the methodology PDF document."""
    project_root = Path(__file__).resolve().parent.parent
    output_path = project_root / "docs" / "NoseCheck_Methodology.pdf"
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
        Paragraph("NoseCheck Methodology", title_style),
        Paragraph(
            "Deviated Nasal Septum (DNS) Screening Tool — Technical Overview",
            body_style,
        ),
        Spacer(1, 0.3 * inch),
    ])

    # --- Overview ---
    story.extend([
        Paragraph("1. Overview", h2_style),
        Paragraph(
            "NoseCheck is a DNS (Deviated Nasal Septum) screening tool that combines "
            "computer vision analysis of smartphone photos with symptom assessment and "
            "calibration against known reference data.",
            body_style,
        ),
        Spacer(1, 0.2 * inch),
    ])

    # --- Visual Analysis Pipeline ---
    story.extend([
        Paragraph("2. Visual Analysis Pipeline", h2_style),
        Paragraph("2.1 Landmark Detection", h3_style),
        Paragraph(
            "Uses MediaPipe Face Landmarker to detect facial landmarks including "
            "nose tip, bridge, nostrils, and face edges.",
            body_style,
        ),
        Spacer(1, 0.15 * inch),
        Paragraph("2.2 Asymmetry Metrics (4 measurements)", h3_style),
    ])

    metrics_data = [
        ["Metric", "What it measures"],
        ["Lateral deviation", "Distance of nose tip from facial midline (normalized by face width)"],
        ["Septal angle", "Angle of bridge-to-tip line from vertical"],
        ["Nostril asymmetry", "Left vs right nostril width difference"],
        ["Bridge straightness", "Deviation of nasal bridge from midline"],
    ]
    t1 = Table(metrics_data, colWidths=[1.8 * inch, 4.2 * inch])
    t1.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4472C4")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 10),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
        ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#E7E6E6")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
    ]))
    story.extend([t1, Spacer(1, 0.2 * inch)])

    story.extend([
        Paragraph("2.3 Score Calculation", h3_style),
        Paragraph(
            "Raw metrics are normalized to 0–100 using scaling factors. A noise floor "
            "removes small values (e.g., &lt;1% face width, &lt;1°) to reduce landmark jitter. "
            "Weighted combination: Lateral deviation 40%, Septal angle 30%, Nostril asymmetry "
            "20%, Bridge straightness 10%. Final deviation score: 0–100.",
            body_style,
        ),
        Spacer(1, 0.15 * inch),
        Paragraph("2.4 Severity Classification Bands", h3_style),
    ])

    bands_data = [
        ["Score range", "Classification"],
        ["0–30", "Normal"],
        ["30–50", "Mild"],
        ["50–70", "Moderate"],
        ["70–100", "Severe"],
    ]
    t2 = Table(bands_data, colWidths=[1.5 * inch, 4.5 * inch])
    t2.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4472C4")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#D9E2F3")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
    ]))
    story.extend([t2, Spacer(1, 0.3 * inch)])

    # --- Symptom Questionnaire ---
    story.extend([
        Paragraph("3. Symptom Questionnaire", h2_style),
        Paragraph(
            "Self-reported symptoms (e.g., breathing difficulty, congestion) produce "
            "a symptom score (0–100).",
            body_style,
        ),
        Spacer(1, 0.2 * inch),
    ])

    # --- Adaptive Scoring ---
    story.extend([
        Paragraph("4. Adaptive Score Combination", h2_style),
        Paragraph(
            "Visual and symptom scores are combined with adaptive weights. Higher "
            "symptom severity increases the weight given to symptoms.",
            body_style,
        ),
        Spacer(1, 0.15 * inch),
    ])

    adaptive_data = [
        ["Symptom score", "Visual weight", "Symptom weight"],
        ["0–40", "65%", "35%"],
        ["40–60", "55%", "45%"],
        ["60–75", "45%", "55%"],
        ["75–100", "35%", "65%"],
    ]
    t3 = Table(adaptive_data, colWidths=[1.8 * inch, 2.2 * inch, 2.2 * inch])
    t3.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4472C4")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#D9E2F3")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
    ]))
    story.extend([t3, Spacer(1, 0.3 * inch)])

    # --- Calibration ---
    story.extend([
        Paragraph("5. Calibration &amp; Validation", h2_style),
        Paragraph("5.1 3D Model Calibration", h3_style),
        Paragraph(
            "3D-printed nasal models with known septal deviations (Straight, C-curve, "
            "S-curve) are photographed and analyzed. Scaling factors are tuned so scores "
            "align with known severities.",
            body_style,
        ),
        Spacer(1, 0.15 * inch),
        Paragraph("5.2 CT Validation", h3_style),
        Paragraph(
            "CT scans (e.g., TCIA, NasalSeg) provide ground-truth internal septal "
            "deviation in mm. Frontal views rendered from CT are analyzed by NoseCheck. "
            "Correlation (Pearson r, R²) between CT deviation and NoseCheck score is evaluated.",
            body_style,
        ),
        Spacer(1, 0.3 * inch),
    ])

    # --- Research Basis ---
    story.extend([
        Paragraph("6. Research Basis", h2_style),
        Paragraph(
            "• Perceptible threshold: ~4 mm nasal tip deviation is when deviation becomes noticeable.",
            body_style,
        ),
        Paragraph(
            "• Clinically negligible: Deviations below 2–3 mm are considered negligible.",
            body_style,
        ),
        Paragraph(
            "• Normal variation: ~32% of people without DNS have some facial asymmetry.",
            body_style,
        ),
        Spacer(1, 0.3 * inch),
    ])

    # --- Limitation ---
    story.extend([
        Paragraph("7. Important Limitation", h2_style),
        Paragraph(
            "External 2D measurements may not correlate strongly with internal septal "
            "deviation. C-curve and S-curve septums can have identical external appearance. "
            "Therefore: symptoms are crucial for DNS screening; the algorithm combines "
            "visual + symptom scores; the tool is a screening aid, not a diagnostic device.",
            body_style,
        ),
    ])

    doc.build(story)
    return output_path


if __name__ == "__main__":
    out = build_document()
    print(f"Generated: {out}")
