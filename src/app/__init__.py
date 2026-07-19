"""
NoseCheck Flask Web Application.

Mobile-friendly web interface for DNS screening.
"""

import os
import sys
import tempfile
import uuid
from pathlib import Path

from flask import Flask, jsonify, render_template, request, redirect, url_for

_root = Path(__file__).resolve().parent.parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))
os.chdir(_root)

app = Flask(__name__, template_folder=str(_root / "templates"), static_folder=str(_root / "static"))

try:
    import config
    app.config["MAX_CONTENT_LENGTH"] = config.FLASK_CONFIG.get("max_content_length", 16 * 1024 * 1024)
    upload = config.FLASK_CONFIG.get("upload_folder", _root / "data" / "images")
    app.config["UPLOAD_FOLDER"] = str(Path(upload))
    ALLOWED_EXTENSIONS = config.FLASK_CONFIG.get("allowed_extensions", {"png", "jpg", "jpeg", "heic", "heif"})
except ImportError:
    app.config["UPLOAD_FOLDER"] = str(_root / "data" / "images")
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "heic", "heif"}

_upload = Path(app.config["UPLOAD_FOLDER"])
try:
    _upload.mkdir(parents=True, exist_ok=True)
    (_upload / ".write_test").touch()
    (_upload / ".write_test").unlink()
except (OSError, PermissionError):
    app.config["UPLOAD_FOLDER"] = tempfile.gettempdir()

