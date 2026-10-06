"""
Preview the measurement overlay on a real photo, using the real pipeline.

This is the "test run": it does exactly what the web app does for an upload
(run_pipeline -> dorsal-offset score -> overlay), then draws the overlay onto
your photo and saves a PNG so you can check the landmarks by eye. Nothing is
deployed or sent anywhere.

Usage (from the repo root):
    python scripts/preview_overlay.py path/to/photo.jpg
    python scripts/preview_overlay.py path/to/photo.jpg out.png --enlarge

What to look for:
  * the dashed cyan line should run from between the inner corners of the
    eyes down over the middle of the upper lip
  * the yellow dots should sit on the bridge of the nose, root to tip
  * the pink/red dot marks the point furthest from the line
If any of those are clearly in the wrong place, that photo's score is not
trustworthy, which is exactly what the on-screen overlay is meant to reveal.

Note: importing the app creates the local nosecheck.db file if it does not
exist yet (it is git-ignored). Nothing is written to it by this script.
"""
import argparse
import sys
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

# BGR versions of the colours used in templates/upload.html
CYAN = (238, 211, 34)
YELLOW = (21, 204, 250)
PINK = (133, 113, 251)
RED = (72, 29, 225)
WHITE = (255, 255, 255)
HALO = (0, 0, 0)


def _dashed(img, p, q, color, thick, dash=14, gap=9):
    p, q = np.array(p, float), np.array(q, float)
    length = np.linalg.norm(q - p)
    if length < 1:
        return
    u = (q - p) / length
    t = 0.0
    while t < length:
        a = p + u * t
        b = p + u * min(t + dash, length)
        cv2.line(img, tuple(a.astype(int)), tuple(b.astype(int)), color, thick, cv2.LINE_AA)
        t += dash + gap


def draw_overlay(image, ov, enlarge=1.0):
    """Draw the overlay dict (as returned by the app) onto a copy of image."""
    out = image.copy()
    h, w = out.shape[:2]
    s = max(1.0, max(h, w) / 800.0)           # scale line widths with image size
    P = lambda p: np.array([p[0] * w, p[1] * h], float)

    a, b = P(ov["anchors"]["canthal_mid"]), P(ov["anchors"]["philtrum"])
    d = b - a
    dd = float(d @ d)

    def foot(q):
        t = ((q - a) @ d) / dd if dd else 0.0
        return a + t * d

    def place(p):
        q = P(p)
        if enlarge == 1.0 or not dd:
            return q
        f = foot(q)
        return f + enlarge * (q - f)

    def ipt(q):
        return (int(round(q[0])), int(round(q[1])))

    top, bot = P(ov["midline"]["top"]), P(ov["midline"]["bottom"])
    cv2.line(out, ipt(top), ipt(bot), HALO, int(4 * s), cv2.LINE_AA)
    _dashed(out, top, bot, CYAN, max(2, int(2 * s)))

    pts = [place([p["x"], p["y"]]) for p in ov["dorsum"]]
    for q0, q1 in zip(pts, pts[1:]):
        cv2.line(out, ipt(q0), ipt(q1), HALO, int(3 * s), cv2.LINE_AA)
    for q0, q1 in zip(pts, pts[1:]):
        cv2.line(out, ipt(q0), ipt(q1), YELLOW, max(1, int(1.4 * s)), cv2.LINE_AA)
    for q in pts:
        cv2.circle(out, ipt(q), int(3.5 * s), YELLOW, -1, cv2.LINE_AA)
        cv2.circle(out, ipt(q), int(3.5 * s), HALO, 1, cv2.LINE_AA)

    for p, q in zip(ov["dorsum"], pts):
        if p["id"] == ov.get("max_id"):
            f = foot(q)
            cv2.line(out, ipt(f), ipt(q), HALO, int(3 * s), cv2.LINE_AA)
            cv2.line(out, ipt(f), ipt(q), PINK, max(1, int(1.6 * s)), cv2.LINE_AA)
            cv2.circle(out, ipt(q), int(6 * s), RED, -1, cv2.LINE_AA)
            cv2.circle(out, ipt(q), int(6 * s), WHITE, max(1, int(1.5 * s)), cv2.LINE_AA)

    for q in (a, b):
        cv2.circle(out, ipt(q), int(4 * s), WHITE, -1, cv2.LINE_AA)
        cv2.circle(out, ipt(q), int(4 * s), CYAN, max(1, int(1.5 * s)), cv2.LINE_AA)

    if enlarge != 1.0:
        label = f"Deviation enlarged {enlarge:g}x"
        scale = 0.6 * s
        cv2.putText(out, label, (int(10 * s), int(24 * s)), cv2.FONT_HERSHEY_SIMPLEX,
                    scale, HALO, int(4 * s), cv2.LINE_AA)
        cv2.putText(out, label, (int(10 * s), int(24 * s)), cv2.FONT_HERSHEY_SIMPLEX,
                    scale, WHITE, max(1, int(1.5 * s)), cv2.LINE_AA)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("photo")
    ap.add_argument("out", nargs="?", help="output PNG (default: <photo>_overlay.png)")
    ap.add_argument("--enlarge", action="store_true",
                    help="exaggerate the deviation 5x so small offsets are visible")
    args = ap.parse_args(argv)

    photo = Path(args.photo)
    if not photo.exists():
        sys.exit(f"No such file: {photo}")

    from src.app import run_pipeline
    from src.image_processing.image_loader import load_image

    result = run_pipeline(str(photo))
    if result is None:
        sys.exit("The pipeline could not analyse this photo (no face or nose found).")

    method = result.get("analysis_method")
    print(f"method          : {method}")
    print(f"status          : {result.get('status', 'measured')}")
    if result.get("status") == "rejected" or result.get("deviation_score") is None:
        print(f"rejected        : {result.get('message') or result.get('reason')}")
        print("No overlay drawn: the photo was rejected before measurement.")
        return 0
    print(f"score           : {result.get('deviation_score')} ({result.get('classification')})")
    print(f"offset          : {result.get('offset')}  (of interocular distance)")
    print(f"yaw             : {result.get('yaw')} deg")
    if method != "dorsal_offset":
        print("WARNING: this photo was scored by the LEGACY fallback, not dorsal-offset.")

    ov = result.get("overlay")
    if not ov:
        sys.exit("No overlay was produced for this photo.")

    image = load_image(str(photo))
    drawn = draw_overlay(image, ov, enlarge=5.0 if args.enlarge else 1.0)
    out = Path(args.out) if args.out else photo.with_name(photo.stem + "_overlay.png")
    cv2.imwrite(str(out), drawn)
    print(f"saved           : {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
