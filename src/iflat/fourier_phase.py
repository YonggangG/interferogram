"""Fourier-carrier phase extraction prototype.

This module implements the first-pass high-carrier fringe path. It is intentionally
small and diagnostic-friendly; convention matching against Zygo references will
come after the initial maps are produced.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy import ndimage as ndi
from skimage.restoration import unwrap_phase


@dataclass(frozen=True)
class PhaseExtractionResult:
    wrapped_phase: np.ndarray
    unwrapped_phase: np.ndarray
    wavefront_waves: np.ndarray
    carrier_peak: tuple[int, int]
    filter_radius_px: int
    method: str = "circular"


def normalize_image(gray: np.ndarray) -> np.ndarray:
    """Normalize image to float range [0, 1]."""
    arr = np.asarray(gray, dtype=float)
    lo, hi = np.nanpercentile(arr, [1, 99])
    if hi <= lo:
        return np.zeros_like(arr, dtype=float)
    return np.clip((arr - lo) / (hi - lo), 0, 1)


def prepare_fft_image(gray: np.ndarray, mask: np.ndarray | None = None, sigma: float = 12.0) -> np.ndarray:
    """Normalize, background-correct, mask-fill, and window an image for FFT."""
    img = normalize_image(gray)
    background = ndi.gaussian_filter(img, sigma=sigma)
    img = img - background
    if mask is not None:
        mask_bool = np.asarray(mask, dtype=bool)
        valid_mean = float(np.nanmean(img[mask_bool]))
        img = np.where(mask_bool, img, valid_mean)
        # Taper image edges and mask boundary to reduce FFT leakage.
        dist = ndi.distance_transform_edt(mask_bool)
        taper = np.clip(dist / 8.0, 0, 1)
        img = img * taper
    else:
        h, w = img.shape
        img = img * np.outer(np.hanning(h), np.hanning(w))
    img = img - np.nanmean(img)
    return img


def find_carrier_peak(spectrum: np.ndarray, dc_radius: int = 20) -> tuple[int, int]:
    """Find strongest non-DC FFT sideband peak."""
    return find_carrier_candidates(spectrum, dc_radius=dc_radius, count=1)[0]


def find_carrier_candidates(spectrum: np.ndarray, dc_radius: int = 20, count: int = 12) -> list[tuple[int, int]]:
    """Find non-DC local maxima that may be FFT sideband carrier peaks."""
    mag = np.abs(spectrum).copy()
    h, w = mag.shape
    cy, cx = h // 2, w // 2
    yy, xx = np.indices(mag.shape)
    mag[(xx - cx) ** 2 + (yy - cy) ** 2 <= dc_radius**2] = 0
    # Suppress extreme corners, which are usually noise/edge leakage for these crops.
    mag[(xx < 3) | (yy < 3) | (xx > w - 4) | (yy > h - 4)] = 0
    local_max = mag == ndi.maximum_filter(mag, size=5)
    coords = np.argwhere(local_max & (mag > 0))
    coords = sorted(coords, key=lambda p: mag[tuple(p)], reverse=True)
    candidates: list[tuple[int, int]] = []
    for py, px in coords:
        p = (int(py), int(px))
        if all((py - qy) ** 2 + (px - qx) ** 2 > 6**2 for qy, qx in candidates):
            candidates.append(p)
        if len(candidates) >= count:
            break
    return candidates


def circular_window(shape: tuple[int, int], center: tuple[int, int], radius: int) -> np.ndarray:
    """Create a soft circular Hann-like sideband window."""
    h, w = shape
    cy, cx = center
    yy, xx = np.indices(shape)
    r = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
    win = np.zeros(shape, dtype=float)
    inside = r <= radius
    win[inside] = 0.5 * (1 + np.cos(np.pi * r[inside] / max(radius, 1)))
    return win


def gaussian_window(
    shape: tuple[int, int],
    center: tuple[int, int],
    sigma_major: float,
    sigma_minor: float | None = None,
    angle_rad: float = 0.0,
) -> np.ndarray:
    """Create a rotated elliptical Gaussian sideband window."""
    if sigma_minor is None:
        sigma_minor = sigma_major
    h, w = shape
    cy, cx = center
    yy, xx = np.indices(shape)
    x = xx - cx
    y = yy - cy
    ca, sa = np.cos(angle_rad), np.sin(angle_rad)
    xr = ca * x + sa * y
    yr = -sa * x + ca * y
    return np.exp(-0.5 * ((xr / sigma_major) ** 2 + (yr / sigma_minor) ** 2))


def extract_phase_fft_at_peak(
    gray: np.ndarray,
    peak: tuple[int, int],
    filter_radius_px: int,
    mask: np.ndarray | None = None,
    method: str = "gaussian",
    ellipse_ratio: float = 0.65,
    angle_rad: float = 0.0,
) -> PhaseExtractionResult:
    """Extract phase using a specified carrier peak and filter."""
    img = prepare_fft_image(gray, mask=mask)
    spectrum = np.fft.fftshift(np.fft.fft2(img))
    h, w = img.shape
    if method == "circular":
        window = circular_window(spectrum.shape, peak, filter_radius_px)
    elif method == "gaussian":
        window = gaussian_window(spectrum.shape, peak, filter_radius_px, filter_radius_px * ellipse_ratio, angle_rad)
    else:
        raise ValueError(f"Unknown FFT filter method: {method}")
    sideband = spectrum * window

    cy, cx = h // 2, w // 2
    py, px = peak
    shifted = np.roll(sideband, shift=(cy - py, cx - px), axis=(0, 1))
    analytic = np.fft.ifft2(np.fft.ifftshift(shifted))
    wrapped = np.angle(analytic)
    if mask is not None:
        wrapped_for_unwrap = np.ma.array(wrapped, mask=~np.asarray(mask, dtype=bool))
        unwrapped_ma = unwrap_phase(wrapped_for_unwrap)
        unwrapped = np.asarray(unwrapped_ma.filled(np.nan), dtype=float)
    else:
        unwrapped = unwrap_phase(wrapped)
    wavefront_waves = unwrapped / (2 * np.pi)
    return PhaseExtractionResult(
        wrapped_phase=wrapped,
        unwrapped_phase=unwrapped,
        wavefront_waves=wavefront_waves,
        carrier_peak=peak,
        filter_radius_px=int(filter_radius_px),
        method=method,
    )


def extract_phase_fft(
    gray: np.ndarray,
    filter_radius_px: int | None = None,
    mask: np.ndarray | None = None,
) -> PhaseExtractionResult:
    """Extract phase from a high-carrier interferogram using FFT sideband filtering."""
    img = prepare_fft_image(gray, mask=mask)
    spectrum = np.fft.fftshift(np.fft.fft2(img))
    h, w = img.shape
    peak = find_carrier_peak(spectrum, dc_radius=max(6, min(h, w) // 18))
    if filter_radius_px is None:
        filter_radius_px = max(5, min(h, w) // 12)
    return extract_phase_fft_at_peak(
        gray,
        peak=peak,
        filter_radius_px=filter_radius_px,
        mask=mask,
        method="gaussian",
    )