_sessions = {}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def run_pipeline(image_path):
    """Run full analysis pipeline on an image with angle detection.

    Path A: Full face detected -> MediaPipe landmark-based analysis
    Path B: No face detected -> contour-based analysis for isolated nose models
    """
    from src.image_processing.image_loader import load_image
    from src.image_processing.preprocessor import preprocess
    from src.landmark_detection.stable_detector import detect_landmarks_stable
    from src.measurement.asymmetry_calculator import calculate
    from src.measurement.angle_detection import detect_camera_tilt, compensate_for_tilt, get_angle_warning
    from src.scoring.ml_score_calculator import ml_calculate_score as calculate_score

    image = load_image(image_path)
    if image is None:
        return None

    processed = preprocess(image)
    landmarks, _confidence = detect_landmarks_stable(processed)

    if landmarks is None and image.shape[0] > 0:
        h, w = image.shape[:2]
        max_dim = 960
        if max(h, w) > max_dim:
            scale = max_dim / max(h, w)
            import cv2
            new_w = int(w * scale)
            new_h = int(h * scale)
            fallback = cv2.resize(image, (new_w, new_h))
        else:
            fallback = image
        landmarks, _confidence = detect_landmarks_stable(fallback)

    if landmarks is not None:
        tilt_info = detect_camera_tilt(landmarks)
        measurements = calculate(landmarks)

        if not tilt_info['is_frontal']:
            measurements = compensate_for_tilt(measurements, tilt_info)

        result = calculate_score(measurements)
        result['camera_angle'] = tilt_info
        result['angle_warning'] = get_angle_warning(tilt_info)
        result['analysis_method'] = 'landmark'
    else:
        from src.measurement.contour_analyzer import analyze_contour
        contour_metrics = analyze_contour(image)
        if contour_metrics is None:
            return None

        measurements = {
            "lateral_deviation": contour_metrics["lateral_deviation"],
            "septal_angle": contour_metrics["septal_angle"],
            "nostril_asymmetry": contour_metrics["nostril_asymmetry"],
            "bridge_straightness": contour_metrics["bridge_straightness"],
            "face_width": contour_metrics["face_width"],
        }
        result = calculate_score(measurements)
        result['analysis_method'] = 'contour'
        result['contour_detail'] = {
            "area_asymmetry": contour_metrics.get("area_asymmetry", 0),
            "nostril_detail": contour_metrics.get("nostril_detail", {}),
            "contour_area": contour_metrics.get("contour_area", 0),
        }
        result['angle_warning'] = None

    import gc
    gc.collect()

    return result


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        try:
            if "photo" not in request.files:
                return jsonify({"error": "No photo provided"}), 400
            file = request.files["photo"]
            if file.filename == "":
                return jsonify({"error": "No file selected"}), 400
            if file and allowed_file(file.filename):
                ext = file.filename.rsplit(".", 1)[1].lower()
                filename = f"{uuid.uuid4().hex}.{ext}"
                upload_dir = Path(app.config["UPLOAD_FOLDER"])
                upload_dir.mkdir(parents=True, exist_ok=True)
                filepath = upload_dir / filename
                file.save(str(filepath))
                result = run_pipeline(str(filepath))
                try:
                    filepath.unlink(missing_ok=True)
                except OSError:
                    pass
                if result is None:
                    return jsonify({"error": "Could not detect nose in image. Please upload a clear frontal photo of a face or nose model."}), 400
                
                response = {
                    "deviation_score": result["deviation_score"],
                    "classification": result["classification"],
                    "metrics": result.get("raw_metrics", {}),
                    "analysis_method": result.get("analysis_method", "landmark"),
                }
                
                if result.get('angle_warning'):
                    response['warning'] = result['angle_warning']
                    response['camera_angle'] = {
                        'vertical_tilt': result['camera_angle']['vertical_tilt'],
                        'quality_score': result['camera_angle']['quality_score'],
                    }
                
                if result.get('contour_detail'):
                    response['contour_detail'] = result['contour_detail']
                
                return jsonify(response)
        except Exception as e:
            import traceback
            traceback.print_exc()
            return jsonify({"error": str(e)}), 500
    return render_template("upload.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    """API endpoint: POST photo, return JSON with deviation_score, classification, metrics."""
    try:
        if "photo" not in request.files and "image" not in request.files:
            return jsonify({"error": "No photo provided"}), 400
        file = request.files.get("photo") or request.files.get("image")
        if file.filename == "":
            return jsonify({"error": "No file selected"}), 400
        if not allowed_file(file.filename):
            return jsonify({"error": "Invalid file type"}), 400
        ext = file.filename.rsplit(".", 1)[1].lower()
        filename = f"{uuid.uuid4().hex}.{ext}"
        upload_dir = Path(app.config["UPLOAD_FOLDER"])
        upload_dir.mkdir(parents=True, exist_ok=True)
        filepath = upload_dir / filename
        file.save(str(filepath))
        result = run_pipeline(str(filepath))
        try:
            filepath.unlink(missing_ok=True)
        except OSError:
            pass
        if result is None:
            return jsonify({"error": "Could not detect nose in image. Please upload a clear frontal photo of a face or nose model."}), 400
        
        response = {
            "deviation_score": result["deviation_score"],
            "classification": result["classification"],
            "metrics": result.get("raw_metrics", {}),
            "analysis_method": result.get("analysis_method", "landmark"),
        }
        
        if result.get('angle_warning'):
            response['warning'] = result['angle_warning']
            response['camera_angle'] = {
                'vertical_tilt': result['camera_angle']['vertical_tilt'],
                'quality_score': result['camera_angle']['quality_score'],
            }
        
        if result.get('contour_detail'):
            response['contour_detail'] = result['contour_detail']
        
        return jsonify(response)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


def _classify_score(score: float) -> str:
    """
    Classify severity from 0-100 score.

    Uses the SAME classification_thresholds defined in config.py (and used
    by src/scoring/score_calculator.py) so that the photo-only score and the
    combined visual+symptom score are always classified consistently. These
    used to be two separate hardcoded threshold sets that disagreed with
    each other (e.g. a score of 60 was "moderate" in one path and "severe"
    in the other) -- that inconsistency is what this fixes.
    """
    from src.scoring.score_calculator import _classify
    return _classify(score)


@app.route("/questionnaire", methods=["GET", "POST"])
def questionnaire():
    from src.questionnaire.questionnaire import get_questions, compute_symptom_score, combine_scores

    if request.method == "POST":
        data = request.get_json() or request.form
        responses = []
        questions = get_questions()
        for q in questions:
            key = f"symptom_{q['id']}"
            val = data.get(key, 0)
            try:
                responses.append(int(val))
            except (ValueError, TypeError):
                responses.append(0)
        symptom_score = compute_symptom_score(responses)
        visual_score = float(data.get("visual_score", 0))
        combined = combine_scores(visual_score, symptom_score)
        classification = _classify_score(combined)
        return jsonify({
            "symptom_score": symptom_score,
            "visual_score": visual_score,
            "combined_score": combined,
            "classification": classification,
        })
    return render_template("questionnaire.html", questions=get_questions())


@app.route("/result")
def result():
    score = request.args.get("score", type=float, default=0)
    classification = request.args.get("classification", "normal")
    visual_score = request.args.get("visual_score", type=float, default=None)
    symptom_score = request.args.get("symptom_score", type=float, default=None)
    return render_template(
        "result.html",
        score=score,
        classification=classification,
        visual_score=visual_score,
        symptom_score=symptom_score,
    )


@app.route("/validation")
def validation_report():
    """Serve the CT validation research report if it exists."""
    report = _root / "data" / "ct_validation" / "validation_report.html"
    if report.exists():
        return report.read_text(encoding="utf-8")
    return render_template("validation_empty.html")


def create_app():
    return app


@app.route("/debug/measurements", methods=["POST"])
def debug_measurements():
    import json as _j
    if "photo" not in request.files:
        return _j.dumps({"error": "no photo"}), 400
    photo = request.files["photo"]
    suffix = Path(photo.filename).suffix.lower()
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        photo.save(tmp.name)
        tmp_path = tmp.name
    try:
        from src.image_processing.image_loader import load_image
        from src.image_processing.preprocessor import preprocess
        from src.landmark_detection.stable_detector import detect_landmarks_stable
        from src.measurement.asymmetry_calculator import calculate
        from src.measurement.angle_detection import detect_camera_tilt, compensate_for_tilt
        image = load_image(tmp_path)
        if image is None:
            return _j.dumps({"error": "failed"}), 400
        processed = preprocess(image)
        landmarks, _confidence = detect_landmarks_stable(processed) or detect_landmarks(image)
        if landmarks is None:
            return _j.dumps({"error": "no face"}), 400
        tilt = detect_camera_tilt(landmarks)
        m = calculate(landmarks)
        if not tilt["is_frontal"]:
            m = compensate_for_tilt(m, tilt)
        return _j.dumps({"input_shape": list(image.shape), "processed_shape": list(processed.shape), "measurements": {k: float(v) for k,v in m.items()}, "tilt": {k: float(v) if isinstance(v, (int,float)) else v for k,v in tilt.items()}}, indent=2), 200
    finally:
        import os; os.unlink(tmp_path)
