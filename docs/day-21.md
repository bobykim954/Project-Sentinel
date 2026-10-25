@'
# Day 21 â€” Event Lifecycle Reliability Testing

**Date:** 25 October 2026

## Objective

Test whether Project Sentinel handles the person-event lifecycle correctly, including normal event completion, event history recording, and shutdown while an event is active.

## Tests performed

### 1. Dashboard startup

Started the dashboard server using `py src\dashboard_server.py`.

The server started successfully and reported its local address as `http://127.0.0.1:8000`.

### 2. Normal event completion

Started Sentinel using `py src\sentinel.py` and tested person detection.

The event history contained completed events with unique event IDs, camera information, start and end times, detected regions, evidence paths, confidence values, and durations.

Three observed events had durations of approximately 26.66 seconds, 5.25 seconds, and 4.44 seconds.

### 3. Duplicate-record check

Searched `data/events.csv` for event `EVT-20261025-213959-095526`.

The search returned one matching record. This confirmed that this specific event appeared once in the CSV history.

### 4. Shutdown during an active event

Started Sentinel, waited for an active person event, and stopped the program using Ctrl+C while the event was still active.

The shutdown test passed. Sentinel finalized the active event, and the active status was cleared from the dashboard.

## Observations

- The dashboard server started successfully.
- Person events were recorded in the CSV history.
- Event records included useful information for later review.
- The checked event appeared only once in the history.
- Graceful shutdown finalized the active event and cleared its live status.
- The existing event lifecycle handled the tested scenarios without requiring a code change.

## Limitations

These tests cover the scenarios performed during this session. They do not prove that every possible event lifecycle condition is handled correctly.

The duplicate-record check covered one specific event. More automated tests would help verify duplicate prevention and shutdown behavior consistently.

The short events observed during testing may be valid detections, but additional testing is needed to assess event stability and whether detection thresholds need adjustment.

## Day 21 outcome

Day 21 focused on testing and observing existing behavior rather than adding a new feature. The normal completion, duplicate-record, and graceful-shutdown checks passed.

No source-code changes were made during this session.

## Next steps

- Add repeatable automated tests for event lifecycle behavior.
- Continue checking that active status is cleared when events end or monitoring exits.
- Keep generated event history, dashboard reports, and evidence images separate from source-code and documentation commits.
'@ | Set-Content -Path docs\day-21.md -Encoding utf8
