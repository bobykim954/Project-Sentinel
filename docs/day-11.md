# Project Sentinel — Day 11

## Event History Analytics

**Date:** 3 October 2026
**Project:** Project Sentinel
**Stage:** Day 11

---

## 1. What I wanted to build

By Day 10, Sentinel had started collecting structured event information.

The event history contained details such as:

* event ID
* camera ID
* start and end time
* region
* motion area
* bounding-box information
* evidence path
* event duration

At that point, I had a growing list of events, but I was still mostly looking at the CSV manually.

For Day 11, I wanted Sentinel to start doing something useful with the information it had already collected.

The goal was to create a small analytics layer that could answer questions such as:

> How many events have been recorded?

> Which region has had the most events?

> How long do events usually last?

> Which event lasted the longest?

> How many events have linked evidence?

---

## 2. Separating analysis from live detection

Instead of adding more code to `src/main.py`, I created a separate file:

```text
src/event_summary.py
```

The idea is to keep the live camera system separate from the analytics system.

The structure is now:

```text
src/main.py
    ↓
Detect and record events

data/events.csv
    ↓
Store event history

data/evidence/
    ↓
Store visual evidence

src/event_summary.py
    ↓
Analyze stored events

reports/event-summary.md
    ↓
Readable summary
```

This keeps the project easier to understand as it grows.

---

## 3. Reading the event history

The analytics script reads:

```text
data/events.csv
```

Each stored event is loaded into the program and converted into values that can be analyzed.

For example, duration is converted into a number so Sentinel can calculate averages and compare events.

The script also handles older records where some of the newer fields are empty.

That is important because the event history contains records from different stages of development.

---

## 4. Statistics generated

The first successful analysis loaded:

```text
Loaded 11 events.
```

The report calculated:

```text
Total events: 11
Total recorded duration: 61.30 seconds
Average event duration: 5.57 seconds
Longest event: 25.95 seconds
Evidence-linked events: 4
```

These numbers were generated directly from the current `events.csv`.

---

## 5. Longest event

The longest recorded event was:

```text
Event ID:
EVT-20261002-125752-352344

Camera:
CAM-01

Region:
BOTTOM RIGHT

Duration:
25.95 seconds
```

This is useful because Sentinel can now identify specific patterns in its stored history instead of only listing events.

---

## 6. Largest recorded motion area

The event with the largest recorded motion area was:

```text
Event ID:
EVT-20261002-132119-717016

Camera:
CAM-01

Region:
BOTTOM LEFT

Motion area:
5294
```

This came from the real Day 9 event data.

---

## 7. Events by region

The report grouped the current 11 events by region:

```text
Region        Events
------------  ------
BOTTOM LEFT       4
BOTTOM RIGHT      4
TOP LEFT          3
```

There are currently no stored events labelled `TOP RIGHT`.

This does not necessarily mean no activity ever happened there. It only describes the events currently stored in the event history.

That distinction matters when interpreting early test data.

---

## 8. Events by camera

All 11 currently stored events are associated with:

```text
CAM-01
```

This is expected because the current development setup still uses one webcam.

The camera ID structure is already in place so that future cameras can be added without redesigning the event records.

---

## 9. Evidence coverage

The report found:

```text
Evidence-linked events: 4
```

This is also consistent with the project history.

The first seven events were recorded before Sentinel began saving evidence images.

The four later events have evidence paths linked to JPEG files.

So the current history contains a mixture of older and newer records.

That is a real part of the project's development history rather than something to hide or fill with fake data.

---

## 10. Latest event

The latest event currently stored was:

```text
Event ID:
EVT-20261002-133944-382960

Camera:
CAM-01

Start time:
2026-10-02 13:39:44

Region:
BOTTOM LEFT

Duration:
2.86 seconds
```

This corresponds to the second event from the Day 10 testing session.

---

## 11. Full event table

The generated report also includes all 11 stored events with:

```text
Event ID
Camera
Region
Motion area
Duration
Evidence availability
```

This gives a simple way to inspect the history without manually opening the CSV.

---

## 12. What I learned

### Stored data becomes more useful when it can be summarized

Before this step, the CSV was mainly a place where Sentinel stored information.

Now another part of the system can read that information and turn it into useful summaries.

That is the beginning of an analytics layer.

---

### Separate tools make the project easier to grow

Keeping analytics in:

```text
src/event_summary.py
```

instead of adding everything to `main.py` is cleaner.

The live detection system has one job.

The analytics script has another job.

Later, a dashboard can use the same stored data without needing to rewrite the detection system.

---

### Early data needs context

The report contains events from different stages of the project.

Some have evidence.

Some do not.

Some contain bounding-box information.

Older ones do not.

That is normal for a developing project, and the analytics system needs to describe the data as it really exists rather than pretending every record was created with the final schema.

---

## 13. Current limitations

This is still a basic analytics layer.

It only analyzes the information already stored in the CSV.

It does not yet understand:

```text
person
vehicle
animal
intrusion
normal activity
unusual behaviour
```

It also does not yet display the evidence images alongside the event records.

The data is still stored in CSV format, which is convenient for now but will eventually become less suitable as the number of events grows.

---

## 14. What Day 11 accomplished

By the end of Day 11, Sentinel could:

* read its stored event history
* calculate total event count
* calculate total event duration
* calculate average event duration
* identify the longest event
* identify the largest recorded motion area
* group events by region
* group events by camera
* count evidence-linked events
* identify the latest event
* generate a human-readable Markdown report

The system now looks more like:

```text
Camera
   ↓
Detection
   ↓
Event
   ↓
Evidence + History
   ↓
Analytics
   ↓
Report
```

That is a meaningful change from the earlier stages because Sentinel is starting to learn from the information it has already collected.

---

## 15. Current status

**Day 11 technical work:** COMPLETE

**Event history analysis:** WORKING

**Event count:** WORKING

**Duration statistics:** WORKING

**Region statistics:** WORKING

**Camera statistics:** WORKING

**Evidence statistics:** WORKING

**Latest-event lookup:** WORKING

**Markdown report generation:** WORKING

**Real event data used:** YES

**Report generated successfully:** YES

**Documentation:** COMPLETE

**Git commit:** PENDING

**GitHub push:** PENDING

---

## Day 11 conclusion

Day 11 moved Sentinel from simply collecting event data to actually using that data.

The result is still simple, but it gives us the first real analytics layer in the project.

More importantly, it is built on the event history that Sentinel has actually produced during testing.

This gives us a foundation for future features such as dashboards, trends, camera comparisons, and eventually more intelligent event analysis.

The development process remains:

**Build → Test → Observe → Improve → Document → Commit → Push.**
