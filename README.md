# NoseCheckAI

A screening aid that estimates external nasal asymmetry from a smartphone photo, paired with a symptom questionnaire. Built out of a real septoplasty case, developed with a board-certified facial plastic surgeon (Dr. Alexander Markarian, USC), and validated honestly rather than assumed to work.

🔗 **Live app:** [nosecheckai-v2.onrender.com](https://nosecheckai-v2.onrender.com)

---

## What this actually is

This is not a diagnostic tool, and the app says so on every screen. It measures one thing: how far your nasal bridge sits from your facial midline in a frontal photo. That measurement was validated against 35 clinician-graded photos and holds up under real statistical scrutiny — but it has real, documented limits, and this README states them plainly rather than burying them.

**What it can do:** flag photos with marked external deviation, with high specificity (96% — it rarely flags someone incorrectly).

**What it can't do:** grade severity on a four-level scale (mild/moderate/severe testing performed no better than chance), or see internal septal deviation, which is what actually drives most clinical diagnoses and requires an in-person exam or CT scan.

---

## The measurement

Fourteen different computer-vision approaches were tested against clinician-graded photos over the course of development — landmark geometry, dorsal curvature, mirror symmetry, shadow analysis, spectral features, direct pixel-intensity ridge tracking. Thirteen returned no meaningful signal. One did:

**Dorsal offset from the intercanthal–philtrum midline.**

- A reference line is drawn from the midpoint of the inner eye corners to the philtrum — both points independent of nose shape, so a deviated nose can't pull its own reference line toward itself.
- Seven points along the nasal bridge are each measured for perpendicular distance from that line.
- The largest of those distances, normalized by interocular distance, is the score.

No model, no training data, no learned weights — it's geometry. That matters: every classifier tested (logistic regression, random forest, gradient boosting, SVM, k-NN, naive Bayes, Gaussian process, ordinal regression) performed at or below chance on four-class grading, because the underlying data genuinely contains contradictory labels at near-identical measurements. A fitted model would just memorize noise. This measurement doesn't try to do more than the data supports.

### Validation, honestly reported

| Metric | Result |
|---|---|
| Rank correlation with clinical grade (all data, n=35) | ρ = 0.61, p = 0.0001 |
| Rank correlation, leave-one-out (unseen photos) | ρ = 0.49, p = 0.003 |
| Severe vs. non-severe accuracy | 86% |
| Sensitivity | 56% — misses roughly half of clinically severe cases |
| Specificity | 96% — rarely flags a normal nose incorrectly |
| Within-subject reproducibility (5 repeat photos, same person) | ±0.0016 normalized units (~8 points on the 0–100 scale) |
| Robustness to lighting/contrast/noise/perspective/compression | Spread = 0.36 of the clinical signal — holds up |
| Four-class (normal/mild/moderate/severe) accuracy | At chance — not usable |

A pose gate rejects any photo where head yaw exceeds 3°, since a 12° turn was found to inflate the measurement nearly 5-fold on an otherwise straight nose — an artifact of projection, not anatomy.

An unresolved limitation: a capture-geometry proxy (face width ÷ interocular distance) correlates with clinical grade almost as strongly as the measurement itself (ρ = 0.58), suggesting some of the signal may reflect how photos were taken rather than pure anatomy. This is flagged, not hidden, and is the reason a properly controlled follow-up dataset is the next real step.

Full methodology, all fourteen tested approaches, and complete statistics are in the accompanying research paper (see `docs/`).

---

## How it works

```
Photo upload → pose check (reject if >3° head turn)
             → MediaPipe facial landmarks
             → dorsal offset from midline
             → 0–100 score, reported alongside a NOSE-style symptom score
             → both shown separately, never blended into one number
```

The photo score and the symptom score are deliberately **not** combined into a single figure. A person can have real symptoms with a straight-looking nose (internal deviation without visible external crookedness) — a genuine, common presentation that a blended score would quietly average away. Both are shown side by side, with a plain-language note when they disagree.

---

## App structure

- **Onboarding** — one-time intro, screening-not-diagnosis disclaimer
- **Home** — start a screening, see your last result
- **Photo Guide** — capture instructions, including the 3° pose limit
- **Upload** — take/select a photo, get the photo-only score
- **Questionnaire** — 8-question symptom checklist, one question at a time
- **Result** — two independent scores (photo, symptoms), a score breakdown page explaining the real method and its real numbers, and a share code for a clinician
- **History / Profile** — session-based (see Known Limitations)
- **Clinician Portal** — look up a shared result by code and add notes; also a real (non-fabricated) list of recent results

---

## Known limitations

- **No real accounts.** History and Profile are tied to an anonymous browser session cookie. Clearing cookies or switching devices loses access to past results.
- **No clinician authentication.** Anyone with a share code can view and annotate that result. Fine for a first version; not secure for production use with real patient data.
- **Ephemeral storage in production.** The current Render deployment uses SQLite on a non-persistent disk — data can be lost on redeploy. Not yet suitable for anything that needs to reliably persist.
- **Small validation set.** All statistics above come from 35 photos. Confidence intervals are wide, and the measurement was developed and evaluated on the same set (mitigated by leave-one-out estimation, not eliminated by it).
- **External measurement only.** This cannot and does not assess internal septal anatomy.

---

## Running locally

```bash
git clone https://github.com/sairamvottikonda-tech/NoseCheckAI.git
cd NoseCheckAI
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m flask --app src.app run --port 5001
```

Open `http://localhost:5001`.

### Project layout

```
NoseCheckAI/
├── src/
│   ├── app/__init__.py          # Flask routes
│   ├── db.py                    # SQLite persistence (results, share codes, notes)
│   ├── image_processing/        # Upload handling, preprocessing
│   ├── landmark_detection/      # MediaPipe wrapper, stable multi-pass detector
│   ├── measurement/             # dorsal_offset.py -- the validated measurement
│   ├── scoring/                 # scorer.py -- pose gate + scoring
│   └── questionnaire/           # Symptom checklist, scoring
├── templates/                   # Jinja2 templates (onboarding, home, guide, upload,
│                                 #   questionnaire, result, detail, history, profile,
│                                 #   clinician, clinician_all)
├── static/style.css
└── docs/                        # Research paper, methodology notes
```

---

## Research paper

The full methodology — all fourteen tested measurements, the statistical protocol, the capture-geometry confound, and the honest limitations — is written up as a research paper intended for review with the collaborating surgeon and potential submission to a digital health or medical imaging venue. See `docs/` for the current draft.

---

## Disclaimer

This is a screening aid for research and educational purposes only. It is not a clinical diagnosis and is not a substitute for examination by a qualified clinician. In validation, this tool missed approximately half of clinically severe cases — a low score does not rule out nasal septal deviation. If you have symptoms, see a doctor regardless of what this app shows.

## Acknowledgements

Developed in collaboration with Dr. Alexander Markarian, M.D., Facial Plastic Surgery, USC, who provided clinical grading for the validation set.
