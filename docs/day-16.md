# Day 16 - Person-Aware Event Priority

**Date:** October 6, 2026

## Goal

The goal for Day 16 was to improve the existing event priority system so that it could use the person-detection information added during Day 15.

Previously, event priority was based only on motion area and event duration. The updated priority engine now also considers confidently detected multi-person events.

The intention was not to create a complex machine-learning risk score. The system remains a simple, explainable rule-based heuristic.

## What Changed

The existing `src/event_priority.py` was updated to use:

* Motion area
* Event duration
* Object type
* Number of detected people
* Detection confidence
* Priority reason

The generated report now explains why an event received its priority instead of displaying only HIGH, MEDIUM, or LOW.

## Priority Rules

The original motion and duration rules were preserved.

### HIGH

An event receives HIGH base priority when:

```text
motion area >= 3000
OR
duration >= 10 seconds
```

### MEDIUM

An event receives MEDIUM base priority when:

```text
motion area >= 1500
OR
duration >= 3 seconds
```

### LOW

Events below those thresholds remain LOW.

## Multi-Person Escalation

A person-aware event qualifies for multi-person escalation when:

```text
object_type = PERSON
object_count >= 2
detection_confidence >= 0.80
```

A qualifying multi-person event is raised by one priority level, up to HIGH.

If the event is already HIGH because of motion area or duration, its priority remains HIGH. The report records this explicitly rather than artificially increasing the priority.

## Test Result

The priority engine was run against the current event history.

The test processed:

```text
17 events
```

The resulting priority distribution was:

```text
HIGH: 8
MEDIUM: 7
LOW: 2
```

The event history contained:

```text
Person-aware events: 6
Multi-person events with confidence >= 0.80: 3
```

## Multi-Person Results

Three stored events contained two detected people with confidence above the current threshold.

### Event 1

```text
Event ID: EVT-20261005-234139-428717
Region: BOTTOM RIGHT
People: 2
Confidence: 0.93
Motion area: 11506
Duration: 41.70s
Priority: HIGH
```

The event was already HIGH because it had both a large motion area and long duration.

### Event 2

```text
Event ID: EVT-20261005-231949-684287
Region: BOTTOM RIGHT
People: 2
Confidence: 0.92
Motion area: 1806
Duration: 23.79s
Priority: HIGH
```

This event was already HIGH because of its long duration.

### Event 3

```text
Event ID: EVT-20261005-231943-239564
Region: BOTTOM RIGHT
People: 2
Confidence: 0.93
Motion area: 204174
Duration: 5.77s
Priority: HIGH
```

This event was already HIGH because of its very large motion area.

## Important Observation

The current dataset did not contain a multi-person event that started at LOW or MEDIUM and was then raised by the new person-aware rule.

All three confirmed multi-person events were already HIGH because of motion area or duration.

This was not treated as a reason to artificially change the thresholds. The rule was left as implemented and documented honestly.

This means the person-aware escalation logic is implemented and ready, but its escalation effect still needs to be demonstrated with a suitable real-world event in a future test.

## Report Improvements

The generated `reports/event-priority.md` now includes:

* Priority summary
* Person detection summary
* Object count
* Detection confidence
* Priority reason
* High-priority event details
* Multi-person event details
* Explanation of the rule limitations

For example, an event can now be described as:

```text
Large motion area + long duration;
multi-person detected (2 people, confidence 0.93),
already HIGH
```

This makes the decision easier to understand and debug.

## Current Limitation

Priority is still a simple heuristic. It does not mean that Sentinel has identified an intruder, threat, crime, or dangerous activity.

Historical events created before person detection was introduced have empty person-specific fields and therefore do not receive person-aware escalation.

The current priority rules are deliberately simple and will need more real camera data before stronger conclusions can be made about what different event patterns should mean.

## Status

Day 16 successfully upgraded the event priority engine to understand person-aware event data and generate explainable priority decisions.

Current pipeline:

```text
Camera
   ->
Motion Detection
   ->
Person Detection
   ->
Event History
   ->
Priority Analysis
   ->
Explainable Event Report
```

The priority engine is now ready for future improvements based on real event history.
