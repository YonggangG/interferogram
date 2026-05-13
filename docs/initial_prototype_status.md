# Initial Prototype Status

## Date

2026-05-13

## Confirmed validation assumptions

- `Zygo0.png` through `Zygo5.png` map to mirror faces 1 through 6.
- Wavelength is 633 nm.
- Zygo reference values are wavefront error in waves.

## Work completed

1. Extracted six screenshots from the user-provided ZIP.
2. Created a validation manifest from OCR/vision extraction.
3. Extracted the lower-right fringe image panel from each screenshot.
4. Created a local Python virtual environment and installed prototype dependencies.
5. Implemented first-pass modules:
   - `src/mask_utils.py`
   - `src/fourier_phase.py`
   - `src/metrics.py`
   - `src/run_initial_analysis.py`
   - `src/compare_to_zygo.py`
6. Ran first-pass FFT carrier phase extraction and generated diagnostic maps.

## Generated outputs

- ROI crops: `data/processed/fringe_roi/`
- ROI metadata: `data/processed/fringe_roi/roi_metadata.json`
- First FFT analysis outputs: `reports/initial_fft_analysis/`
- First comparison CSV: `reports/initial_fft_analysis/zygo_comparison.csv`
- Diagnostic contact sheet: `reports/initial_fft_analysis/roi_mask_wavefront_contact_sheet.png`

## First-pass result

The first-pass FFT extraction runs end-to-end, but it does **not yet match** the Zygo reference values.

Observed issue:

- Prototype P-V/RMS values are much larger than Zygo references.
- This means the naive FFT sideband/unwrapping path is extracting large carrier/ramp/unwrap structure from the screenshot fringe panels rather than the same processed wavefront convention reported by Zygo.

This is an expected early prototype failure mode because the current input is a screenshot-rendered fringe panel, not the original raw interferogram intensity data.

## Immediate technical hypotheses

1. The screenshot fringe panel may include display scaling, gamma, UI rendering, and non-raw intensity mapping.
2. The dark panel/background and aperture edge strongly affect FFT sideband selection and unwrapping.
3. The Fourier path needs better carrier peak selection, sideband radius tuning, and masked/windowed preprocessing.
4. Zygo's reported values likely use internal calibration and term-removal conventions that need to be matched.
5. It may be necessary to use the screenshot wavefront map and color scale for validation, while using direct fringe images for final real analysis.

## Next engineering steps

1. Improve fringe ROI preprocessing:
   - crop only the active aperture, not the whole display panel
   - apply a 2D window inside the valid aperture
   - remove background and carrier ramp more carefully
2. Add parameter sweep for FFT sideband radius and peak selection.
3. Add residual diagnostics after removing piston/tilt/power.
4. Decide whether screenshot-derived fringe panels are sufficient for algorithm validation, or whether direct raw fringe images are required.
5. Consider extracting the displayed Zygo wavefront map as an alternate validation path from screenshots.
