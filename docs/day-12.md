# Project Sentinel — Day 12

## Event Dashboard

**Date:** 3 October 2026
**Project:** Project Sentinel
**Stage:** Day 12

---

## 1. What I wanted to improve

By Day 11, Sentinel could analyze the event history and generate a Markdown report.

That was useful, but it still required reading a text report.

For Day 12, I wanted to make the information easier to understand at a glance.

The goal was to create a small local dashboard that could show:

* total events
* average duration
* longest event
* evidence-linked events
* events by region
* camera summary
* event records
* links to stored evidence

The dashboard is generated from the same event history used by the analytics system.

---

## 2. Dashboard structure

I created:

```text id="f0f6aa"
src/event_dashboard.py
```

The script reads:

```text id="y6t5st"
data/events.csv
```

and generates:

```text id="jt7g1x"
reports/event-dashboard.html
```

The project structure is now becoming:

```text id="7pjx7g"
src/
├── main.py
├── event_summary.py
└── event_dashboard.py

data/
├── events.csv
└── evidence/

reports/
├── event-summary.md
└── event-dashboard.html
```

This keeps detection, analytics, and presentation as separate parts of the project.

---

## 3. Dashboard information

The dashboard currently displays four main summary values.

The real event history produced:

```text id="6xtk8a"
Total Events: 11
Average Duration: 5.57s
Longest Event: 25.95s
Evidence Linked: 4
```

These values match the event history that Sentinel has collected during testing.

---

## 4. Region summary

The dashboard also groups the recorded events by region.

The current data shows:

```text id="40yepa"
BOTTOM LEFT   → 4 events
BOTTOM RIGHT  → 4 events
TOP LEFT      → 3 events
```

There are currently no stored `TOP RIGHT` events in the event history.

This is a description of the current test data, not a claim that the camera can never detect activity in that region.

---

## 5. Camera summary

The dashboard shows:

```text id="eehn0x"
CAM-01: 11 events
```

This is expected because the development system is still using one webcam.

The camera ID structure remains useful because the project is eventually intended to work with multiple CCTV sources.

---

## 6. Event details

The dashboard includes a table of the stored events.

Each row contains:

```text id="ealh7d"
Event ID
Camera
Start Time
Region
Motion Area
Duration
Evidence
```

The most recent event shown in the current data is:

```text id="x7i0fr"
EVT-20261002-133944-382960
CAM-01
BOTTOM LEFT
2.86 seconds
```

The dashboard also exposes links to the evidence images for events that have saved snapshots.

---

## 7. Evidence integration

Four events in the current history have linked evidence.

The dashboard displays a `View evidence` link for those records.

For example:

```text id="kvcw42"
EVT-20261002-133944-382960
    ↓
data/evidence/EVT-20261002-133944-382960.jpg
```

This makes the dashboard more useful than the event summary alone because the stored event can be connected directly to its visual evidence.

---

## 8. Search functionality

The dashboard includes a search field for the event table.

The intended use is to search by information such as:

```text id="a7uv4g"
Event ID
Camera ID
Region
Start time
```

This is a small convenience feature now, but it gives us a starting point for more useful event filtering later.

---

## 9. Testing

I generated the dashboard using:

```powershell id="0efrwi"
python src/event_dashboard.py
```

The script reported:

```text id="zziyk6"
Loaded 11 events.
Dashboard saved: reports/event-dashboard.html
```

The generated dashboard displayed the current event information, including the 11 stored events, regional counts, camera summary, durations, and evidence links.

This confirmed that the dashboard was successfully reading the stored event history and presenting it in a more accessible form.

---

## 10. What I learned

### Stored data becomes much more useful when it is easy to read

The CSV file is good for the program.

The Markdown report is good for a simple text summary.

The dashboard is better when I want to look at the system more like an actual application.

Each representation has a different purpose.

---

### Presentation should come after the underlying data works

The dashboard was not built around fake examples.

It reads the event records Sentinel has already generated.

This means that when the event history changes, the dashboard can reflect the new data without manually changing the values.

---

### Keeping components separate helps the project grow

Sentinel now has different pieces with different responsibilities:

```text id="al71cu"
main.py
    → detection and event creation

event_summary.py
    → statistics

event_dashboard.py
    → presentation

events.csv
    → stored history

evidence/
    → visual evidence
```

This is becoming a cleaner structure for the larger project.

---

## 11. Current limitations

The dashboard is still a local development dashboard.

It is generated as a static HTML file rather than being a live application.

It currently shows one camera because only `CAM-01` is being used.

The dashboard does not yet update automatically while Sentinel is running.

It also does not yet display live camera feeds, object classifications, alerts, or more advanced analytics.

Those features can be added later when they become useful.

---

## 12. What Day 12 accomplished

By the end of Day 12, Sentinel could:

* read its stored event history
* generate a visual HTML dashboard
* show total event count
* show average event duration
* show longest event
* show evidence coverage
* group events by region
* summarize events by camera
* display event details
* provide links to saved evidence
* provide basic event searching
* keep dashboard generation separate from live detection

The overall system is now:

```text id="g0rtvc"
Camera
   ↓
Motion Detection
   ↓
Event
   ↓
Localization
   ↓
Metadata
   ↓
Evidence
   ↓
Event History
   ↓
Analytics
   ↓
Dashboard
```

---

## 13. Current status

**Day 12 technical work:** COMPLETE

**Dashboard generation:** WORKING

**Event summary cards:** WORKING

**Region summary:** WORKING

**Camera summary:** WORKING

**Event table:** WORKING

**Evidence links:** WORKING

**Search field:** ADDED

**Real event data displayed:** YES

**Dashboard generation test:** COMPLETED

**Documentation:** COMPLETE

**Git commit:** PENDING

**GitHub push:** PENDING

---

## Day 12 conclusion

Day 12 made the project much easier to see.

Before this, Sentinel's information was mainly inside a CSV file and a Markdown report.

Now there is a local dashboard that brings the information together in one place.

This is still only a development dashboard, but it makes the project feel much more like an application and gives us a better base for future monitoring and analytics features.

The development process remains:

**Build → Test → Observe → Improve → Document → Commit → Push.**
