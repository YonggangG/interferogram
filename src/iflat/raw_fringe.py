"""Raw/direct fringe analysis mode."""

from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Sequence

import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageDraw

from .fourier_phase import extract_phase_fft_at_peak, find_carrier_candidates, prepare_fft_image
from .metrics import fit_polynomial


@dataclass(frozen=True)
class RawFringeResult:
    mode: str
    input_file: str
    crop_file: str
    bbox: list[int] | None
    wavelength_nm: float
    values_are: str
    selected_peak: list[int]
    selected_radius: int
    selected_ellipse_ratio: float
    pv_after_tilt_waves: float
    rms_after_tilt_waves: float
    power_x_coeff_waves: float
    power_y_coeff_waves: float
    power_mean_coeff_waves: float
    irregularity_after_tilt_power_waves: float
    residual_rms_waves: float
    pv_after_tilt_nm_wavefront: float
    rms_after_tilt_nm_wavefront: float
    irregularity_nm_wavefront: float
    residual_rms_nm_wavefront: float
    pv_after_tilt_nm_surface_reflection: float
    rms_after_tilt_nm_surface_reflection: float
    irregularity_nm_surface_reflection: float
    residual_rms_nm_surface_reflection: float
    report_image: str
    metrics_json: str
    caution: str


def _edge_mask(shape: tuple[int, int], margin: int = 3) -> np.ndarray:
    mask = np.ones(shape, dtype=bool)
    mask[:margin, :] = False
    mask[-margin:, :] = False
    mask[:, :margin] = False
    mask[:, -margin:] = False
    return mask


def _pv_rms(arr: np.ndarray) -> tuple[float, float]:
    v = arr[np.isfinite(arr)]
    return float(np.nanmax(v) - np.nanmin(v)), float(np.nanstd(v - np.nanmean(v)))


def _save_map(path: Path, arr: np.ndarray, title: str, cmap: str = "RdBu_r") -> None:
    plt.figure(figsize=(4.5, 3.5))
    plt.imshow(arr, cmap=cmap)
    plt.colorbar(label="waves")
    plt.title(title)
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(path, dpi=160)
    plt.close()


def _auto_center_bbox(image: Image.Image) -> list[int]:
    """Conservative fallback crop: central 55% region.

    Production callers should provide the detected/selected aperture bbox.
    """
    w, h = image.size
    side_w = int(w * 0.55)
    side_h = int(h * 0.55)
    x1 = (w - side_w) // 2
    y1 = (h - side_h) // 2
    return [x1, y1, x1 + side_w, y1 + side_h]


def _score_solution(pv_tilt: float, rms_tilt: float, irr: float, radius: int) -> float:
    return irr + 0.25 * rms_tilt + 0.02 * max(pv_tilt - 1.0, 0) + 0.002 * radius


