# Project Sentinel — Day 13

## Rule-Based Event Priority

**Date:** 3 October 2026
**Project:** Project Sentinel
**Stage:** Day 13

---

## 1. What I wanted to improve

By Day 12, Sentinel had a working local dashboard showing its event history.

The system could now detect events, store evidence, keep metadata, analyze the history, and display the results.

However, all events were still being treated the same way.

For a future surveillance system, it would be useful to have a simple way to separate events that deserve more attention from events that appear relatively minor.

So on Day 13, I added a small **rule-based event priority system**.

The goal was:

```text id="t7d3j7"
Stored Event
     ↓
Read event information
     ↓
Apply simple rules
     ↓
Assign priority
     ↓
Generate priority report
```

---

## 2. Why I kept this separate

I did not add the priority logic directly into `src/main.py`.

The camera and detection pipeline is already working, so there was no reason to make the core program more complicated just to add this feature.

I created:

```text id="88cb7h"
src/event_priority.py
```

The script reads the existing:

```text id="2ezcqi"
data/events.csv
```

and generates:

```text id="v0z6a7"
reports/event-priority.md
```

This keeps detection, storage, analysis, and prioritization as separate pieces.

---

## 3. Priority rules

The first version uses simple rules based on two values Sentinel already records:

```text id="p8a6ne"
Motion area
Event duration
```

The current rules are:

```text id="tq0uj0"
HIGH
Motion area >= 3000
OR duration >= 10 seconds

MEDIUM
Motion area >= 1500
OR duration >= 3 seconds

LOW
Everything else
```

These values are not meant to represent a real security standard.

They are simply a starting point that can be tested and changed as more real data becomes available.

---

## 4. Why a rule-based system was used

At this stage, Sentinel does not know what caused an event.

It cannot reliably distinguish:

```text id="d3mqe1"
Person
Vehicle
Animal
Shadow
Lighting change
Other movement
```

So it would be misleading to pretend that the system can determine whether an event is actually dangerous.

Instead, the priority system uses measurable information that Sentinel already has.

This makes the behaviour transparent.

For example:

```text id="o6b5fs"
Large motion area
        +
Long duration
        ↓
Higher priority
```

The rules can later be replaced or extended when Sentinel has more information.

---

## 5. Testing

I ran:

```powershell id="d4t3d7"
python src/event_priority.py
```

The script successfully loaded the current event history:

```text id="gcmag4"
Loaded 11 events.
```

It then classified the events:

```text id="q83m6a"
HIGH: 3
MEDIUM: 6
LOW: 2
```

The report was generated at:

```text id="3y0mrv"
reports/event-priority.md
```

---

## 6. Results from the real event history

The current 11 events were divided as follows:

```text id="mc27p1"
HIGH    → 3
MEDIUM  → 6
LOW     → 2
```

Some examples from the stored history:

```text id="f8ywh0"
5294 motion area, 3.60s
→ HIGH

1483 motion area, 25.95s
→ HIGH

3697 motion area, 12.45s
→ HIGH
```

On the lower end:

```text id="nbguj9"
892 motion area, 1.86s
→ LOW

1036 motion area, 0.99s
→ LOW
```

Other events fell into the MEDIUM category because they met one of the medium-level conditions.

---

## 7. What I learned

### Existing data can support new features

One of the useful things about the project structure so far is that the priority engine does not need to touch the camera.

It simply reads data Sentinel has already collected.

That means the same event history can support multiple layers:

```text id="h2rllk"
Event history
    ↓
Analytics
    ↓
Dashboard
    ↓
Priority
```

This makes the system easier to extend.

---

### Transparent rules are useful during development

The rules are simple enough that I can look at an event and understand why it received a particular priority.

That is useful at this stage because I am still learning what the real event data looks like.

Later, the rules can be changed based on actual testing.

---

### Priority does not mean danger

This is important.

A HIGH event in the current system only means that its motion area or duration crossed the configured thresholds.

It does **not** mean:

```text
Intruder detected
Danger detected
Crime detected
```

Those would require much more context and better detection capabilities.

---

## 8. Current limitations

The current priority system is based only on:

```text id="t6g9n9"
Motion area
Duration
```

It does not consider:

* object type
* time of day
* known/unknown person
* camera location
* repeated behaviour
* zones of interest
* other cameras
* previous events
* actual security context

Because of this, the priority levels should currently be treated as **simple attention categories** rather than security judgments.

---

## 9. What Day 13 accomplished

By the end of Day 13, Sentinel could:

* read stored event history
* apply transparent priority rules
* assign HIGH, MEDIUM, or LOW priority
* summarize priority counts
* list all events with their assigned priority
* identify high-priority events
* generate a separate Markdown priority report

The updated architecture is:

```text id="1u4l9i"
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
   ↓
Priority
```

---

## 10. Current status

**Day 13 technical work:** COMPLETE

**Priority engine:** WORKING

**Rule-based classification:** WORKING

**Priority summary:** WORKING

**High-priority event listing:** WORKING

**Real event history used:** YES

**11 existing events analyzed:** YES

**Priority report generated:** YES

**Documentation:** COMPLETE

**Git commit:** PENDING

**GitHub push:** PENDING

---

## Day 13 conclusion

Day 13 added a simple decision layer on top of Sentinel's existing event data.

The system can now look at stored event information and decide how much attention an event should receive according to transparent rules.

It is intentionally not presented as intelligent threat detection.

At this stage, the value is in building the structure that future, more advanced intelligence can use.

The priority engine is also another example of keeping the system modular: the camera does not need to know anything about event prioritization.

The development process remains:

**Build → Test → Observe → Improve → Document → Commit → Push.**
