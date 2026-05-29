# -*- coding: utf-8 -*-
"""
Contour-based nose analyzer for isolated nose models (3D-printed or standalone).

When MediaPipe cannot detect a full face (e.g., for 3D-printed calibration
models), this module segments the nose by color/contrast and measures
left-right symmetry directly from the contour shape.
"""

import math
import cv2
import numpy as np


def _segment_nose(image):
    """
    Segment the nose object from the background.

    Tries color-based segmentation first (for colored PLA models),
    then falls back to edge/threshold-based segmentation.
    """
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Detect saturated colored objects (3D-printed PLA is typically
    # a vivid single color: green, blue, red, etc.)
    color_mask = cv2.inRange(hsv, (0, 50, 60), (180, 255, 255))
    # Exclude skin-tone hues (roughly H=0-25 with moderate S)
    skin_mask = cv2.inRange(hsv, (0, 30, 60), (25, 170, 255))
    color_mask = cv2.bitwise_and(color_mask, cv2.bitwise_not(skin_mask))

    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
    color_mask = cv2.morphologyEx(color_mask, cv2.MORPH_CLOSE, kernel, iterations=2)
    color_mask = cv2.morphologyEx(color_mask, cv2.MORPH_OPEN, kernel, iterations=1)

    contours, _ = cv2.findContours(color_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        largest = max(contours, key=cv2.contourArea)
        area = cv2.contourArea(largest)
        img_area = image.shape[0] * image.shape[1]
        if area > img_area * 0.02:
            mask = np.zeros(image.shape[:2], dtype=np.uint8)
            cv2.drawContours(mask, [largest], -1, 255, cv2.FILLED)
            return mask

    # Fallback: Otsu thresholding on grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (11, 11), 0)
    _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=2)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        thresh = cv2.bitwise_not(thresh)
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=2)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if contours:
        largest = max(contours, key=cv2.contourArea)
        mask = np.zeros(image.shape[:2], dtype=np.uint8)
        cv2.drawContours(mask, [largest], -1, 255, cv2.FILLED)
        return mask

    return np.zeros(image.shape[:2], dtype=np.uint8)