def analyze_raw_fringe(
    image_path: str | Path,
    output_dir: str | Path,
    bbox: Sequence[int] | None = None,
    wavelength_nm: float = 633.0,
    values_are: str = "wavefront_error",
) -> RawFringeResult:
    """Analyze a direct/raw fringe image using FFT carrier demodulation.

    This mode is intended for direct interferogram intensity images. Photographed
    screenshots can run, but are marked prototype-level because camera gamma,
    saturation, and perspective can bias phase recovery.
    """
    image_path = Path(image_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    image = Image.open(image_path).convert("RGB")
    bbox_list = list(map(int, bbox)) if bbox is not None else _auto_center_bbox(image)
    crop = image.crop(tuple(bbox_list))
    crop_file = output_dir / "fringe_crop.png"
    crop.save(crop_file)

    gray = np.asarray(crop.convert("L"), dtype=float)
    mask = _edge_mask(gray.shape)
    prepared = prepare_fft_image(gray, mask=mask)
    spectrum = np.fft.fftshift(np.fft.fft2(prepared))
    candidates = find_carrier_candidates(spectrum, dc_radius=max(4, min(gray.shape) // 18), count=10)

    best = None
    rows = []
    for peak in candidates:
        py, px = peak
        angle = np.arctan2(py - gray.shape[0] // 2, px - gray.shape[1] // 2)
        for radius in range(3, 18):
            for ratio in (0.45, 0.65, 0.9, 1.0):
                try:
                    result = extract_phase_fft_at_peak(
                        gray,
                        peak=peak,
                        filter_radius_px=radius,
                        mask=mask,
                        method="gaussian",
                        ellipse_ratio=ratio,
                        angle_rad=angle,
                    )
                    wf = result.wavefront_waves - np.nanmean(result.wavefront_waves[mask])
                    tilt_fit, _ = fit_polynomial(wf, mask, terms=("piston", "tilt_x", "tilt_y"))
                    tilt_removed = wf - tilt_fit
                    pv_tilt, rms_tilt = _pv_rms(tilt_removed[mask])
                    power_fit, coeffs = fit_polynomial(
                        wf, mask, terms=("piston", "tilt_x", "tilt_y", "power_x", "power_y")
                    )
                    residual = wf - power_fit
                    irr, residual_rms = _pv_rms(residual[mask])
                    score = _score_solution(pv_tilt, rms_tilt, irr, radius)
                    row = {
                        "peak_y": py,
                        "peak_x": px,
                        "radius": radius,
                        "ellipse_ratio": ratio,
                        "pv_after_tilt_waves": pv_tilt,
                        "rms_after_tilt_waves": rms_tilt,
                        "irregularity_after_tilt_power_waves": irr,
                        "residual_rms_waves": residual_rms,
                        "power_x_coeff": float(coeffs.get("power_x", 0.0)),
                        "power_y_coeff": float(coeffs.get("power_y", 0.0)),
                        "power_mean_coeff": float((coeffs.get("power_x", 0.0) + coeffs.get("power_y", 0.0)) / 2),
                        "score": score,
                    }
                    rows.append(row)
                    candidate = (score, row, wf, tilt_removed, residual)
                    if best is None or score < best[0]:
                        best = candidate
                except Exception:
                    continue
    if best is None:
        raise RuntimeError("No valid FFT demodulation solution found")

    _, row, wf, tilt_removed, residual = best
    _save_map(output_dir / "wavefront_raw.png", wf, "Raw unwrapped wavefront")
    _save_map(output_dir / "tilt_removed.png", tilt_removed, "Tilt-removed wavefront")
    _save_map(output_dir / "residual_irregularity.png", residual, "Residual after tilt + power")

    annotated = image.copy()
    draw = ImageDraw.Draw(annotated)
    draw.rectangle(tuple(bbox_list), outline="yellow", width=3)
    annotated_file = output_dir / "input_with_crop.png"
    annotated.save(annotated_file)

    report_file = output_dir / "diagnostic_report_with_metrics.png"
    _write_report_image(annotated_file, output_dir / "tilt_removed.png", output_dir / "residual_irregularity.png", report_file, row, wavelength_nm)

    with (output_dir / "sweep.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(sorted(rows, key=lambda r: r["score"]))

    result = RawFringeResult(
        mode="raw_direct_fringe",
        input_file=str(image_path),
        crop_file=str(crop_file),
        bbox=bbox_list,
        wavelength_nm=wavelength_nm,
        values_are=values_are,
        selected_peak=[int(row["peak_y"]), int(row["peak_x"])],
        selected_radius=int(row["radius"]),
        selected_ellipse_ratio=float(row["ellipse_ratio"]),
        pv_after_tilt_waves=float(row["pv_after_tilt_waves"]),
        rms_after_tilt_waves=float(row["rms_after_tilt_waves"]),
        power_x_coeff_waves=float(row["power_x_coeff"]),
        power_y_coeff_waves=float(row["power_y_coeff"]),
        power_mean_coeff_waves=float(row["power_mean_coeff"]),
        irregularity_after_tilt_power_waves=float(row["irregularity_after_tilt_power_waves"]),
        residual_rms_waves=float(row["residual_rms_waves"]),
        pv_after_tilt_nm_wavefront=float(row["pv_after_tilt_waves"] * wavelength_nm),
        rms_after_tilt_nm_wavefront=float(row["rms_after_tilt_waves"] * wavelength_nm),
        irregularity_nm_wavefront=float(row["irregularity_after_tilt_power_waves"] * wavelength_nm),
        residual_rms_nm_wavefront=float(row["residual_rms_waves"] * wavelength_nm),
        pv_after_tilt_nm_surface_reflection=float(row["pv_after_tilt_waves"] * wavelength_nm / 2),
        rms_after_tilt_nm_surface_reflection=float(row["rms_after_tilt_waves"] * wavelength_nm / 2),
        irregularity_nm_surface_reflection=float(row["irregularity_after_tilt_power_waves"] * wavelength_nm / 2),
        residual_rms_nm_surface_reflection=float(row["residual_rms_waves"] * wavelength_nm / 2),
        report_image=str(report_file),
        metrics_json=str(output_dir / "metrics.json"),
        caution="Prototype estimate unless input is raw/direct interferogram intensity data with calibrated geometry.",
    )
    (output_dir / "metrics.json").write_text(json.dumps(asdict(result), indent=2), encoding="utf-8")
    return result


def _write_report_image(input_path: Path, tilt_path: Path, residual_path: Path, out: Path, row: dict[str, float], wavelength_nm: float) -> None:
    input_img = Image.open(input_path).convert("RGB")
    tilt_img = Image.open(tilt_path).convert("RGB")
    resid_img = Image.open(residual_path).convert("RGB")
    fig = plt.figure(figsize=(14, 9), facecolor="white")
    gs = fig.add_gridspec(2, 3, height_ratios=[1, 0.55])
    for ax, img, title in zip(
        [fig.add_subplot(gs[0, i]) for i in range(3)],
        [input_img, tilt_img, resid_img],
        ["Input with selected fringe ROI", "Tilt-removed wavefront map", "Residual after tilt + power"],
    ):
        ax.imshow(img)
        ax.set_title(title, fontsize=13, weight="bold")
        ax.axis("off")
    ax_text = fig.add_subplot(gs[1, :])
    ax_text.axis("off")
    text = (
        f"FFT fringe analysis ({wavelength_nm:g} nm, wavefront error)\n\n"
        f"P-V after tilt removal: {row['pv_after_tilt_waves']:.3f} λ = {row['pv_after_tilt_waves'] * wavelength_nm:.1f} nm wavefront | {row['pv_after_tilt_waves'] * wavelength_nm / 2:.1f} nm surface (reflection)\n"
        f"RMS after tilt removal: {row['rms_after_tilt_waves']:.3f} λ = {row['rms_after_tilt_waves'] * wavelength_nm:.1f} nm wavefront | {row['rms_after_tilt_waves'] * wavelength_nm / 2:.1f} nm surface (reflection)\n"
        f"Power mean coefficient: {row['power_mean_coeff']:.3f} λ (X: {row['power_x_coeff']:.3f} λ, Y: {row['power_y_coeff']:.3f} λ)\n"
        f"Irregularity after tilt + power removal: {row['irregularity_after_tilt_power_waves']:.3f} λ = {row['irregularity_after_tilt_power_waves'] * wavelength_nm:.1f} nm wavefront | {row['irregularity_after_tilt_power_waves'] * wavelength_nm / 2:.1f} nm surface (reflection)\n"
        f"Residual RMS: {row['residual_rms_waves']:.3f} λ = {row['residual_rms_waves'] * wavelength_nm:.1f} nm wavefront | {row['residual_rms_waves'] * wavelength_nm / 2:.1f} nm surface (reflection)\n\n"
        "Caution: prototype-level unless input is raw calibrated interferogram data."
    )
    ax_text.text(0.01, 0.95, text, va="top", ha="left", fontsize=13, family="DejaVu Sans Mono", bbox=dict(boxstyle="round", facecolor="#f7f7f7", edgecolor="#cccccc"))
    fig.tight_layout()
    fig.savefig(out, dpi=160, bbox_inches="tight")
    plt.close(fig)
