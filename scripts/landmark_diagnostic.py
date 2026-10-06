"""
Landmark diagnostic: does MediaPipe's nose mesh actually follow this nose?

For one photo, runs the dorsal-offset measurement four ways and draws each
variant's nose-bridge points on the photo, so you can see whether they agree
with each other and with the nose you can see.

  A  as the app does it  (resized to 640x480 with padding, contrast-normalised)
  B  resized the same way, but without contrast normalisation
  C  full resolution (no resize, no contrast normalisation)
  D  photo mirrored left-right, measured like A, then mapped back

How to read it:
  * A-D agree with each other but sit off the visible nose
        -> the face mesh itself is not following the nose on this photo
           (a limit of the detector, not of the drawing or the resize).
  * A-D disagree with each other
        -> the measurement is unstable for this photo; resizing, contrast
           handling or orientation is changing where the points land.

Signed offsets are in interocular units. Positive = toward the RIGHT SIDE OF
THE PICTURE (which is the subject's left), negative = toward the left side
of the picture.

Usage (from the repo root):
    python scripts/landmark_diagnostic.py photo.jpg
    python scripts/landmark_diagnostic.py photo.jpg out.png --mesh

Nothing is deployed or stored; it only reads the photo and writes a PNG.
"""
import argparse
import sys
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

# BGR colours for the four variants
COLOURS = {"A": (21, 204, 250), "B": (0, 140, 255), "C": (80, 200, 60), "D": (200, 60, 200)}
LABELS = {
    "A": "A as app (640x480 + contrast)",
    "B": "B resized, no contrast",
    "C": "C full resolution",
    "D": "D mirrored, then mapped back",
}
MAX_FULL_RES = 2400  # long side cap for variant C, for speed only


def _detect(bgr):
    import mediapipe as mp
    from src.landmark_detection.detector import _get_face_landmarker
    rgb = np.ascontiguousarray(cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB))
    res = _get_face_landmarker().detect(
        mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb))
    if not res.face_landmarks:
        return None, None
    mat = (np.array(res.facial_transformation_matrixes[0])
           if res.facial_transformation_matrixes else None)
    return res.face_landmarks[0], mat


def _measure(bgr_fed, to_original, mirror_sign=1):
    """Run detection + dorsal offset on the image actually fed to MediaPipe."""
    from src.measurement.dorsal_offset import compute_dorsal_offset
    from src.measurement.pose_gate import extract_pose
    lms, mat = _detect(bgr_fed)
    if lms is None:
        return {"ok": False, "why": "no face found"}
    h, w = bgr_fed.shape[:2]
    m = compute_dorsal_offset(lms, w, h)
    if m is None:
        return {"ok": False, "why": "degenerate geometry"}
    pts = m["points_px"]
    out = {
        "ok": True,
        "yaw": extract_pose(mat)["yaw"] if mat is not None else None,
        "max_offset": m["max_offset"],
        "profile": {i: mirror_sign * v for i, v in m["profile"].items()},
        "canthal_mid": to_original(pts["canthal_mid"]),
        "philtrum": to_original(pts["philtrum"]),
        "dorsum": {i: to_original(p) for i, p in pts["dorsum"].items()},
        "mesh": [to_original((l.x * w, l.y * h)) for l in lms],
    }
    return out


def run_variants(image):
    from src.image_processing import preprocessor as pp
    h, w = image.shape[:2]
    geom = pp.letterbox_geometry(w, h)

    def via_letterbox(pt, flip=False):
        x = (pt[0] - geom["left"]) / geom["new_w"]
        y = (pt[1] - geom["top"]) / geom["new_h"]
        return (1.0 - x if flip else x, y)

    results = {}
    results["A"] = _measure(pp.preprocess(image), via_letterbox)

    saved = pp.NORMALIZE_LIGHTING
    pp.NORMALIZE_LIGHTING = False
    try:
        results["B"] = _measure(pp.preprocess(image), via_letterbox)
    finally:
        pp.NORMALIZE_LIGHTING = saved

    big = image
    if max(h, w) > MAX_FULL_RES:
        s = MAX_FULL_RES / max(h, w)
        big = cv2.resize(image, (round(w * s), round(h * s)), interpolation=cv2.INTER_AREA)
    bh, bw = big.shape[:2]
    results["C"] = _measure(big, lambda p: (p[0] / bw, p[1] / bh))

    flipped = cv2.flip(image, 1)
    results["D"] = _measure(pp.preprocess(flipped),
                            lambda p: via_letterbox(p, flip=True), mirror_sign=-1)
    return results


