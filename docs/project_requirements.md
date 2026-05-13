# Project Requirements

## 1. Objective

Build a batch analysis tool that estimates flatness and wavefront/surface error parameters from rectangular-aperture interferogram fringe images.

The target application is flatness evaluation of hexagon scanning mirror faces. Each mirror has six rectangular reflective faces. The system should process six face images as a batch and produce a comparable report across all faces.

## 2. Target outputs

For each image / mirror face, the system should output:

- P-V error
- RMS error
- Power
- Irregularity
- Rectangular low-order polynomial coefficients
- Zernike-equivalent coefficients
- Wavefront error map
- Residual map after selected term removal
- Diagnostic images showing ROI detection, fringe crop, FFT peak selection, phase map, and residual map

For a six-face batch, the system should output:

- Summary table for all six faces
- Pass/fail status if tolerances are supplied
- Worst face by P-V, RMS, Power, and Irregularity
- CSV export
- Human-readable HTML or PDF report

## 3. Input types

### 3.1 MVP input

- Zygo-like screenshots containing:
  - a fringe image in one region of the screenshot
  - displayed numerical output such as P-V, RMS, Power, Irregularity, or related values
  - wavefront error map

These screenshots will be used both as input material and as validation references.

### 3.2 Future input

- Direct fringe image files without screenshot UI
- Direct phase/wavefront data if available from instruments
- Multi-frame phase-shifting interferometry image sets

## 4. Required user-supplied metadata

For reliable quantitative results, each image or batch should include:

- Wavelength, default 633 nm
- Reflection or transmission test geometry
- Physical aperture dimensions of each rectangular mirror face
- Whether output should be wavefront error or surface error
- Which terms should be removed before computing irregularity
- Optional expected commercial-software values for validation

## 5. Main assumptions for MVP

- The aperture is rectangular.
- The fringe pattern is visible and has sufficient contrast.
- The first algorithm path focuses on spatial-carrier / Fourier-transform fringe analysis.
- Sparse fringe centerline analysis is deferred to a later phase.
- Results are engineering estimates until validated against commercial interferometer outputs.

## 6. Success criteria for MVP

The MVP is considered useful when, on a representative validation set:

- Rectangular ROI can be extracted or manually specified.
- Phase extraction produces a plausible continuous wavefront map.
- P-V and RMS are within approximately 10–15% of trusted Zygo-style reference values for suitable high-carrier images.
- Power and Irregularity definitions are documented and repeatable.
- Batch report generation works for six mirror faces.

## 7. Explicit non-goals for MVP

- Fully automatic interpretation of arbitrary low-quality phone photos.
- Guaranteed equivalence to Zygo internal algorithms.
- Sparse-fringe full automation.
- Multi-wavelength or phase-shifting analysis unless suitable data is provided.
- Production-certified metrology without calibration and validation.
