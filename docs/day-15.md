# Day 15 - Person-Aware Event Integration

**Date:** October 5, 2026

## Goal

The main goal for Day 15 was to integrate the person detector built on Day 14 with the existing Project Sentinel motion and event pipeline.

Previously, Sentinel could detect motion, identify its region, create event records, and save evidence. The new version adds person detection so that an event is only started when motion is detected and at least one person is visible.

The basic event condition is:

```text
Motion detected + Person detected = Person event
```

## What was added

The integrated `src/sentinel.py` now combines:

* Motion detection
* Regional motion analysis
* YOLO person detection
* Person count tracking
* Detection confidence tracking
* Event start and end states
* Event IDs
* Camera IDs
* Evidence snapshots
* Event history in CSV format

The event history was also migrated to a person-aware format while preserving the existing records.

At the start of Day 15, the migration reported:

```text
Event history updated. 11 existing events kept.
```

No previous event records were intentionally removed.

## Person-Aware Event Fields

The current event history contains:

```text
event_id
camera_id
start_time
end_time
region
motion_area
bbox_x
bbox_y
bbox_width
bbox_height
evidence_path
object_type
object_count
detection_confidence
duration_seconds
```

Older events have blank values for person-specific fields because those events were created before person detection was added.

## Single-Person Test

A real webcam test produced three completed person events.

### Event 1

```text
Event ID: EVT-20261005-225312-231726
Camera: CAM-01
Region: BOTTOM RIGHT
People: 1
Confidence: 0.80
Motion area: 3445
Duration: 2.78s
Evidence: data/evidence/EVT-20261005-225312-231726.jpg
```

### Event 2

```text
Event ID: EVT-20261005-225315-367216
Camera: CAM-01
Region: TOP RIGHT
People: 1
Confidence: 0.70
Motion area: 1699
Duration: 2.52s
Evidence: data/evidence/EVT-20261005-225315-367216.jpg
```

### Event 3

```text
Event ID: EVT-20261005-225319-535203
Camera: CAM-01
Region: BOTTOM LEFT
People: 1
Confidence: 0.84
Motion area: 8498
Duration: 6.14s
Evidence: data/evidence/EVT-20261005-225319-535203.jpg
```

These events confirmed that the integrated pipeline could detect a person while also processing motion and creating normal event records.

## Two-Person Test

A later controlled test was performed with two people visible to the camera.

The first event produced:

```text
PERSON EVENT STARTED!
People at start: 1
```

and later completed with:

```text
Max People: 2
Max Confidence: 0.93
```

The CSV confirmed:

```text
object_type = PERSON
object_count = 2
detection_confidence = 0.93
duration_seconds = 41.70
```

This is important because the second person was not detected in the first frame of the event, but was detected later while the same event was still active.

The system therefore now tracks the maximum person count reached during an event instead of relying only on the first detection frame.

A previous test also directly produced:

```text
People: 2
```

at event start, confirming that the detector can recognize two people simultaneously.

## Terminal Output Improvement

The event-start message was changed to make its meaning clearer:

```text
People at start: 1
```

instead of simply:

```text
People: 1
```

At event completion, Sentinel now reports:

```text
Max People: 2
Max Confidence: 0.93
```

This avoids confusion when the number of detected people changes while an event is active.

## Event Finalization Improvement

An active person event is now finalized when Sentinel exits normally.

This prevents the system from leaving an event unfinished when the program is stopped while an event is active.

## Evidence and Event History

Each new person event saves an evidence image under:

```text
data/evidence/
```

and records the event in:

```text
data/events.csv
```

Evidence paths are stored using forward slashes so the event history remains consistent across the project.

## Important Limitation

The bounding box currently stored in the event history is the **motion bounding box**, not the YOLO person bounding box.

The YOLO person boxes are displayed during detection, but the CSV event record still uses the motion bounding box produced by the motion detector.

This is currently acceptable for the integration stage, but it should be improved later so that event evidence can store the actual detected person's bounding box.

Another limitation is that a dedicated integrated bag-only regression test was not performed during this session. The standalone YOLO detector was previously tested and its false-positive behavior was reduced, but the integrated pipeline should receive a dedicated regression test later.

## Current Status

Day 15 successfully integrated person detection into the Sentinel event pipeline.

Confirmed during testing:

* Person-aware event detection
* Single-person detection
* Two-person detection
* Maximum people tracking
* Maximum confidence tracking
* Evidence capture
* Event history recording
* Event start and end handling
* Event finalization on exit
* Person-aware CSV migration

The next stage is to continue building higher-level intelligence on top of these structured events rather than changing the core detector unnecessarily.
