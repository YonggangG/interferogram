# Technical Design

## 1. Proposed architecture

The recommended implementation is a Python algorithm core with a local web interface.

```text
Browser UI
  -> FastAPI backend
    -> image preprocessing module
    -> ROI / rectangular aperture module
    -> Fourier phase extraction module
    -> phase unwrapping module
    -> wavefront conversion module
    -> fitting and metrics module
    -> report generation module
```

This architecture keeps the algorithm easy to test while allowing later packaging as a Windows executable or deployment as a local lab web service.

## 2. Core Python dependencies

Likely dependencies:

- `numpy` for arrays and numerical operations
- `scipy` for FFT, filters, and least-squares fitting
- `opencv-python` for image preprocessing and rectangle detection
- `scikit-image` for phase unwrapping and image utilities
- `matplotlib` or `plotly` for diagnostic plots
- `pandas` for CSV/table output
- `fastapi` + `uvicorn` for web service mode
- optional: `prysm` for interferogram and Zernike reference logic

Useful open-source references:

- `harmenhoek/InterferometryPython`: Fourier-space filtering of single-wavelength interferometry images.
- `githubdoe/DFTFringe`: complete interferometry analysis program, useful as architecture and Zernike reference, although mainly telescope/circular-aperture oriented.
- `prysm`: interferometric wavefront analysis examples, PV/RMS operations, Zernike fitting concepts.
- `scikit-image`: `restoration.unwrap_phase` for phase unwrapping.

## 3. Processing pipeline

### 3.1 Image ingestion

Inputs may be:

1. Direct fringe image.
2. Zygo-style screenshot containing a fringe image and reference metrics.

For screenshots, the MVP should initially allow manual crop selection or semi-automatic extraction of the fringe panel. Automatic screenshot parsing can be added after sample images are received.

### 3.2 Preprocessing

Steps:

1. Convert to grayscale.
2. Normalize intensity.
3. Remove large-scale illumination background using a large Gaussian blur or morphological opening.
4. Enhance local contrast using CLAHE if needed.
5. Apply denoising with a small median or Gaussian filter.

### 3.3 Rectangular ROI and mask

Steps:

1. Detect rectangular aperture by contour detection or allow manual four-corner selection.
2. Estimate rectangle with `cv2.minAreaRect` or four-point perspective transform.
3. Warp the ROI to a canonical rectangle.
4. Generate a boolean valid-data mask.
5. Apply a small edge margin to avoid boundary artifacts.
6. Normalize coordinates:
   - center at `(0, 0)`
   - x and y scaled to `[-1, 1]` or to physical dimensions in mm

### 3.4 Fourier carrier phase extraction

For high-frequency, mostly parallel fringes:

1. Compute 2D FFT of preprocessed ROI.
2. Suppress the DC/low-frequency center.
3. Detect the strongest carrier peak.
4. Apply a bandpass window around the selected carrier peak.
5. Shift the selected sideband to the origin.
6. Inverse FFT to obtain a complex analytic signal.
7. Compute wrapped phase using `angle(complex_signal)`.

This follows the classic Fourier-transform method for fringe-pattern analysis.

### 3.5 Phase unwrapping

Use masked phase unwrapping when possible. Initial implementation can use:

```python
skimage.restoration.unwrap_phase(wrapped_phase)
```

The unwrapped phase should be quality-checked for discontinuities and obvious unwrap failures.

### 3.6 Unit conversion

Let `phi` be unwrapped optical phase in radians.

Wavefront error in waves:

```text
W_waves = phi / (2π)
```

Wavefront error in nm:

```text
W_nm = W_waves × wavelength_nm
```

For reflective surface error:

```text
surface_error_nm = W_nm / 2
```

The software must always state whether reported values are wavefront error or surface error.

## 4. Metrics and fitting

### 4.1 Piston, tilt, and power removal

Low-order rectangular fit:

```text
W(x, y) = a00 + a10*x + a01*y + a20*x² + a02*y² + a11*x*y + ...
```

Initial fit basis:

- piston: `1`
- x tilt: `x`
- y tilt: `y`
- x power / curvature: `x²`
- y power / curvature: `y²`
- saddle / astig-like term: `x*y`

### 4.2 P-V

```text
PV = max(W_valid) - min(W_valid)
```

The selected term-removal state must be recorded. Raw P-V and term-removed P-V should be distinguished.

### 4.3 RMS

```text
RMS = std(W_valid - mean(W_valid))
```

### 4.4 Power

For rectangular apertures, report:

- X Power from the `x²` coefficient
- Y Power from the `y²` coefficient
- Mean Power from the average of X/Y curvature terms
- Optional astig-like difference between X and Y curvature terms

The exact conversion to waves over aperture must be calibrated against validation data and documented.

### 4.5 Irregularity

Recommended definition:

```text
Irregularity = P-V of residual after removing piston, tilt, and power terms
```

Residual:

```text
R = W - W_low_order
```

Then:

```text
Irregularity = max(R_valid) - min(R_valid)
```

### 4.6 Zernike-equivalent terms

Because the aperture is rectangular, standard circular Zernike terms are not orthogonal over the valid domain. However, for compatibility with commercial reports, the system can fit Zernike terms over the rectangular sample points by least squares.

The report must label these as:

```text
Zernike-equivalent coefficients fitted over rectangular mask
```

A rectangular Legendre or XY polynomial basis should be considered the primary basis for engineering interpretation.

## 5. Reporting

Per-image report should include:

- Input image and detected/cropped fringe ROI
- FFT spectrum and selected carrier peak
- Wrapped phase map
- Unwrapped wavefront map
- Low-order fitted surface
- Residual map
- Metrics table
- Coefficients table
- Unit and wavelength settings

Batch report should include:

- One-row summary per face
- Ranking / worst face
- Optional tolerance pass/fail
- Export as CSV and HTML/PDF

## 6. Risks

Main risks:

- Incorrect carrier peak selection.
- Phase unwrap errors near low-contrast regions.
- Confusion between wavefront error and surface error.
- Mismatch between our Power/Irregularity definitions and Zygo-specific conventions.
- Rectangular Zernike coefficients being over-interpreted.

Mitigation:

- Keep diagnostic images for every processing stage.
- Validate against known Zygo outputs.
- Make term-removal settings explicit.
- Prefer rectangular polynomial terms as primary results.
