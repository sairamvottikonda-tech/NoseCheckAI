"""
Pure-computation statistics module for NoseCheck validation.

No heavy dependencies -- uses only math and builtins.
Safe for production (Render 512MB free tier).
"""

import math
from typing import Dict, List, Optional, Tuple


def pearson_r(x: List[float], y: List[float]) -> float:
    """Pearson correlation coefficient between two equal-length lists."""
    n = len(x)
    if n < 2 or n != len(y):
        return 0.0

    mean_x = sum(x) / n
    mean_y = sum(y) / n

    ss_xy = sum((xi - mean_x) * (yi - mean_y) for xi, yi in zip(x, y))
    ss_xx = sum((xi - mean_x) ** 2 for xi in x)
    ss_yy = sum((yi - mean_y) ** 2 for yi in y)

    denom = math.sqrt(ss_xx * ss_yy)
    if denom == 0:
        return 0.0
    return ss_xy / denom


def r_squared(x: List[float], y: List[float]) -> float:
    """Coefficient of determination (R^2)."""
    r = pearson_r(x, y)
    return r * r


def linear_regression(
    x: List[float], y: List[float]
) -> Dict[str, float]:
    """
    Simple linear regression: y = slope * x + intercept.

    Returns dict with slope, intercept, r, r_squared, and p_value_approx.
    """
    n = len(x)
    if n < 2 or n != len(y):
        return {"slope": 0, "intercept": 0, "r": 0, "r_squared": 0, "p_value_approx": 1.0}

    mean_x = sum(x) / n
    mean_y = sum(y) / n

    ss_xy = sum((xi - mean_x) * (yi - mean_y) for xi, yi in zip(x, y))
    ss_xx = sum((xi - mean_x) ** 2 for xi in x)

    if ss_xx == 0:
        return {"slope": 0, "intercept": mean_y, "r": 0, "r_squared": 0, "p_value_approx": 1.0}

    slope = ss_xy / ss_xx
    intercept = mean_y - slope * mean_x
    r = pearson_r(x, y)
    r_sq = r * r

    p_value = 1.0
    if n > 2 and abs(r) < 1.0:
        t_stat = r * math.sqrt((n - 2) / (1 - r * r))
        df = n - 2
        p_value = 2.0 * (1.0 - _t_cdf_approx(abs(t_stat), df))

    return {
        "slope": slope,
        "intercept": intercept,
        "r": r,
        "r_squared": r_sq,
        "p_value_approx": max(0.0, min(1.0, p_value)),
    }


def _t_cdf_approx(t: float, df: int) -> float:
    """Approximate CDF of Student's t-distribution."""
    if df <= 0:
        return 0.5
    z = t * (1 - 1 / (4 * df)) / math.sqrt(1 + t * t / (2 * df))
    return _norm_cdf(z)


def _norm_cdf(x: float) -> float:
    """Standard normal CDF (Abramowitz & Stegun 26.2.17)."""
    if x < -8:
        return 0.0
    if x > 8:
        return 1.0
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2)))


def rmse(actual: List[float], predicted: List[float]) -> float:
    """Root mean square error between two lists."""
    n = len(actual)
    if n == 0 or n != len(predicted):
        return 0.0
    mse = sum((a - p) ** 2 for a, p in zip(actual, predicted)) / n
    return math.sqrt(mse)


def descriptive_stats(values: List[float]) -> Dict[str, float]:
    """Mean, std, min, max, median, IQR for a list of floats."""
    if not values:
        return {"mean": 0, "std": 0, "min": 0, "max": 0, "median": 0, "q1": 0, "q3": 0, "iqr": 0, "n": 0}

    n = len(values)
    sorted_v = sorted(values)
    mean = sum(values) / n
    variance = sum((v - mean) ** 2 for v in values) / max(1, n - 1)
    std = math.sqrt(variance)

    def _percentile(data, p):
        k = (len(data) - 1) * p / 100.0
        f = math.floor(k)
        c = math.ceil(k)
        if f == c:
            return data[int(k)]
        return data[int(f)] * (c - k) + data[int(c)] * (k - f)

    median = _percentile(sorted_v, 50)
    q1 = _percentile(sorted_v, 25)
    q3 = _percentile(sorted_v, 75)

    return {
        "mean": mean,
        "std": std,
        "min": sorted_v[0],
        "max": sorted_v[-1],
        "median": median,
        "q1": q1,
        "q3": q3,
        "iqr": q3 - q1,
        "n": n,
    }


def category_accuracy(
    expected: List[str], actual: List[str]
) -> Dict[str, object]:
    """
    Per-category precision/recall and overall accuracy.

    Returns dict with overall_accuracy, per_category, n, correct.
    """
    if not expected or len(expected) != len(actual):
        return {"overall_accuracy": 0, "per_category": {}, "n": 0}

    n = len(expected)
    correct = sum(1 for e, a in zip(expected, actual) if e == a)

    categories = sorted(set(expected) | set(actual))
    per_cat = {}
    for cat in categories:
        cat_total = sum(1 for e in expected if e == cat)
        cat_correct = sum(1 for e, a in zip(expected, actual) if e == cat and a == cat)
        per_cat[cat] = {
            "correct": cat_correct,
            "total": cat_total,
            "accuracy": cat_correct / cat_total if cat_total > 0 else 0.0,
        }

    return {
        "overall_accuracy": correct / n if n > 0 else 0.0,
        "per_category": per_cat,
        "n": n,
        "correct": correct,
    }
