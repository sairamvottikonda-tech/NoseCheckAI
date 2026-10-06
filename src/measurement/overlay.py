"""
Measurement overlay for the result screen.

Turns the points the dorsal-offset measurement used into coordinates the
browser can draw over the user's own photo: the reference midline
(inner-canthus midpoint -> philtrum) and the dorsum sample points.

DISPLAY ONLY. Nothing here feeds the score. The point of drawing it is so a
person (or a clinician) can see what was measured and spot a misplaced
landmark, which is the main way this measurement can quietly go wrong.

Coordinates are returned normalised 0..1 against the ORIGINAL (EXIF-upright)
photo, so the frontend can draw at any display size. The measurement itself
runs on a letterboxed, resized copy; letterbox_geometry() undoes that.
"""

from src.image_processing.preprocessor import letterbox_geometry

# How far the drawn midline extends past the two anchors, as a fraction of
# the anchor-to-anchor distance. Purely cosmetic.
_EXTEND_ABOVE = 0.45
_EXTEND_BELOW = 0.35


def _to_original(pt, geom):
    """Preprocessed-canvas pixel -> original photo, normalised 0..1."""
    x = (pt[0] - geom["left"]) / geom["new_w"]
    y = (pt[1] - geom["top"]) / geom["new_h"]
    return [round(x, 5), round(y, 5)]


def build_overlay(points_px, orig_w, orig_h, max_idx=None):
    """
    Args:
        points_px: the "points_px" dict from compute_dorsal_offset(), in
            preprocessed-canvas pixels.
        orig_w, orig_h: size of the original upright photo.
        max_idx: landmark index with the largest offset (highlighted).

    Returns:
        JSON-serialisable dict, coordinates normalised to the original photo.
    """
    geom = letterbox_geometry(orig_w, orig_h)

    cm = points_px["canthal_mid"]
    ph = points_px["philtrum"]
    dx, dy = ph[0] - cm[0], ph[1] - cm[1]
    top = [cm[0] - _EXTEND_ABOVE * dx, cm[1] - _EXTEND_ABOVE * dy]
    bottom = [ph[0] + _EXTEND_BELOW * dx, ph[1] + _EXTEND_BELOW * dy]

    dorsum = []
    for i, (idx, pt) in enumerate(points_px["dorsum"].items()):
        x, y = _to_original(pt, geom)
        dorsum.append({
            "id": int(idx),
            "x": x,
            "y": y,
            # The first dorsum point (168) sits at the reference end and is
            # not scored; it is drawn but not eligible to be the maximum.
            "scored": i != 0,
        })

    return {
        "midline": {"top": _to_original(top, geom),
                    "bottom": _to_original(bottom, geom)},
        "anchors": {"canthal_mid": _to_original(cm, geom),
                    "philtrum": _to_original(ph, geom)},
        "dorsum": dorsum,
        "max_id": None if max_idx is None else int(max_idx),
    }
