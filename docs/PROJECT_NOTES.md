# NoseCheck Project Notes

## Research Objectives

The NoseCheck project aims to develop an accessible screening tool for detecting Deviated Nasal Septum (DNS) using:

1. Smartphone-captured photographs
2. Automated computer vision analysis
3. Self-reported symptom assessment

## Target Users

- Adolescents and young adults for health awareness
- Researchers studying DNS prevalence
- Educational institutions for health screening programs

## Key Research Questions

1. Can smartphone photos reliably detect nasal asymmetry?
2. What correlation exists between visual measurements and known deviations?
3. How repeatable are the measurements across multiple photos?
4. Can the system accurately classify severity levels?
5. How well do visual measurements correlate with self-reported symptoms?

## Methodology

### Phase 1: Calibration
- Create 3D models with known deviations (0mm, 2mm, 5mm, 10mm)
- 3D print models with realistic nose features
- Capture standardized photographs
- Process through detection pipeline
- Calibrate scoring weights

### Phase 2: Validation
- Test repeatability with multiple photos per model
- Validate correlation between known and calculated deviations
- Assess inter-observer reliability (if applicable)
- Calculate accuracy metrics

### Phase 3: Symptom Integration
- Develop symptom questionnaire
- Collect symptom data alongside visual measurements
- Analyze correlation between visual scores and symptoms
- Develop combined screening algorithm

### Phase 4: Real-World Testing (Future)
- Pilot study with volunteers
- Clinical validation (with appropriate ethical approval)
- Comparison with medical imaging (if available)

## Expected Outcomes

### Quantitative Metrics
- Correlation coefficient (r²) > 0.80 between known and calculated deviations
- Coefficient of variation (CV) < 10% for repeated measurements
- Classification accuracy > 85% for severity categories

### Deliverables
- Working software system
- Calibration dataset and parameters
- Statistical analysis and validation results
- Research paper/report with findings
- Educational tool for health awareness

## Technical Considerations

### Image Quality Requirements
- Minimum resolution: 1920x1080 pixels
- Frontal face view with nose fully visible
- Adequate lighting (no harsh shadows)
- Neutral facial expression
- Distance calibration using reference marker

### Landmark Detection Accuracy
- MediaPipe Face Mesh: 468 landmarks, including detailed nasal region
- Target accuracy: < 2mm error in landmark positioning
- Confidence threshold: > 0.9 for reliable detection

### Measurement Precision
- Sub-millimeter precision for lateral deviation
- < 1 degree precision for septal angle
- < 5% error for nostril area ratios

## Limitations and Future Work

### Current Limitations
- Smartphone-based system (not medical-grade imaging)
- 2D analysis from single frontal photo
- Requires good lighting and clear image quality
- Cannot detect internal septal deviations

### Future Enhancements
- Multi-angle photo analysis (frontal + profile views)
- 3D reconstruction from multiple images
- Machine learning classification model
- Integration with symptom severity prediction
- Mobile app development
- Clinical validation study

## Ethical Considerations

- Research use only (not for clinical diagnosis)
- Appropriate consent for any human subjects
- Data privacy and security
- Clear communication about limitations
- Medical disclaimer included in all materials

## Timeline Considerations

This document tracks progress but avoids specific timelines. Tasks should be completed sequentially based on logical dependencies.

## References

[To be added: relevant research papers, MediaPipe documentation, etc.]
