# Test Image Intake Guide

## 1. What to provide now

Please provide six Zygo-style screenshots similar to the previously shared example.

Each screenshot should ideally show:

- The original fringe pattern image, usually in a small panel or corner.
- The wavefront error map.
- Numeric outputs such as P-V, RMS, Power, and Irregularity.
- Wavelength or test setup information if visible.
- Any active term-removal settings if visible.

## 2. Preferred image quality

For best extraction:

- Use the highest-resolution screenshot available.
- Avoid additional compression if possible.
- Prefer PNG over JPEG if available.
- Make sure the numeric values are readable.
- Make sure the fringe panel is not covered or cropped.

## 3. Metadata to send with the images

If known, please include:

- Mirror face physical size: length × width in mm.
- Wavelength: e.g. 633 nm.
- Whether Zygo output is wavefront error or surface error.
- Whether the mirror was tested in reflection.
- Any tolerance thresholds for pass/fail.
- Face ordering: which screenshot corresponds to face 1–6.

## 4. Suggested message format

You can upload the six images first, then send a short note like:

```text
Face order: uploaded order = face 1 to face 6.
Wavelength: 633 nm.
Aperture size: __ mm × __ mm.
Output type: Zygo values are wavefront error / surface error / unknown.
Reflection test: yes / no / unknown.
```

If some metadata is unknown, send the images anyway. The first analysis pass can still proceed, but unit conversion and Zygo comparison may be marked provisional.

## 5. How the images will be used

The screenshots will be used to create the initial validation set:

1. Extract the fringe ROI.
2. Manually record Zygo-displayed reference values.
3. Run the prototype phase extraction pipeline.
4. Compare computed metrics against Zygo values.
5. Decide whether the FFT-based MVP is sufficient or whether additional algorithms are needed.

## 6. Privacy / data handling note

The files will stay in the local project workspace unless you explicitly ask for publishing or external sharing.
