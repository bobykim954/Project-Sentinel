# Project Sentinel - Event Priority

This report applies a simple rule-based priority to the stored events.

The priority is based on detected motion area and event duration.

## Current Rules

- HIGH: motion area >= 3000 or duration >= 10s
- MEDIUM: motion area >= 1500 or duration >= 3s
- LOW: everything else

## Priority Summary

| Priority | Events |
|---|---:|
| HIGH | 3 |
| MEDIUM | 6 |
| LOW | 2 |

## Events

| Event ID | Camera | Region | Area | Duration | Priority |
|---|---|---|---:|---:|---|
| `EVT-20261002-133944-382960` | CAM-01 | BOTTOM LEFT | 1817 | 2.86s | **MEDIUM** |
| `EVT-20261002-133939-358477` | CAM-01 | BOTTOM LEFT | 892 | 1.86s | **LOW** |
| `EVT-20261002-132124-597336` | CAM-01 | TOP LEFT | 2981 | 2.27s | **MEDIUM** |
| `EVT-20261002-132119-717016` | CAM-01 | BOTTOM LEFT | 5294 | 3.60s | **HIGH** |
| `EVT-20261002-125820-561691` | CAM-01 | BOTTOM RIGHT | 1597 | 7.25s | **MEDIUM** |
| `EVT-20261002-125752-352344` | CAM-01 | BOTTOM RIGHT | 1483 | 25.95s | **HIGH** |
| `EVT-20261002-125750-761175` | CAM-01 | BOTTOM RIGHT | 1036 | 0.99s | **LOW** |
| `EVT-20261002-125749-091187` | CAM-01 | BOTTOM RIGHT | 1916 | 1.42s | **MEDIUM** |
| `EVT-20261002-125744-113469` | CAM-01 | BOTTOM LEFT | 2250 | 1.26s | **MEDIUM** |
| `EVT-20261002-125742-543374` | CAM-01 | TOP LEFT | 2746 | 1.39s | **MEDIUM** |
| `EVT-20261002-125729-360518` | CAM-01 | TOP LEFT | 3697 | 12.45s | **HIGH** |

## High Priority Events

- `EVT-20261002-132119-717016` - BOTTOM LEFT - 5294 area - 3.60s
- `EVT-20261002-125752-352344` - BOTTOM RIGHT - 1483 area - 25.95s
- `EVT-20261002-125729-360518` - TOP LEFT - 3697 area - 12.45s

## Notes

Priority is currently a simple heuristic based on motion area and duration. It does not mean that Sentinel has identified an intruder or dangerous activity.

The rules are deliberately simple so they can be tested and changed as more real camera data becomes available.
