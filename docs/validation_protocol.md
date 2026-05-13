# Validation Protocol

## 1. Purpose

The project must be validated against trusted commercial interferometer outputs before its numerical results are treated as metrology-grade.

The first validation source will be six Zygo-style screenshots supplied by the user. Each screenshot is expected to contain both the fringe pattern image and displayed wavefront-error outputs.

## 2. Validation dataset

Initial dataset:

- Six screenshots, ideally one for each face of a hexagon scanning mirror.
- Each screenshot should include the fringe image and visible metrics such as P-V, RMS, Power, and Irregularity if available.
- Wavelength should be known, default assumed to be 633 nm unless the screenshot or user notes say otherwise.

Preferred filename convention:

```text
face_01_zygo.png
face_02_zygo.png
face_03_zygo.png
face_04_zygo.png
face_05_zygo.png
face_06_zygo.png
```

## 3. Reference data extraction

For each screenshot, manually or semi-automatically record:

- Face ID
- Reference wavelength
- Zygo P-V
- Zygo RMS
- Zygo Power
- Zygo Irregularity
- Whether values are wavefront error or surface error
- Any displayed removed terms or analysis settings
- Fringe ROI crop location

A validation manifest should be created as CSV or JSON.

Example JSON record:

```json
{
  "face_id": "face_01",
  "source_file": "face_01_zygo.png",
  "wavelength_nm": 633.0,
  "reference_units": "waves",
  "reference_type": "wavefront_error",
  "zygo": {
    "pv_waves": 0.289,
    "rms_waves": 0.044,
    "power_waves": -0.056,
    "irregularity_waves": 0.329
  },
  "notes": "Example values only. Replace with real extracted values."
}
```

## 4. Algorithm validation steps

For each screenshot:

1. Crop or extract the fringe ROI.
2. Run preprocessing.
3. Detect or define rectangular aperture.
4. Run Fourier carrier phase extraction.
5. Unwrap phase.
6. Convert to wavefront/surface units.
7. Compute metrics using documented term-removal settings.
8. Compare against Zygo reference values.
9. Save diagnostics and residual maps.

## 5. Metrics for comparison

For each metric:

```text
absolute_error = measured - reference
relative_error = absolute_error / reference
```

Report:

- Mean absolute error across six faces
- Maximum absolute error
- Mean relative error
- Maximum relative error
- Per-face discrepancy notes

## 6. Initial acceptance targets

For suitable high-carrier screenshots:

- P-V: within 10–15% of reference
- RMS: within 10–15% of reference
- Power: within 10–20% initially, then improve after convention matching
- Irregularity: within 10–20% initially, then improve after term-removal matching

The early tolerance is intentionally loose because screenshots may include compression artifacts, rescaling, and uncertain internal Zygo processing settings.

## 7. Known validation limitations

Screenshots are not ideal raw metrology data. They may have:

- Downsampled or compressed fringe images
- UI scaling artifacts
- Unknown gamma correction
- Cropped or non-original fringe regions
- Unknown Zygo internal filtering and term-removal conventions

If direct raw interferogram images or phase maps become available, they should be preferred for quantitative validation.

## 8. Decision gates

### Gate 1: Feasibility

At least 4 of 6 screenshots produce plausible wavefront maps with no major unwrap failures.

### Gate 2: Metric agreement

P-V and RMS are within approximately 15% of reference on most images.

### Gate 3: Batch utility

Six-face report gives stable relative ranking of mirror faces.

### Gate 4: Production direction

If the above gates pass, continue to a web UI and packaged workflow. If not, re-evaluate whether raw data, better image capture, or PSI images are required.
