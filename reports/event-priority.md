# Project Sentinel - Event Priority

This report applies a simple rule-based priority to the stored events.

The base priority uses motion area and event duration. Person-aware events can be escalated when multiple people are detected with sufficient confidence.

## Current Rules

- HIGH base priority: motion area >= 3000 or duration >= 10s
- MEDIUM base priority: motion area >= 1500 or duration >= 3s
- LOW base priority: everything else
- Multi-person escalation: PERSON event with 2+ people and confidence >= 0.80
- Multi-person escalation increases priority by one level, up to HIGH

## Priority Summary

| Priority | Events |
|---|---:|
| HIGH | 8 |
| MEDIUM | 7 |
| LOW | 2 |

## Person Detection Summary

- Person-aware events: 6
- Multi-person events with confidence >= 0.80: 3

## Events

| Event ID | Camera | Region | Area | Duration | Object | Count | Confidence | Priority | Reason |
|---|---|---|---:|---:|---|---:|---:|---|---|
| `EVT-20261005-234139-428717` | CAM-01 | BOTTOM RIGHT | 11506 | 41.70s | PERSON | 2 | 0.93 | **HIGH** | Large motion area + long duration; multi-person detected (2 people, confidence 0.93), already HIGH |
| `EVT-20261005-231949-684287` | CAM-01 | BOTTOM RIGHT | 1806 | 23.79s | PERSON | 2 | 0.92 | **HIGH** | Long duration; multi-person detected (2 people, confidence 0.92), already HIGH |
| `EVT-20261005-231943-239564` | CAM-01 | BOTTOM RIGHT | 204174 | 5.77s | PERSON | 2 | 0.93 | **HIGH** | Large motion area; multi-person detected (2 people, confidence 0.93), already HIGH |
| `EVT-20261005-225319-535203` | CAM-01 | BOTTOM LEFT | 8498 | 6.14s | PERSON | 1 | 0.84 | **HIGH** | Large motion area |
| `EVT-20261005-225315-367216` | CAM-01 | TOP RIGHT | 1699 | 2.52s | PERSON | 1 | 0.70 | **MEDIUM** | Moderate motion area |
| `EVT-20261005-225312-231726` | CAM-01 | BOTTOM RIGHT | 3445 | 2.78s | PERSON | 1 | 0.80 | **HIGH** | Large motion area |
| `EVT-20261002-133944-382960` | CAM-01 | BOTTOM LEFT | 1817 | 2.86s | UNKNOWN | - | - | **MEDIUM** | Moderate motion area |
| `EVT-20261002-133939-358477` | CAM-01 | BOTTOM LEFT | 892 | 1.86s | UNKNOWN | - | - | **LOW** | Small/short event |
| `EVT-20261002-132124-597336` | CAM-01 | TOP LEFT | 2981 | 2.27s | UNKNOWN | - | - | **MEDIUM** | Moderate motion area |
| `EVT-20261002-132119-717016` | CAM-01 | BOTTOM LEFT | 5294 | 3.60s | UNKNOWN | - | - | **HIGH** | Large motion area |
| `EVT-20261002-125820-561691` | CAM-01 | BOTTOM RIGHT | 1597 | 7.25s | UNKNOWN | - | - | **MEDIUM** | Moderate motion area + moderate duration |
| `EVT-20261002-125752-352344` | CAM-01 | BOTTOM RIGHT | 1483 | 25.95s | UNKNOWN | - | - | **HIGH** | Long duration |
| `EVT-20261002-125750-761175` | CAM-01 | BOTTOM RIGHT | 1036 | 0.99s | UNKNOWN | - | - | **LOW** | Small/short event |
| `EVT-20261002-125749-091187` | CAM-01 | BOTTOM RIGHT | 1916 | 1.42s | UNKNOWN | - | - | **MEDIUM** | Moderate motion area |
| `EVT-20261002-125744-113469` | CAM-01 | BOTTOM LEFT | 2250 | 1.26s | UNKNOWN | - | - | **MEDIUM** | Moderate motion area |
| `EVT-20261002-125742-543374` | CAM-01 | TOP LEFT | 2746 | 1.39s | UNKNOWN | - | - | **MEDIUM** | Moderate motion area |
| `EVT-20261002-125729-360518` | CAM-01 | TOP LEFT | 3697 | 12.45s | UNKNOWN | - | - | **HIGH** | Large motion area + long duration |

## High Priority Events

- `EVT-20261005-234139-428717` - BOTTOM RIGHT - 11506 area - 41.70s - PERSON
  - Reason: Large motion area + long duration; multi-person detected (2 people, confidence 0.93), already HIGH
  - People: 2 | Confidence: 0.93
- `EVT-20261005-231949-684287` - BOTTOM RIGHT - 1806 area - 23.79s - PERSON
  - Reason: Long duration; multi-person detected (2 people, confidence 0.92), already HIGH
  - People: 2 | Confidence: 0.92
- `EVT-20261005-231943-239564` - BOTTOM RIGHT - 204174 area - 5.77s - PERSON
  - Reason: Large motion area; multi-person detected (2 people, confidence 0.93), already HIGH
  - People: 2 | Confidence: 0.93
- `EVT-20261005-225319-535203` - BOTTOM LEFT - 8498 area - 6.14s - PERSON
  - Reason: Large motion area
  - People: 1 | Confidence: 0.84
- `EVT-20261005-225312-231726` - BOTTOM RIGHT - 3445 area - 2.78s - PERSON
  - Reason: Large motion area
  - People: 1 | Confidence: 0.80
- `EVT-20261002-132119-717016` - BOTTOM LEFT - 5294 area - 3.60s - UNKNOWN
  - Reason: Large motion area
- `EVT-20261002-125752-352344` - BOTTOM RIGHT - 1483 area - 25.95s - UNKNOWN
  - Reason: Long duration
- `EVT-20261002-125729-360518` - TOP LEFT - 3697 area - 12.45s - UNKNOWN
  - Reason: Large motion area + long duration

## Multi-Person Events

- `EVT-20261005-234139-428717` - BOTTOM RIGHT - 2 people - confidence 0.93 - priority **HIGH**
  - Reason: Large motion area + long duration; multi-person detected (2 people, confidence 0.93), already HIGH
- `EVT-20261005-231949-684287` - BOTTOM RIGHT - 2 people - confidence 0.92 - priority **HIGH**
  - Reason: Long duration; multi-person detected (2 people, confidence 0.92), already HIGH
- `EVT-20261005-231943-239564` - BOTTOM RIGHT - 2 people - confidence 0.93 - priority **HIGH**
  - Reason: Large motion area; multi-person detected (2 people, confidence 0.93), already HIGH

## Notes

Priority is currently a simple heuristic. It does not mean that Sentinel has identified an intruder, threat, crime, or dangerous activity.

Person count and detection confidence are used only to escalate confidently detected multi-person events by one priority level.

When a multi-person event is already HIGH because of motion area or duration, the multi-person rule does not increase it further. The report records this explicitly in the priority reason.

Historical events created before person detection was added are still included in the report. Their person-related fields remain empty and therefore do not receive person-aware escalation.

The rules are deliberately simple so they can be tested and changed as more real camera data becomes available.
