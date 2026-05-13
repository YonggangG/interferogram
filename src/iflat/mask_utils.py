"""Mask utilities for Zygo screenshot fringe ROI crops."""

from __future__ import annotations

import numpy as np
from scipy import ndimage as ndi
from skimage import filters, morphology


def aperture_mask(gray: np.ndarray, edge_margin_px: int = 8) -> np.ndarray:
    """Estimate the visible interferogram aperture mask from a grayscale ROI.

    The Zygo screenshots place the fringe image on a very dark UI panel. This
    threshold-based mask excludes the black panel and keeps the bright aperture.
    """
    arr = np.asarray(gray, dtype=float)
    arr_norm = (arr - np.nanmin(arr)) / max(np.nanmax(arr) - np.nanmin(arr), 1e-9)
    try:
        thr = filters.threshold_otsu(arr_norm)
    except ValueError:
        thr = 0.1
    # Keep pixels brighter than the dark panel. Otsu may be too high for fringes,
    # so cap the threshold conservatively.
    mask = arr_norm > min(thr, 0.18)
    mask = morphology.remove_small_objects(mask, min_size=max(64, arr.size // 500))
    mask = ndi.binary_fill_holes(mask)
    mask = morphology.binary_opening(mask, morphology.disk(2))
    mask = morphology.binary_closing(mask, morphology.disk(3))
    if edge_margin_px > 0:
        mask = ndi.binary_erosion(mask, iterations=edge_margin_px)
    return mask.astype(bool)
