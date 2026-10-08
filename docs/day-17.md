# Day 17 - Event Intelligence Dashboard

**Date:** October 8, 2026

## Goal

The goal for Day 17 was to bring the event information built during the previous development stages into a single local dashboard.

Previously, Sentinel could detect motion, identify people, store event history, calculate priority, and save evidence. The dashboard update connects those pieces so that an event can be reviewed from one place.

## What Changed

The local dashboard in `reports/event-dashboard.html` was expanded to display:

* Total event count
* Person-aware event count
* Multi-person event count
* High-priority event count
* Evidence-linked event count
* Average event duration
* Priority distribution
* Events by region
* Camera summary
* Latest event
* Longest event
* Latest high-priority event
* Search and filtering
* Event history
* Person count
* Detection confidence
* Priority reason
* Evidence links

The dashboard reads the existing event history from:

```text
data/events.csv
```

and uses the same priority engine from:

```text
src/event_priority.py
```

rather than duplicating the priority rules.

## Event Data Integration

The event table now combines the information collected by Sentinel into one view:

```text
Event ID
Camera
Start Time
Region
Object
Count
Confidence
Priority
Motion Area
Duration
Evidence
Priority Reason
```

This makes individual events easier to review without opening the CSV manually.

## Test Results

Before the dashboard test, Sentinel generated three additional person-aware events.

### Event 1

```text
Event ID: EVT-20261008-193042-356084
Camera: CAM-01
Detected at start: 1 person
Primary Region: TOP LEFT
Duration: 11.59s
Maximum Confidence: 0.88
```

### Event 2

```text
Event ID: EVT-20261008-193056-182324
Camera: CAM-01
Detected at start: 1 person
Primary Region: TOP LEFT
Duration: 19.91s
Maximum Confidence: 0.94
```

### Event 3

```text
Event ID: EVT-20261008-193117-682461
Camera: CAM-01
Detected at start: 1 person
Primary Region: BOTTOM RIGHT
Duration: 3.86s
Maximum Confidence: 0.70
```

The third event was also checked directly in the CSV:

```text
Region: BOTTOM RIGHT
Object type: PERSON
Object count: 1
Detection confidence: 0.70
Duration: 3.86s
Evidence: data/evidence/EVT-20261008-193117-682461.jpg
```

## Dashboard Result

After the new events were recorded, the dashboard processed:

```text
23 total events
```

The dashboard displayed:

```text
Total Events: 23
Person Events: 12
Multi-Person Events: 3
High Priority: 14
Evidence Linked: 16
Average Duration: 13.43s
```

The region summary showed:

```text
BOTTOM RIGHT: 10
BOTTOM LEFT: 6
TOP LEFT: 5
TOP RIGHT: 2
```

The dashboard also correctly identified:

```text
Camera: CAM-01
```

for all currently stored events.

## Region Consistency

A useful test during Day 17 was verifying that the new primary-region logic remained consistent after dashboard generation.

For:

```text
EVT-20261008-193117-682461
```

the stored region was:

```text
BOTTOM RIGHT
```

The dashboard displayed the same region.

The earlier two events also demonstrated that the primary region can differ from the region detected when an event starts. This is expected because Sentinel now selects the dominant region observed throughout the event instead of simply keeping the final detected region.

## Dashboard Filtering

The dashboard includes local filtering for:

* Search
* Priority
* Object type
* Region

The filtering is performed in the browser without regenerating the dashboard or changing the stored event history.

## Evidence Access

Evidence-linked events include a `View evidence` link.

The links point to locally stored images under:

```text
data/evidence/
```

This allows an event record to be connected directly to its captured evidence.

## Architecture

The current local workflow is now:

```text
Camera
   ->
Motion Detection
   ->
Person Detection
   ->
Event Aggregation
   ->
Event History
   ->
Priority Engine
   ->
Event Dashboard
   ->
Evidence Review
```

This is a more complete surveillance workflow than the earlier standalone detection components.

## Important Limitations

The dashboard is still a local development interface.

A HIGH priority event does not mean Sentinel has identified an intruder, crime, or dangerous activity.

The priority engine remains a simple rule-based heuristic.

Historical events created before person detection was introduced may still show UNKNOWN object information because those fields were not available when the events were recorded.

The event history currently stores a motion bounding box rather than the YOLO person bounding box.

The dashboard is also generated from stored CSV data and does not yet provide real-time updates while Sentinel is running.

## Current Status

Day 17 successfully connected the existing Sentinel components into a single event intelligence interface.

The system can now:

```text
Detect
Record
Aggregate
Classify
Prioritize
Explain
Review
```

from one local dashboard.

The next improvements can focus on making the dashboard more operational and eventually supporting real-time monitoring rather than only reviewing stored events.
