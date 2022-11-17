import numpy as np


def custom_mad(data, axis=None):
    if np.unique(data).size > 0:
        median = np.median(data, axis) if len(data) > 0 else 0.0
        den = np.absolute(data - median)
        return np.mean(den) if np.unique(den).size > 0 else []
    else:
        return []


def custom_zscore(points, const: float = 0.6745):

    if np.unique(points).size > 0:
        median = np.median(points)
        _mad = custom_mad(points)
        outl = [const * (c - median) / _mad for c in points] if _mad != 0.0 else []
        return np.array(outl) if np.unique(outl).size > 0 else np.array([])
    else:
        return np.array([])