def print_table(results):
    ids = [168, 6, 197, 195, 5, 4, 1]
    print("\nSigned offset at each bridge point, in interocular units "
          "(positive = right side of the picture):")
    print(f"{'variant':32s} {'yaw':>6s} {'max':>8s}  " + " ".join(f"{i:>7d}" for i in ids))
    for k in "ABCD":
        r = results[k]
        if not r["ok"]:
            print(f"{LABELS[k]:32s}  -- {r['why']}")
            continue
        yaw = f"{r['yaw']:.1f}" if r["yaw"] is not None else "n/a"
        row = " ".join(f"{r['profile'].get(i, float('nan')):+7.4f}" for i in ids)
        print(f"{LABELS[k]:32s} {yaw:>6s} {r['max_offset']:8.4f}  {row}")

    ok = [r for r in results.values() if r["ok"]]
    if len(ok) >= 2:
        mean_signed = [np.mean([v for i, v in r["profile"].items() if i != 168]) for r in ok]
        spread = max(mean_signed) - min(mean_signed)
        sides = {np.sign(m) for m in mean_signed if abs(m) > 0.003}
        print(f"\nAverage signed offset across variants: {min(mean_signed):+.4f} to "
              f"{max(mean_signed):+.4f}  (spread {spread:.4f}; the repeat-photo noise "
              f"floor is about 0.0016)")
        if spread > 0.004 or len(sides) > 1:
            print("-> The variants DISAGREE: the measurement is sensitive to resizing, "
                  "contrast handling or orientation on this photo.")
        else:
            print("-> The variants AGREE with each other. Compare them with the visible "
                  "nose in the saved picture: if they sit off the nose, the face mesh is "
                  "not following it.")


def draw(image, results, show_mesh):
    h, w = image.shape[:2]
    ref = next((results[k] for k in "ABCD" if results[k]["ok"]), None)
    if ref is None:
        return None
    P = lambda p: np.array([p[0] * w, p[1] * h], float)
    a, b = P(ref["canthal_mid"]), P(ref["philtrum"])
    L = float(np.linalg.norm(b - a))
    x0 = int(max(0, (a[0] + b[0]) / 2 - 1.1 * L)); x1 = int(min(w, (a[0] + b[0]) / 2 + 1.1 * L))
    y0 = int(max(0, a[1] - 0.6 * L));              y1 = int(min(h, b[1] + 0.7 * L))
    crop = image[y0:y1, x0:x1].copy()
    s = max(1.0, 900.0 / max(1, crop.shape[0]))
    crop = cv2.resize(crop, None, fx=s, fy=s, interpolation=cv2.INTER_CUBIC)
    T = lambda p: (int(round((P(p)[0] - x0) * s)), int(round((P(p)[1] - y0) * s)))

    if show_mesh and ref["ok"]:
        for p in ref["mesh"]:
            cv2.circle(crop, T(p), 2, (255, 255, 255), -1, cv2.LINE_AA)

    # reference line from the variant-A anchors (or first available)
    top = a - 0.45 * (b - a); bot = b + 0.35 * (b - a)
    pt0, pt1 = T(((top[0]) / w, (top[1]) / h)), T(((bot[0]) / w, (bot[1]) / h))
    cv2.line(crop, pt0, pt1, (0, 0, 0), 4, cv2.LINE_AA)
    cv2.line(crop, pt0, pt1, (238, 211, 34), 2, cv2.LINE_AA)

    for k in "ABCD":
        r = results[k]
        if not r["ok"]:
            continue
        pts = [T(r["dorsum"][i]) for i in r["dorsum"]]
        cv2.polylines(crop, [np.array(pts)], False, (0, 0, 0), 3, cv2.LINE_AA)
        cv2.polylines(crop, [np.array(pts)], False, COLOURS[k], 1, cv2.LINE_AA)
        for q in pts:
            cv2.circle(crop, q, 4, COLOURS[k], -1, cv2.LINE_AA)
            cv2.circle(crop, q, 4, (0, 0, 0), 1, cv2.LINE_AA)

    y = 18
    for k in "ABCD":
        if results[k]["ok"]:
            cv2.putText(crop, LABELS[k], (8, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 3, cv2.LINE_AA)
            cv2.putText(crop, LABELS[k], (8, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLOURS[k], 1, cv2.LINE_AA)
            y += 20
    return crop


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("photo")
    ap.add_argument("out", nargs="?", help="output PNG (default: <photo>_diagnostic.png)")
    ap.add_argument("--mesh", action="store_true",
                    help="also draw all 478 face-mesh points (variant A) as small white dots")
    args = ap.parse_args(argv)

    photo = Path(args.photo)
    if not photo.exists():
        sys.exit(f"No such file: {photo}")
    from src.image_processing.image_loader import load_image
    image = load_image(str(photo))
    if image is None:
        sys.exit("Could not read that image.")

    results = run_variants(image)
    print_table(results)
    pic = draw(image, results, args.mesh)
    if pic is None:
        sys.exit("No variant found a face, so nothing to draw.")
    out = Path(args.out) if args.out else photo.with_name(photo.stem + "_diagnostic.png")
    cv2.imwrite(str(out), pic)
    print(f"\nsaved: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
