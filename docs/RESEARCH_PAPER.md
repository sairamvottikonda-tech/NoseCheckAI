# What a Frontal Photograph Can and Cannot Reveal About Nasal Deviation

### A Measurement-Validation Study of Fourteen Computer Vision Approaches

**Sairam Vottikonda**
*In collaboration with Alexander Markarian, M.D., Facial Plastic Surgery, USC*

Code: [github.com/sairamvottikonda-tech/NoseCheckAI](https://github.com/sairamvottikonda-tech/NoseCheckAI) · App: [nosecheckai-v2.onrender.com](https://nosecheckai-v2.onrender.com)

---

## Abstract

**Background.** Nasal obstruction often goes unrecognized because patients normalize symptoms or face barriers to specialty care. This study investigates whether computer vision measurements from standardized facial photographs correlate with physician assessments of nasal deviation, exploring the feasibility of an accessible screening tool.

**Objective.** Rather than reporting a single algorithm, we set out to determine what quantity, if any, is recoverable from a frontal photograph, and to characterize its precision, its failure modes, and its confounds.

**Methods.** Fourteen candidate measurements were implemented and evaluated against surgeon-assigned severity grades for 35 photographs. Candidates spanned sparse landmark geometry, dorsal contour curvature, left–right mirror comparison at both landmark and pixel level, shadow-intensity asymmetry, spectral and gradient-histogram descriptors, and direct localisation of the nasal ridge from image intensity. Each was assessed by Spearman rank correlation with clinical grade, then screened by permutation testing, outlier removal, partial correlation controlling for head pose, and image-space augmentation. Within-subject measurement precision was established independently from five repeated photographs of one individual before any clinical comparison was made.

**Results.** One measurement survived: the maximum perpendicular offset of the nasal dorsum from a midline defined by the inner canthi and the philtrum, normalised by interocular distance (ρ = +0.609, p = 0.0001, n = 35; leave-one-out ρ = +0.486, p = 0.003). Severe versus non-severe classification reached 86% accuracy, with sensitivity 56% and specificity 96%; under a 2° head-yaw gate specificity reached 100%. Four-class agreement with clinical grading was at chance across nine classifier families. Within-subject precision was ±0.0016 normalised units, approximately 8 points on a 0–100 scale. Thirteen alternative measurements returned p > 0.5 or proved statistically redundant. A capture-geometry confound was identified: the ratio of facial width to interocular distance predicted clinical grade at ρ = +0.577.

**Conclusions.** External dorsal position measured from a frontal photograph ranks nasal deviation severity with moderate reliability and high specificity, but resolves only severe from non-severe cases and misses approximately half of clinically severe presentations. Four-level clinical grading is not recoverable from frontal photographic geometry. We report the negative results in full, since the pattern across fourteen independent approaches constrains what future photographic methods can be expected to achieve.

**Keywords:** nasal septal deviation, nasal obstruction, computer vision, facial landmark detection, screening, measurement validation, negative results

---

## 1. Introduction

Nasal obstruction often goes unrecognized because patients normalize symptoms or face barriers to specialty care. Symptoms present since childhood are frequently not experienced as symptoms at all, and access to otolaryngology or facial plastic surgery is constrained by geography, cost and appointment availability. The result is a population in which a common, treatable condition goes undiagnosed until quality of life is substantially impaired.

Nasal septal deviation (NSD) is among the most prevalent anatomical variations in otolaryngology, with estimates that 70–80% of the general population exhibits some degree of deviation, most of it subclinical. Among symptomatic individuals it presents as unilateral obstruction, exertional breathing difficulty, sleep disturbance and recurrent sinusitis. Patients commonly normalise these symptoms over years.

Diagnosis presently requires in-person examination. A screening tool that could be used without specialist access — flagging individuals who warrant formal evaluation — would address a real gap, provided its limitations were stated accurately enough that a negative result was not mistaken for reassurance.

Smartphone photography and on-device facial landmark detection make such a tool technically plausible. Google's MediaPipe Face Landmarker detects 478 facial landmarks in real time on consumer hardware, including multiple nasal reference points. Whether those points encode clinically meaningful information about nasal deviation is a separate and open question, and it is the question this study addresses.

### 1.1 What this study contributes

This paper differs from the typical structure of an applied computer vision report in three respects, each deliberate.

First, it is framed as a measurement-validation study rather than a system description. We do not report one algorithm and its accuracy. We report fourteen candidate measurements, of which thirteen failed, and treat the pattern of failure as the primary result.

Second, measurement precision was established before any clinical comparison. Five photographs of one subject, taken minutes apart, define a noise floor against which every subsequent correlation is interpreted. Several candidate measurements that appeared promising were discarded because within-subject variation exceeded between-grade variation.

Third, we report a confound we could not fully resolve. The ratio of facial width to interocular distance, a proxy for camera geometry with no anatomical relationship to the septum, predicts clinical grade in our sample nearly as strongly as the retained measurement. We describe this in full rather than omitting it.

### 1.2 Research question and hypothesis

**Research question:** Do computer vision measurements of external nasal asymmetry, derived from standard frontal photographs, correlate with surgeon assessments of nasal deviation severity, and with what precision and reliability?

**Hypothesis:** A geometric measurement of external nasal asymmetry will correlate positively with surgeon-assessed severity, with the correlation strongest for centreline displacement and degraded by head rotation, photographic capture geometry, and the limited relationship between external appearance and internal septal anatomy.

---

## 2. Background and Related Work

### 2.1 Objective measurement of septal deviation

Quantitative assessment of NSD has been studied predominantly in computed tomography. 2D CT measurements — maximum deviation and deviation area — have been shown to be most predictive of 3D nasal cavity asymmetry from volumetric segmentation. NSD-Net, the first automated NSD assessment framework, was trained on a 500-scan CT dataset with expert annotation. These approaches achieve high precision but require radiology infrastructure and are unsuited to population screening.

The clinical grading standard (Elahi et al.) defines severity by the angle between a line through the crista galli and nasal crest of the maxilla and a line to the point of maximum septal deflection, measured on coronal CT: mild below 9°, moderate 9–15°, severe above 15°. Every landmark in this construction lies inside the skull — a material constraint on any photographic method.

### 2.2 Photographic analysis of nasal appearance

Two-dimensional photographic analysis has been developed chiefly for rhinoplasty outcome assessment. Crooked-nose outcome studies report a nasion–tip–lip deviation angle averaging 6.84° pre-operatively and 2.01° post-operatively, and classify external deviation as I-, C- or S-shaped, with roughly 70% of cases being C-type.

Siamese architectures comparing mirrored facial halves have reported up to 97% accuracy for binary symmetric-versus-asymmetric classification of general facial asymmetry, trained on 1,200 expert-labelled photographs. That work reported reduced performance from landmark-based directional analysis, attributing it to landmark placement error in lateral and chin regions.

A lightweight deep learning pipeline for automatic apparent nasal index from single photographs achieved 80.7% accuracy on five-category nasal shape classification, trained on approximately 30,000 CelebA images, and explicitly identifies asymmetry detection as unaddressed future work.

### 2.3 The gap

No published work, to our knowledge, evaluates a photographic computer vision method for nasal deviation screening against surgeon-assigned clinical grades. Existing photographic work addresses either aesthetic outcome measurement in already-diagnosed surgical patients, or coarse shape categorisation unrelated to deviation. Existing NSD work is CT-based. The specific question of what a frontal photograph can contribute to identifying nasal deviation in an unselected population has not been examined.

---

## 3. Methods

### 3.1 System architecture

NoseCheckAI is a Python Flask application deployed on a cloud server and accessible from any browser, including mobile. A user uploads a frontal photograph and optionally completes a symptom questionnaire. Source code is publicly available at the repository linked above.

### 3.2 Image preprocessing

Uploaded images undergo EXIF orientation correction; channel normalisation, converting grayscale to three-channel BGR and stripping alpha from RGBA inputs; and aspect-ratio-preserving resize with letterboxing to a 640×480 frame.

The letterboxing step is not cosmetic. An earlier implementation force-resized to a fixed frame, introducing up to 2.4× horizontal distortion on portrait-format photographs and directly corrupting every horizontal-distance measurement. This class of preprocessing error is silent — it produces plausible numbers — and is likely to affect other image-based measurement tools that do not document their resize behaviour.

### 3.3 Landmark detection

Landmark detection uses MediaPipe Face Landmarker (`face_landmarker.task`, float16), configured with `num_faces=1`, static image mode, and minimum detection confidence 0.5. The model returns 478 landmarks; twenty relevant to nasal geometry are extracted, together with the 4×4 facial transformation matrix used for head pose estimation.

### 3.4 The reference frame problem

Any measurement of nasal deviation is a measurement relative to a facial midline, and the choice of midline turned out to dominate the choice of measurand.

Three midline definitions were compared across ten photographs: an average of the face-edge midpoint and eye-corner midpoint; a line from glabella to menton; and a line from the intercanthal midpoint to the philtrum. Mean disagreement between definitions was 3.32 pixels, with a maximum of 8.80, against a total normal-to-severe measurement range spanning approximately 1.5 pixels.

Reproducibility was assessed on five photographs of one subject taken minutes apart. The face-edge midline produced normalised tip offsets of +0.0197, +0.0192, +0.0136, +0.0032 and −0.0042 — a reversal of sign on an unchanging nose (SD = 0.01046). The intercanthal–philtrum midline produced −0.0041, −0.0066, −0.0025, −0.0082 and −0.0115 (SD = 0.00352). Measured through the complete pipeline, reproducibility improved from SD 0.01046 to 0.00241, a fourfold gain.

The intercanthal–philtrum midline was adopted. Both endpoints are midline structures independent of nasal anatomy, and neither depends on the facial outline, which varies with hairline, jaw morphology and head rotation.

### 3.5 Head pose gating

Roll, pitch and yaw are extracted from MediaPipe's facial transformation matrix. Photographs exceeding 3° of yaw are rejected rather than scored.

The threshold is empirically motivated. One subject photographed at 11.97° yaw measured 0.0690 normalised offset; the same nose in a second photograph at 3.39° yaw measured 0.0146 — a 4.7-fold difference attributable to projection geometry rather than anatomy. An intermediate approach, de-rotating the landmark cloud using MediaPipe's depth estimates, was implemented and then discarded: on a photograph with only 3.4° of yaw, the correction changed the measurement from 0.0009 to 0.0129, introducing more error than it removed. MediaPipe's z coordinates are relative monocular estimates and are not adequate for this correction. Declining to measure a photograph is honest; silently transforming it is not.

A separate roll-normalisation step (rotating the image so the eyes are level, then re-detecting landmarks) was tested afterward and initially appeared to improve both reproducibility (SD 0.00158 → 0.00081) and the all-data correlation (ρ 0.609 → 0.642). However, full re-evaluation through the deployed pipeline showed it interacting badly with the yaw gate — two confirmed severe cases that previously passed the gate were newly rejected, and leave-one-out correlation and sensitivity both declined (ρ 0.486 → 0.406; sensitivity 56% → 33%). It was reverted. This is reported because the initial, isolated test would have been a false positive as a standalone claim.

### 3.6 Candidate measurements

Fourteen measurements were implemented, spanning six distinct approaches:

**Landmark geometry.** Lateral tip deviation; maximum dorsal offset under three midline definitions; nasion–tip–lip axis angle; drift slope of the dorsal contour.

**Contour curvature.** Quadratic and cubic polynomial fits and cubic-spline signed curvature along the dorsum, with arc-length excess relative to a straight path, intended to capture C- and S-shaped deviation.

**Mirror symmetry.** Perpendicular offset of eight bilateral landmark pairs along the nasal sidewalls (brow–tip aesthetic lines), and pixel-level comparison of the nasal region against its own reflection.

**Photometric.** Shadow-intensity asymmetry sampled across horizontal profiles of the dorsum, with a forehead region as an illumination control.

**Spectral/gradient descriptors.** Histogram-of-oriented-gradients features over an aligned nasal crop, reduced by principal component analysis.

**Direct ridge localisation.** Horizontal intensity scanning to locate the specular highlight of the ridge from image pixels rather than the landmark mesh, using three peak estimators.

### 3.7 Evaluation protocol

Each measurement was assessed by Spearman rank correlation against clinical grade. Measurements reaching nominal significance were subjected to four further checks: outlier leverage (recomputation with the most extreme observation removed), permutation testing (10,000 label shuffles), partial correlation (controlling for head yaw and, separately, for capture geometry), and restricted-range analysis (recomputation within narrow bands of the potential confound).

Measurement precision was established from five repeat photographs of one subject before clinical comparison. Sensitivity to capture conditions was assessed by image-space augmentation: brightness and contrast perturbation, unilateral illumination gradient, additive sensor noise, perspective warp and JPEG recompression, with landmarks re-extracted from each perturbed image.

### 3.8 Scoring

The retained measurement is mapped linearly to a 0–100 scale: `score = offset ÷ 0.020 × 100`, clipped at 100, where the divisor corresponds to the 95th percentile of the graded set. No model is fitted; there are no learned parameters and no training set.

The photo-based score and the symptom-questionnaire score are reported separately rather than combined into a single figure (see Section 6.2).

---

## 4. Materials

**4.1 Photograph set.** Thirty-five photographs with clinician-assigned severity grades: 11 normal, 7 mild, 8 moderate, 9 severe. Comprises cases from the collaborating facial plastic surgeon, two surgically documented pre/post-operative cases, and consenting non-clinical volunteers. Grades assigned by a single surgeon.

**4.2 Precision set.** Five photographs of one subject, taken minutes apart in a single session, used to establish measurement precision independently of clinical comparison.

**4.3 External set.** Forty images from CelebA-HQ, a public dataset of high-resolution photographs, measured to assess false-positive behaviour on unselected faces. No clinical grades exist for this set.

---

## 5. Results

### 5.1 Candidate measurements

| Measurement family | ρ | p | Outcome |
|---|---|---|---|
| Dorsal offset, intercanthal–philtrum midline | +0.609 | 0.0001 | **Retained** |
| Lateral tip deviation, face-edge midline | +0.05 | 0.83 | No association |
| Dorsal offset, glabella–menton midline | +0.042 | 0.86 | No association |
| Nasal axis angle (nasion–tip–lip) | — | — | Tracked head yaw (r=0.87) |
| Dorsal drift slope (linear fit) | +0.018 | 0.94 | No association |
| Spline curvature, quadratic term | +0.449 | 0.007 | Redundant with offset |
| Spline curvature, cubic term | +0.396 | 0.019 | Redundant with offset |
| Arc-length excess of dorsal contour | +0.514 | 0.002 | Redundant with offset |
| Sidewall (brow-tip line) symmetry | −0.128 | 0.59 | No association |
| Shadow-intensity asymmetry | −0.055 | 0.82 | No association |
| Pixel mirror difference | +0.30 | 0.16 | No association |
| HOG silhouette descriptor (PC1) | −0.041 | 0.85 | No association |
| Ridge scan, brightest-pixel | +0.218 | 0.21 | No association |
| Ridge scan, weighted centroid | +0.063 | 0.72 | No association |

The three curvature measurements reached nominal significance but correlated 0.65–0.81 with dorsal offset. After partial correlation controlling for it, their independent contributions were −0.05, −0.00 and +0.10 (all p > 0.37), and adding them reduced leave-one-out performance from ρ = 0.486 to ρ = 0.338. They are reported as redundant, not as findings.

### 5.2 Retained measurement

Maximum dorsal offset from the intercanthal–philtrum midline correlated with clinical grade at ρ = +0.609 (p = 0.0001, n = 35). Leave-one-out: ρ = +0.486 (p = 0.003) — the appropriate figure for unseen photographs.

| Grade | n | Median offset | Range | Median score |
|---|---|---|---|---|
| Normal | 11 | 0.0042 | 0.0016–0.0143 | 21.1 |
| Mild | 7 | 0.0097 | 0.0020–0.0114 | 48.3 |
| Moderate | 8 | 0.0068 | 0.0047–0.0179 | 34.2 |
| Severe | 9 | 0.0150 | 0.0081–0.0690 | 76.2 |

Mild and moderate groups are not separated by this measurement — moderate's median score sits *below* mild's. The severe group is separated. At a threshold of 0.0150, severe versus non-severe classification was 86% accurate (30/35), sensitivity 56% (5/9), specificity 96% (25/26).

| Yaw gate | n retained | ρ | Sensitivity | Specificity |
|---|---|---|---|---|
| None | 35 | +0.609 | 56% | 96% |
| 8° | 34 | +0.580 | 50% | 96% |
| 5° | 34 | +0.580 | 50% | 96% |
| 3° | 31 | +0.566 | 50% | 96% |
| 2° | 28 | +0.566 | 50% | **100%** |

### 5.3 Classifier evaluation

Four-class classification was attempted with logistic regression, ordinal logistic regression (cumulative-logit), random forests, gradient boosting, support vector machines (linear and RBF kernels), k-nearest neighbours, naive Bayes, Gaussian process classification, and linear discriminant analysis. Best leave-one-out result: 26%, against a 31% majority-class baseline.

The reason is visible in the training data. Photographs at normalised offsets of 0.0111 and 0.0117 carry grades of moderate and mild respectively; one at 0.0126 is graded severe while one at 0.0177 is graded normal. Contradictory labels at near-identical measurements cannot be resolved by any model — the fitted classifiers reproduced their own training labels only 49% of the time.

Synthetic data augmentation was evaluated in three forms. Feature-space augmentation (Gaussian perturbation of measurement values) reduced accuracy in all trials. Image-space augmentation (nine perturbed variants per photograph, trained with leave-one-photograph-out evaluation) improved four-class accuracy from 26% to 46% — still well below the 86% achieved by the unfitted threshold. Median-of-augmentations for measurement stabilisation changed correlation from +0.609 to +0.643 while *increasing* within-subject SD from 0.00158 to 0.00181, and was not adopted.

### 5.4 Precision and robustness

Within-subject precision: SD = 0.00158 normalised units (≈8 points on the 0–100 scale). Between-grade SD = 0.00651. Signal-to-noise ratio = 4.1.

| Perturbation | Mean shift | Ratio to signal | Rank order preserved |
|---|---|---|---|
| Brightness ±20% | 0.00118 | 0.18 | Yes |
| Contrast ±20% | 0.00131 | 0.20 | Yes |
| Unilateral lighting | 0.00109 | 0.17 | Yes |
| Sensor noise (σ=8) | 0.00097 | 0.15 | Yes |
| Perspective warp (2%) | 0.00122 | 0.19 | Yes |
| JPEG quality 60 | 0.00089 | 0.14 | Yes |
| **All conditions** | 0.00232 | **0.36** | Yes |

### 5.5 External set behaviour

Ungated, 75% of the CelebA-HQ sample exceeded the severe threshold (median 0.0453 — an order of magnitude above the graded normal median). Median head yaw in this set was 8.85°, versus 0.93° in the graded set, reflecting its origin in unposed press photography. Applying yaw gates of 8°/5°/3°/2° reduced the flagged proportion to 52%/35%/17%/13%, and the median offset to 0.0096 — within the graded normal range. The elevated ungated rate reflects photographs the system should decline to measure, not a property of the measurement.

### 5.6 Capture-geometry confound

The ratio of bi-zygomatic width to interocular distance correlated with clinical grade at ρ = +0.577 (p = 0.0003), with medians of 1.476/1.528/1.583/1.619 across normal/mild/moderate/severe. This quantity has no plausible anatomical relationship to septal deviation; the likely explanation is that clinical and non-clinical photographs were captured under different conditions.

Dorsal offset survived partial correlation controlling for this ratio (ρ = +0.473, p = 0.004), and was unrelated to it within the precision set where capture distance was constant (ρ = −0.10). However, restriction to progressively narrower ratio bands produced decaying correlations: +0.571 (n=29, p=0.001), +0.404 (n=23, p=0.056), +0.221 (n=17, p=0.39). **The confound is not excluded at this sample size** — the most significant open question in the present work.

### 5.7 Correction to a previously reported result

An earlier draft reported a pre-operative score of 74.5 for a surgically documented case. The pre-operative photograph has since been measured at 11.97° of head yaw and is rejected by the current pose gate. A second pre-operative photograph of the same subject, at 3.39° yaw, measures 0.0146 — borderline rather than extreme. The original figure substantially reflected head rotation and should not be cited.

---

## 6. Discussion

The principal finding is narrow. One geometric measurement taken from a frontal photograph ranks nasal deviation severity with moderate reliability, separating severe from non-severe cases with high specificity and modest sensitivity. It does not reproduce four-level clinical grading, and no tested method did.

The thirteen negative results are the larger contribution. They span sparse landmark geometry, dorsal curvature, mirror comparison at landmark and pixel level, shadow intensity, gradient-histogram descriptors, and direct ridge localisation from image intensity. The last is particularly informative because it bypasses the facial mesh entirely — a recurring hypothesis that MediaPipe's landmark model might smooth away genuine asymmetry did not hold up (rho = 0.06–0.22, with a forehead control ruling out an illumination artifact). Independently, the precision set established landmarks reproduce to ±0.0014 normalised units — the landmarks are stable; the grades simply differ by less than that in most of the sample.

The reference frame finding deserves emphasis beyond this application. Substituting the intercanthal–philtrum midline for a face-edge-derived one improved reproducibility fourfold and was the change that made the retained correlation detectable at all. In landmark-based facial measurement, the choice of reference frame can dominate the choice of measurand.

Head pose materially affects any midline-referenced nasal measurement: 12° of yaw produced a 4.7-fold change on an unchanging nose. An attempted correction (roll normalisation) that improved isolated metrics degraded end-to-end performance once tested through the complete pipeline including the pose gate — a caution about validating preprocessing steps in isolation from the system they feed into.

Finally, the tight clustering of clinician-graded cases in external measurement is consistent with the established distinction between internal septal deviation and external nasal deformity. Internal deviation is graded on coronal CT via landmarks internal to the skull. A patient may have marked internal deviation with an externally straight nose, and conversely. The moderate correlation reported here is consistent with a partial rather than deterministic relationship, and any photographic screening tool inherits that ceiling regardless of technical sophistication.

### 6.1 On the absence of a fitted model

No machine learning model is used in the deployed measurement. This was not a starting design choice but an empirical finding: eight classifier families (logistic regression, ordinal regression, random forest, gradient boosting, SVM with two kernels, k-NN, naive Bayes, Gaussian process, LDA) were tested for four-class grading, and all performed at or below chance. The training data contains near-identical measurements with contradictory labels — a genuine property of the data, not a modelling deficiency — and any fitted classifier reproduces that contradiction as noise rather than resolving it. The unfitted geometric threshold, which cannot overfit because nothing is fit, outperformed every trained alternative on the task it is actually suited to (severe vs. non-severe).

### 6.2 Combining photographic and symptom scores

An early implementation combined the photographic score and a symptom-questionnaire score into a single number using hand-selected weights (varying by symptom severity tier) and an ad hoc confidence boost when both scores were elevated. This formula was never validated against outcomes and was removed. The two scores are now reported independently, since a patient can present with significant symptoms and an externally straight nose — internal deviation without visible external crookedness, a real and clinically relevant combination that a blended score would obscure.

---

## 7. Limitations

1. **Sample size.** Thirty-five graded photographs support the reported correlation but not fine-grained classification. Confidence intervals on all reported figures are wide.
2. **Development and evaluation on the same set.** All fourteen measurements were selected and tested on the same photographs. Leave-one-out estimation mitigates but does not eliminate selection effects across multiple candidates. No independent test set has been evaluated.
3. **Capture-geometry confound.** Unresolved at this sample size (Section 5.6) — the most significant open question in the present work.
4. **Sensitivity.** Approximately half of clinically severe cases fall below threshold. A low score does not exclude deviation and must not be presented as reassurance.
5. **Grade resolution.** Mild and moderate cases are indistinguishable. Severity labels are thresholds on a continuous measurement, not clinical grades.
6. **External versus internal anatomy.** The system measures external dorsal position and cannot assess internal septal deviation, which determines most surgical decisions.
7. **Single-rater grading.** All clinical grades derive from one surgeon; inter-rater reliability was not assessed.
8. **Demographic composition.** The photograph set is small and its demographic composition was not systematically characterised. Generalisation across populations is untested.

---

## 8. Future Work

1. **Independent prospective validation.** A set of graded photographs captured under a uniform protocol across all severity levels is the immediate priority — it would simultaneously provide an unseen test set and resolve the confound in Section 5.6 by design.
2. **Standardised photographic protocol.** Fixed subject distance, real-time frontal-alignment verification, and controlled illumination.
3. **Patient-reported outcomes.** The validated NOSE instrument (Stewart et al., 2004) measures symptom burden from nasal obstruction and requires no photograph. Reporting it alongside, not combined with, the photographic measurement preserves the clinically informative case described in Section 6.2.
4. **Additional views.** The basal view, standard in rhinological photography, displays the caudal septum and nostril apertures directly and may carry structural information the frontal view does not.
5. **Active illumination.** Photometric stereo using controlled screen illumination could recover surface orientation of the nasal dorsum, addressing the absence of depth information in a single photograph.
6. **Correlation against CT ground truth.** Direct comparison of external measurement against radiologist-measured septal deviation angle would quantify the external-to-internal relationship that bounds all photographic approaches.

---

## 9. Conclusion

We evaluated fourteen computer vision measurements of external nasal asymmetry against surgeon-assigned severity grades. One survived: maximum dorsal offset from an intercanthal–philtrum midline, correlating with clinical grade at ρ = 0.486 under leave-one-out estimation, separating severe from non-severe cases at 86% accuracy with 96% specificity and 56% sensitivity, reproducing to within approximately 8 points on a 0–100 scale.

Thirteen approaches did not. The consistency of that result across landmark geometry, contour curvature, mirror symmetry, photometric analysis and direct pixel-level ridge localisation suggests a limit on what frontal photographic geometry encodes about nasal deviation, rather than a deficiency of any particular technique. Four-level clinical grading was not recoverable by any method tested, including nine trained classifier families.

A photographic screening tool for nasal deviation is feasible within these bounds: it can flag externally marked deviation with high specificity, and should be presented as doing only that. Whether the measured correlation reflects nasal anatomy or partly reflects how the photographs were captured remains open, and is the question a uniformly captured prospective set would answer.

---

## Acknowledgements

The author thanks Dr. Alexander Markarian for clinical grading and discussion of assessment methodology, and the individuals who consented to photographic measurement.

## Data and Code Availability

Analysis code and the measurement implementation are publicly available at [github.com/sairamvottikonda-tech/NoseCheckAI](https://github.com/sairamvottikonda-tech/NoseCheckAI). Clinical photographs are not shared, in accordance with patient privacy.

## References

1. Mladina R, Čujić E, Subarić M, Vuković K. Nasal septal deformities in ear, nose, and throat patients: an international study. *Am J Otolaryngol.* 2008;29(2):75–82.
2. Bhattacharyya N. Symptom outcomes after endoscopic sinus surgery for chronic rhinosinusitis. *Arch Otolaryngol Head Neck Surg.* 2004;130(3):329–333.
3. Gray LP. Deviated nasal septum: incidence and etiology. *Ann Otol Rhinol Laryngol Suppl.* 1978;87(3 Pt 3 Suppl 50):3–20.
4. Bhattacharyya N, Kepnes LJ. Economic benefit of tonsillectomy in adults with chronic tonsillitis. *Ann Otol Rhinol Laryngol.* 2002;111(11):983–988.
5. Papel ID, et al. *Facial Plastic and Reconstructive Surgery.* 4th ed. Thieme; 2016.
6. Lugaresi C, et al. MediaPipe: a framework for building perception pipelines. arXiv:1906.08172. 2019.
7. Neves CA, et al. Quantification of nasal septal deviation with computed tomography data. *JAMA Facial Plast Surg.* 2020.
8. Zhang Y, et al. NSD-Net: an automatic assessment framework for nasal septum deviation based on landmark detection. *Biomed Signal Process Control.* 2025.
9. Galdino GM, et al. Digital photography: a comparison with film photography. *Plast Reconstr Surg.* 2001;108(6):1764–1767.
10. Automated facial asymmetry assessment using Siamese neural networks on mirrored facial halves. PMC13103240.
11. Barbosa J, et al. Automated facial palsy analysis using facial landmarks. *Annu Int Conf IEEE Eng Med Biol Soc.* 2018.
12. Cheon YW, et al. Three-dimensional analysis of facial asymmetry. *Aesthetic Plast Surg.* 2020.
13. Elahi MM, Frenkiel S, Fageeh N. Paraseptal structural changes and chronic sinus disease in relation to the deviated septum. *J Otolaryngol.* 1997;26(4):236–240.
14. Crooked nose deviation angle and I/C/S-type classification in rhinoplasty outcome assessment.
15. Automatic apparent nasal index from single facial photographs using a lightweight deep learning pipeline: a pilot study. 2025. PMC12654233.
16. Stewart MG, Witsell DL, Smith TL, Weaver EM, Yueh B, Hannley MT. Development and validation of the Nasal Obstruction Symptom Evaluation (NOSE) scale. *Otolaryngol Head Neck Surg.* 2004;130(2):157–163.

---

*References 10 and 14 require full citation details before formal submission. This draft is intended for review with the collaborating surgeon prior to any journal or poster submission.*
