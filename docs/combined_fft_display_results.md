# Combined FFT and Display-Map Results

## Date

2026-05-13

## Scope

Per user instruction, this pass did:

1. Improve the FFT demodulation route first.
2. Then extract the displayed Zygo wavefront map/colorbar route.
3. Combine the results and compare reliability.

## Route 1: Improved FFT demodulation from fringe patches

New scripts:

- `src/run_fft_sweep.py`
- `src/compare_improved_fft.py`

Outputs:

- `reports/improved_fft_sweep/improved_fft_best_metrics.csv`
- `reports/improved_fft_sweep/improved_fft_zygo_comparison.csv`
- `reports/improved_fft_sweep/improved_fft_contact_sheet.png`

Changes from the previous FFT pass:

- background-corrected FFT preparation
- mask-boundary tapering to reduce spectral leakage
- candidate carrier peak search instead of single strongest peak only
- Gaussian/elliptical sideband filters
- radius/ellipse-ratio sweep
- reference-free scoring based on compact residuals and realistic PV/RMS scale

Result:

The FFT route improved substantially. Example: face 01 irregularity changed from about `0.452 waves` in the previous active-aperture pass to `0.228 waves`, very close to Zygo IRR `0.237 waves`.

However, not all faces match. Current FFT route remains inconsistent across the six screenshots.

| Face | Zygo P-V | FFT P-V after tilt | Zygo RMS | FFT RMS after tilt | Zygo IRR | FFT IRR |
|---|---:|---:|---:|---:|---:|---:|
| face_01 | 0.200 | 0.338 | 0.043 | 0.061 | 0.237 | 0.228 |
| face_02 | 0.173 | 0.525 | 0.021 | 0.070 | 0.203 | 0.488 |
| face_03 | 0.089 | 0.167 | 0.009 | 0.021 | 0.107 | 0.169 |
| face_04 | 0.289 | 0.514 | 0.044 | 0.078 | 0.329 | 0.510 |
| face_05 | 0.224 | 0.339 | 0.032 | 0.064 | 0.251 | 0.322 |
| face_06 | 0.168 | 0.278 | 0.026 | 0.043 | 0.193 | 0.265 |

Interpretation:

- The improved FFT route is now plausible, not completely wrong.
- It is still not accurate enough for production validation from screenshots alone.
- The likely cause is that the small lower-right fringe panels are rendered display images, not raw interferogram intensity data.
- This route should remain the basis for future direct-fringe/raw-image analysis, but it should not be judged solely by screenshot fringe patches.

## Route 2: Displayed Zygo wavefront map extraction

New scripts:

- `src/extract_wavefront_maps.py`
- `src/analyze_display_wavefront.py`

Outputs:

- `data/processed/zygo_wavefront_display/`
- `reports/display_wavefront_analysis/display_wavefront_metrics.csv`
- `reports/display_wavefront_analysis/display_wavefront_contact_sheet.png`

Method:

1. Crop the main colored Zygo WAVEFRONT ERROR display.
2. Crop the vertical colorbar.
3. Build a colorbar lookup table from rendered color pixels.
4. Convert the displayed wavefront map colors into a relative scalar map.
5. Calibrate the relative scalar range using OCR-extracted Zygo P-V.
6. Compare display-derived RMS to Zygo RMS.

Important limitation:

- This route is **not independent** for P-V because P-V is used for calibration.
- RMS is still informative because it tests whether the map's spatial distribution is consistent after PV calibration.

Result:

| Face | Zygo RMS | Display-derived RMS | RMS relative error |
|---|---:|---:|---:|
| face_01 | 0.043 | 0.044 | +2.8% |
| face_02 | 0.021 | 0.029 | +40.5% |
| face_03 | 0.009 | 0.018 | +101.4% |
| face_04 | 0.044 | 0.048 | +9.0% |
| face_05 | 0.032 | 0.043 | +33.4% |
| face_06 | 0.026 | 0.032 | +21.9% |

Interpretation:

- The display-map route is much closer to the Zygo screenshot numbers than the fringe FFT route for screenshot validation.
- face 01 and face 04 are especially good.
- face 03 is poor because its RMS is very small and display/color quantization/noise dominates.
- Because P-V is used as a calibration anchor, this route is useful for extracting approximate displayed wavefront maps and sanity-checking reports, not for independent metrology.

## Combined conclusion

The two routes answer different questions:

### FFT fringe route

Best for the eventual product if direct raw fringe images are available. It is physically meaningful and independent, but screenshot fringe panels are too degraded/small/rendered to fully validate it.

### Display wavefront route

Best for extracting information from the current Zygo screenshots. It can reconstruct approximate displayed wavefront maps and reproduce RMS trends reasonably, but it depends on screenshot rendering and PV calibration.

## Current recommendation

Continue the project with a two-mode architecture:

1. **Raw/direct fringe mode**
   - Input: direct interferogram intensity image.
   - Algorithm: improved FFT demodulation + phase unwrap + rectangular polynomial metrics.
   - This is the real production mode.

2. **Zygo screenshot audit mode**
   - Input: Zygo screenshot.
   - Algorithm: OCR + wavefront display/colorbar extraction + approximate map reconstruction.
   - Purpose: validation, legacy report extraction, and dataset bootstrapping.

For accurate production validation, the next best data to request is at least one of:

- direct Zygo raw interferogram image export,
- Zygo phase/wavefront data export,
- higher-resolution screenshot where colorbar numeric labels are readable,
- same mirror face captured as both raw fringe image and Zygo result.

## Combined comparison file

See:

`reports/combined_route_comparison.csv`
