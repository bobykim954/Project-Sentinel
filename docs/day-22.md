# Day 22 — Detector Consolidation

## Objective
Separate person detection logic from the main Sentinel pipeline
to improve code reuse and maintainability.

## Changes
- Moved YOLO detection logic into `src/person_detector.py`.
- Added reusable `detect_persons(frame, model)` functionality.
- Centralized detector configuration and thresholds.
- Removed duplicate detection functions from `src/sentinel.py`.
- Updated Sentinel to import and use the reusable detector.
- Preserved motion detection, event management, evidence capture,
  and dashboard integration.

## Validation
- Both Python modules passed compilation.
- YOLO ONNX model loaded successfully.
- Person detection successfully identified one person.
- Evidence snapshot was saved.
- PERSON event started and ended successfully.
- Event duration: 4.03 seconds.
- Maximum detection confidence: 0.77.
- Camera: CAM-01.
- Detected region: BOTTOM RIGHT.

## Outcome
The reusable detector is integrated into the main Sentinel pipeline.

## Limitations
Testing was performed using the available camera setup.
Further validation with physical analogue CCTV hardware remains
part of the integration work.

## Next
Proceed to the next planned development milestone.