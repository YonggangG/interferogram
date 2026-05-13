# Second-Pass Active Aperture Status

## Date

2026-05-13

## Purpose

The first FFT prototype used the full lower-right Zygo display panel and failed because the mask included too much non-fringe UI/background. This second pass extracts only the active visible fringe patch and reruns the Fourier-carrier path.

## Work completed

New scripts:

- `src/extract_active_apertures.py`
- `src/run_active_analysis.py`
- `src/compare_active_to_zygo.py`

Generated data:

- `data/processed/fringe_active_aperture/`
- `data/processed/fringe_active_aperture/active_aperture_metadata.json`
- `reports/active_fft_analysis/active_fft_metrics.csv`
- `reports/active_fft_analysis/active_fft_zygo_comparison.csv`
- `reports/active_fft_analysis/active_fft_contact_sheet.png`

## Key improvement

The active-aperture crop removes most UI/background contamination. The resulting residual P-V values are now in the same broad order of magnitude as Zygo irregularity for some faces.

## Current comparison summary

| Face | Zygo P-V | Prototype P-V after tilt | Zygo RMS | Prototype RMS after tilt | Zygo IRR | Prototype residual P-V |
|---|---:|---:|---:|---:|---:|---:|
| face_01 | 0.200 | 0.547 | 0.043 | 0.081 | 0.237 | 0.452 |
| face_02 | 0.173 | 0.237 | 0.021 | 0.048 | 0.203 | 0.228 |
| face_03 | 0.089 | 0.386 | 0.009 | 0.069 | 0.107 | 0.361 |
| face_04 | 0.289 | 0.640 | 0.044 | 0.099 | 0.329 | 0.623 |
| face_05 | 0.224 | 0.231 | 0.032 | 0.045 | 0.251 | 0.166 |
| face_06 | 0.168 | 0.471 | 0.026 | 0.053 | 0.193 | 0.489 |

## Interpretation

This is a meaningful improvement but not yet a validated algorithm.

Good signs:

- The pipeline now runs on the actual visible fringe patch rather than the whole UI panel.
- Face 02 and face 05 are much closer to Zygo than the first pass.
- Tilt-removed P-V and residual P-V are now plausible wave-scale values instead of 10–20 waves.

Remaining issues:

- Face 01, 03, 04, and 06 are still too high.
- Screenshot-derived fringe patches are small, rendered, gamma-adjusted, and likely not raw intensity data.
- Zygo's displayed fringe patch may be a visualization, not the exact raw interferogram used for the numerical report.
- Current Fourier sideband selection and filter radius are heuristic.

## Next technical direction

1. Add more robust carrier demodulation:
   - local frequency estimation
   - sideband selection constrained by visible fringe orientation
   - elliptical/Gaussian sideband filters
2. Add reference-guided diagnostic sweeps to understand sensitivity, while keeping production mode reference-free.
3. Extract or approximate the displayed Zygo wavefront map from the screenshot as a second validation route.
4. If available later, prefer direct raw interferogram exports or phase maps over screenshots for real calibration.

## Current conclusion

The screenshot data is useful for bootstrapping and convention matching, but may be insufficient by itself for high-accuracy phase recovery from the lower-right fringe display. The project should continue, but final validation will likely require either direct fringe images or Zygo-exported raw/phase data.
