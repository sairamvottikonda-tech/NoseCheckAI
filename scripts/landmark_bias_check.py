"""
Bias check: do the nose-bridge points sit on one side of the reference line
across MANY photos, and if so is that about the face or about the picture?

Run it on a folder of photos (for example your graded set). Each photo is
measured twice, exactly the way the app measures it:
  * as uploaded
  * mirrored left-right, then mapped back to the original orientation

Signed offsets are in interocular units, averaged over the five scored bridge
points. Positive = toward the RIGHT SIDE OF THE PICTURE (the subject's left)
in the photo as uploaded.

Why measure twice: mirroring tells two kinds of bias apart.
  * Face-side bias   (A + D) / 2   follows the face. The points sit toward the
                                   same side of the subject in both versions.
  * Picture-side bias (A - D) / 2  follows the image. The points shift toward
                                   the same side of the PICTURE even when the
                                   photo is mirrored, which points at the
                                   pipeline or detector, not at anatomy.
Only photos that pass the app's 3 degree head-turn gate are used in the
summary, since those are the ones the app would actually score.

Usage (from the repo root):
    python scripts/landmark_bias_check.py path/to/folder_of_photos
"""
import argparse
import sys
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

EXTS = {".jpg", ".jpeg", ".png"}
SCORED = [6, 197, 195, 5, 4, 1]       # 168 is the reference end and is not scored
MAX_YAW = 3.0                         # same gate the app uses
MEANINGFUL = 0.003                    # about twice the repeat-photo noise floor (0.0016)
CONSISTENT = 0.70                     # share of photos on the same side to call it consistent


def _signed_mean(bgr_fed, sign=1):
    import mediapipe as mp
    from src.landmark_detection.detector import _get_face_landmarker
    from src.measurement.dorsal_offset import compute_dorsal_offset
    from src.measurement.pose_gate import extract_pose
    rgb = np.ascontiguousarray(cv2.cvtColor(bgr_fed, cv2.COLOR_BGR2RGB))
    res = _get_face_landmarker().detect(mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb))
    if not res.face_landmarks or not res.facial_transformation_matrixes:
        return None, None
    h, w = bgr_fed.shape[:2]
    m = compute_dorsal_offset(res.face_landmarks[0], w, h)
    if m is None:
        return None, None
    yaw = extract_pose(np.array(res.facial_transformation_matrixes[0]))["yaw"]
    return sign * float(np.mean([m["profile"][i] for i in SCORED])), yaw


def measure_photo(path):
    from src.image_processing.image_loader import load_image
    from src.image_processing.preprocessor import preprocess
    img = load_image(str(path))
    if img is None:
        return None
    a, yaw = _signed_mean(preprocess(img))
    d, _ = _signed_mean(preprocess(cv2.flip(img, 1)), sign=-1)
    if a is None or d is None:
        return None
    return {"name": Path(path).name, "yaw": yaw, "A": a, "D": d,
            "face": (a + d) / 2.0, "pic": (a - d) / 2.0}


def _side(x):
    return "picture-right" if x > 0 else "picture-left"


def summarise(rows):
    used = [r for r in rows if abs(r["yaw"]) <= MAX_YAW]
    print(f"\nPhotos measured: {len(rows)}   passing the {MAX_YAW:g} degree gate: {len(used)}")
    if len(used) < 5:
        print("Too few usable photos for a meaningful summary.")
        return
    for key, title in (("face", "Face-side component (A+D)/2"), ("pic", "Picture-side component (A-D)/2")):
        vals = np.array([r[key] for r in used])
        med = float(np.median(vals))
        share = float(np.mean(np.sign(vals) == np.sign(med))) if med else 0.0
        where = f"{share*100:.0f}% of photos on the {_side(med)} side" if abs(med) > 1e-9 else "centred"
        print(f"{title:34s} median {med:+.4f}   {where}")
    face = np.array([r["face"] for r in used]); pic = np.array([r["pic"] for r in used])
    fmed, pmed = float(np.median(face)), float(np.median(pic))
    fshare = float(np.mean(np.sign(face) == np.sign(fmed)))
    pshare = float(np.mean(np.sign(pic) == np.sign(pmed)))

    print()
    flagged = False
    if abs(pmed) > MEANINGFUL and pshare >= CONSISTENT:
        flagged = True
        print(f"-> PICTURE-SIDE BIAS: the points shift toward the {_side(pmed)} even when the photo is "
              f"mirrored. That follows the image, not the face, so look at the pipeline or detector.")
    if abs(fmed) > MEANINGFUL and fshare >= CONSISTENT:
        flagged = True
        side = "subject's left (picture-right as uploaded)" if fmed > 0 else "subject's right (picture-left as uploaded)"
        print(f"-> FACE-SIDE BIAS: the points sit toward the {side} in most photos, and it survives "
              f"mirroring. The points follow the face, so the mesh's nose points are consistently "
              f"offset to that side of the eye-corner/philtrum reference line.")
    if not flagged:
        print("-> NO CONSISTENT SIDE BIAS: which side the points fall on varies from photo to photo, "
              "so a miss on one photo is specific to that photo.")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("folder")
    args = ap.parse_args(argv)
    folder = Path(args.folder)
    if not folder.is_dir():
        sys.exit(f"Not a folder: {folder}")
    files = sorted(p for p in folder.iterdir() if p.suffix.lower() in EXTS)
    if not files:
        sys.exit("No .jpg/.jpeg/.png files found in that folder.")

    print(f"{'photo':44s} {'yaw':>6s} {'as-is':>9s} {'mirrored':>9s} {'face-side':>10s} {'pic-side':>9s}")
    rows, skipped = [], []
    for p in files:
        try:
            r = measure_photo(p)
        except Exception as e:                      # keep going on a bad file
            r = None
            print(f"{p.name[:44]:44s}  error: {e}")
        if r is None:
            skipped.append(p.name)
            continue
        rows.append(r)
        gate = "" if abs(r["yaw"]) <= MAX_YAW else "  (over yaw gate)"
        print(f"{r['name'][:44]:44s} {r['yaw']:6.1f} {r['A']:+9.4f} {r['D']:+9.4f} "
              f"{r['face']:+10.4f} {r['pic']:+9.4f}{gate}")
    if skipped:
        print(f"\nNo face found in {len(skipped)} photo(s): " + ", ".join(skipped[:8]) + (" ..." if len(skipped) > 8 else ""))
    summarise(rows)
    return 0


if __name__ == "__main__":
    sys.exit(main())
