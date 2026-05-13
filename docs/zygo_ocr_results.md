# Initial Zygo Screenshot OCR Results

## Source

ZIP file received from user:

`/home/xin/.openclaw/media/inbound/ZygoScreenshots---30563b7f-ca13-4557-919f-ea9d36b7606d.zip`

Extracted files:

- `data/raw/zygo_screenshots/Zygo0.png`
- `data/raw/zygo_screenshots/Zygo1.png`
- `data/raw/zygo_screenshots/Zygo2.png`
- `data/raw/zygo_screenshots/Zygo3.png`
- `data/raw/zygo_screenshots/Zygo4.png`
- `data/raw/zygo_screenshots/Zygo5.png`

Structured manifests:

- `data/raw/zygo_screenshots/validation_manifest.json`
- `data/raw/zygo_screenshots/validation_manifest.csv`

## Confirmed assumptions

- Face mapping: `Zygo0.png` through `Zygo5.png` correspond to faces 1 through 6.
- Wavelength: 633.0 nm.
- Reference values: wavefront error in waves.
- The visible Zygo removal settings appear to include Piston and Tilt removal under Zernike removal mode.
- OCR confidence is currently medium; numeric values should still be reviewed against the screenshots if a discrepancy appears during validation.

## Extracted reference values

| Face | Source | P-V (waves) | RMS (waves) | Power (waves) | Irregularity (waves) | Aperture X (mm) | Aperture Y (mm) |
|---|---|---:|---:|---:|---:|---:|---:|
| face_01 | Zygo0.png | 0.200 | 0.043 | 0.039 | 0.237 | 37.51 | 32.76 |
| face_02 | Zygo1.png | 0.173 | 0.021 | -0.012 | 0.203 | 38.13 | 32.97 |
| face_03 | Zygo2.png | 0.089 | 0.009 | 0.002 | 0.107 | 37.62 | 32.76 |
| face_04 | Zygo3.png | 0.289 | 0.044 | -0.056 | 0.329 | 38.24 | 32.67 |
| face_05 | Zygo4.png | 0.224 | 0.032 | -0.030 | 0.251 | 37.51 | 32.76 |
| face_06 | Zygo5.png | 0.168 | 0.026 | 0.005 | 0.193 | 38.24 | 32.67 |

## Immediate notes

- Face 04 appears to be the worst by P-V, RMS, and irregularity in this initial OCR set.
- Face 03 appears to be the best by P-V, RMS, and irregularity.
- The aperture dimensions vary slightly across screenshots, likely due to Zygo ROI measurement/analysis settings.

## Next validation work

1. Extract the lower-right fringe ROI from each screenshot.
2. Build the first Fourier-carrier phase extraction prototype.
3. Compare prototype P-V/RMS/Power/Irregularity against this manifest.
4. Tune carrier filtering, unwrap, scaling, and term-removal conventions against the six-face validation set.