def _find_bridge_line(contour, bbox):
    """
    Find the ridge/bridge line by computing the horizontal center
    of the contour at each vertical slice.
    Returns list of (x_center, y) from top to bottom.
    """
    x, y, w, h = bbox
    points = contour.reshape(-1, 2)
    bridge = []

    num_slices = min(h, 50)
    for i in range(num_slices):
        y_level = y + int(i * h / num_slices)
        pts_at_y = points[np.abs(points[:, 1] - y_level) <= max(2, h // 100)]
        if len(pts_at_y) >= 2:
            x_min = pts_at_y[:, 0].min()
            x_max = pts_at_y[:, 0].max()
            center_x = (x_min + x_max) / 2.0
            bridge.append((center_x, y_level))

    return bridge


def _measure_nostril_region(mask, contour, bbox):
    """
    Analyze the bottom portion of the nose for nostril asymmetry.
    The bottom 25% typically contains the nostril openings.
    """
    x, y, w, h = bbox
    nostril_top = y + int(h * 0.75)
    nostril_bottom = y + h

    nostril_strip = mask[nostril_top:nostril_bottom, x:x + w]
    if nostril_strip.size == 0:
        return {"left_area": 0, "right_area": 0, "asymmetry": 0.0}

    mid_x = w // 2
    left_half = nostril_strip[:, :mid_x]
    right_half = nostril_strip[:, mid_x:]

    left_area = int(np.count_nonzero(left_half))
    right_area = int(np.count_nonzero(right_half))
    total = left_area + right_area

    asymmetry = abs(left_area - right_area) / total if total > 0 else 0.0

    return {"left_area": left_area, "right_area": right_area, "asymmetry": asymmetry}


def analyze_contour(image):
    """
    Analyze a nose image using contour-based methods.

    Works on isolated nose objects (3D-printed models, clay models, etc.)
    where MediaPipe cannot detect a full face.

    Returns dict with the same metric keys as the landmark-based pipeline:
      lateral_deviation, septal_angle, nostril_asymmetry, bridge_straightness,
      face_width (here: nose_width)
    Or None if no nose-like object is found.
    """
    if image is None or image.size == 0:
        return None

    h_img, w_img = image.shape[:2]
    max_dim = 960
    if max(h_img, w_img) > max_dim:
        scale = max_dim / max(h_img, w_img)
        image = cv2.resize(image, (int(w_img * scale), int(h_img * scale)))
        h_img, w_img = image.shape[:2]

    mask = _segment_nose(image)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None

    contour = max(contours, key=cv2.contourArea)
    area = cv2.contourArea(contour)
    img_area = h_img * w_img
    if area < img_area * 0.01:
        return None

    bbox = cv2.boundingRect(contour)
    bx, by, bw, bh = bbox

    M = cv2.moments(contour)
    if M["m00"] < 1e-6:
        return None
    cx = M["m10"] / M["m00"]
    cy = M["m01"] / M["m00"]

    bbox_center_x = bx + bw / 2.0

    # --- Lateral deviation ---
    # How far the centroid is from the bounding-box center, normalized by width
    lateral_deviation = abs(cx - bbox_center_x) / bw if bw > 0 else 0.0

    # --- Bridge straightness ---
    bridge_points = _find_bridge_line(contour, bbox)
    bridge_dev = 0.0
    if len(bridge_points) >= 3:
        xs = [p[0] for p in bridge_points]
        ref_x = (xs[0] + xs[-1]) / 2.0
        deviations = [abs(x - ref_x) for x in xs]
        bridge_dev = float(np.mean(deviations)) / bw if bw > 0 else 0.0

    # --- Septal angle ---
    # Angle of the line from top-center to bottom-center relative to vertical
    if len(bridge_points) >= 2:
        top = bridge_points[0]
        bot = bridge_points[-1]
        dx = bot[0] - top[0]
        dy = bot[1] - top[1]
        if abs(dy) > 1e-6:
            septal_angle = abs(math.degrees(math.atan2(dx, dy)))
        else:
            septal_angle = 90.0
    else:
        septal_angle = 0.0

    # --- Nostril asymmetry ---
    nostril_info = _measure_nostril_region(mask, contour, bbox)
    nostril_asymmetry = nostril_info["asymmetry"]

    # --- Left/right area symmetry ---
    split_x = int(bbox_center_x)
    left_mask = mask[:, :split_x]
    right_mask = mask[:, split_x:]
    left_total = int(np.count_nonzero(left_mask))
    right_total = int(np.count_nonzero(right_mask))
    area_sum = left_total + right_total
    area_asymmetry = abs(left_total - right_total) / area_sum if area_sum > 0 else 0.0

    # Blend nostril and area asymmetry
    combined_nostril = 0.6 * nostril_asymmetry + 0.4 * area_asymmetry

    # Contour-derived bridge measurements are naturally higher than
    # landmark-based ones; apply a correction factor so the downstream
    # scoring (which uses landmark-tuned scaling) produces sensible
    # results.  Empirically, contour bridge values ~0.08 correspond
    # to landmark values ~0.003 for a straight nose.
    BRIDGE_CORRECTION = 0.15
    corrected_bridge = max(0, bridge_dev - 0.05) * BRIDGE_CORRECTION

    # Similarly, lateral deviation from contour centroid can be offset
    # by the hand holding the model; dampen slightly.
    LATERAL_CORRECTION = 0.5
    corrected_lateral = lateral_deviation * LATERAL_CORRECTION

    return {
        "lateral_deviation": corrected_lateral,
        "septal_angle": septal_angle,
        "nostril_asymmetry": combined_nostril,
        "bridge_straightness": corrected_bridge,
        "face_width": float(bw),
        "analysis_method": "contour",
        "contour_area": float(area),
        "bbox": list(bbox),
        "centroid": (float(cx), float(cy)),
        "nostril_detail": nostril_info,
        "area_asymmetry": area_asymmetry,
        "raw_bridge_dev": bridge_dev,
        "raw_lateral_dev": lateral_deviation,
    }
