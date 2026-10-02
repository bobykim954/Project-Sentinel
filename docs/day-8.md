# Project Sentinel — Day 8

## Event History and Logging

**Date:** 2 October 2026
**Project:** Project Sentinel
**Stage:** Day 8

---

## 1. What I wanted to improve

By Day 7, Sentinel could detect motion, estimate the region where it happened, and draw a bounding box around the main motion area.

The next problem was simple:

> What happens after Sentinel detects an event?

At the moment, the result was mainly printed in the terminal.

That meant the information would disappear once the program stopped.

For Day 8, I wanted Sentinel to start **remembering its events**.

The goal was to create a simple event history containing useful information about what happened.

The new idea was:

```text
Motion detected
      ↓
Event starts
      ↓
Collect event information
      ↓
Event ends
      ↓
Save event to history
```

---

## 2. Event information

For every completed event, Sentinel now stores:

```text
Event ID
Start time
End time
Region
Motion area
Duration
```

This gives each event a small record that can be used later.

For example:

```text
EVT-20261002-125729-360518
2026-10-02 12:57:29
2026-10-02 12:57:41
TOP LEFT
3697
12.45 seconds
```

---

## 3. Creating the event history file

I added a data directory:

```text
data/
```

and an event history file:

```text
data/events.csv
```

The program creates the directory automatically if it does not already exist.

It also creates the CSV headings the first time the file is needed:

```text
event_id,start_time,end_time,region,motion_area,duration_seconds
```

This means Sentinel does not need a database yet.

For this stage of the project, a simple CSV file is enough to prove that event information can be stored and retrieved.

---

## 4. Event IDs

Each event now receives its own ID.

The ID is generated using the current date and time:

```python
event_id = (
    "EVT-"
    + datetime.now().strftime(
        "%Y%m%d-%H%M%S-%f"
    )
)
```

A result can therefore look like:

```text
EVT-20261002-125729-360518
```

This gives each event a unique identifier that can later be used when connecting an event to a snapshot, video clip, alert, or dashboard entry.

---

## 5. Recording the event duration

When an event starts, Sentinel records the start time.

When the event ends, it records the end time and calculates the duration:

```python
duration = (
    event_end_time - event_start_time
).total_seconds()
```

The duration is then stored in the CSV file.

This gives Sentinel a new piece of information beyond simply saying that movement happened.

It can now answer:

> How long did the event last?

---

## 6. Testing the event history

I ran the updated Sentinel program and generated several events.

The terminal produced results including:

```text
EVENT STARTED! ID: EVT-20261002-125729-360518 | Region: TOP LEFT | Area: 3697
EVENT ENDED | ID: EVT-20261002-125729-360518 | Duration: 12.45s
```

Other events were detected in different regions, including:

```text
TOP LEFT
BOTTOM LEFT
BOTTOM RIGHT
```

The recorded durations ranged from less than one second to more than twenty seconds.

One of the longer events lasted:

```text
25.95 seconds
```

This showed that the event state could remain active for a longer period rather than immediately ending.

---

## 7. Verifying the saved file

After stopping the program, I checked the generated file using:

```powershell
Get-Content data\events.csv
```

The file contained the following real test records:

```text
event_id,start_time,end_time,region,motion_area,duration_seconds
EVT-20261002-125729-360518,2026-10-02 12:57:29,2026-10-02 12:57:41,TOP LEFT,3697,12.45
EVT-20261002-125742-543374,2026-10-02 12:57:42,2026-10-02 12:57:43,TOP LEFT,2746,1.39
EVT-20261002-125744-113469,2026-10-02 12:57:44,2026-10-02 12:57:45,BOTTOM LEFT,2250,1.26
EVT-20261002-125749-091187,2026-10-02 12:57:49,2026-10-02 12:57:50,BOTTOM RIGHT,1916,1.42
EVT-20261002-125750-761175,2026-10-02 12:57:50,2026-10-02 12:57:51,BOTTOM RIGHT,1036,0.99
EVT-20261002-125752-352344,2026-10-02 12:57:52,2026-10-02 12:58:18,BOTTOM RIGHT,1483,25.95
EVT-20261002-125820-561691,2026-10-02 12:58:20,2026-10-02 12:58:27,BOTTOM RIGHT,1597,7.25
```

This confirmed that Sentinel was not only displaying event information.

It was actually **saving the information to disk**.

---

## 8. What I learned

### Detection becomes more useful when it creates a record

There is a big difference between:

```text
EVENT STARTED
```

and:

```text
Event ID
Start time
End time
Region
Area
Duration
```

The second result can be stored, searched, analyzed, and eventually displayed in a dashboard.

That is an important step toward the larger Sentinel system.

---

### A CSV file is enough for this stage

I considered the fact that a proper surveillance platform will eventually need a database.

However, there was no reason to introduce database complexity yet.

A CSV file is simple, easy to inspect, and enough to prove that the event logging system works.

A database can come later when the amount of event data justifies it.

---

### Real test data exposes new problems

The test also showed that Sentinel can create several events close together.

For example, there were multiple short events in BOTTOM RIGHT:

```text
1.42 seconds
0.99 seconds
25.95 seconds
7.25 seconds
```

This tells me that the event system is working, but the way it groups nearby activity can still be improved.

That is useful information for a later stage.

---

## 9. Current limitations

The event history is currently stored in a simple CSV file.

The system does not yet save:

* a screenshot of the event
* a video clip
* an image of the detected motion
* object type
* camera ID
* confidence score

The event IDs are also based on the computer's current system time, so synchronization across multiple cameras will need more thought later.

Another limitation is that separate short events can be created when activity happens close together.

This is not being hidden; it is part of the current behaviour of the system and gives us something to improve later.

---

## 10. What Day 8 accomplished

By the end of Day 8, Sentinel could:

* detect an event
* generate a unique event ID
* record when the event started
* record when the event ended
* calculate event duration
* record the approximate region
* record the detected motion area
* save the completed event to a CSV file
* preserve the event after the program is closed

The pipeline is now:

```text
Camera
   ↓
Frame Difference
   ↓
Motion Mask
   ↓
Motion Area
   ↓
Bounding Box
   ↓
Region
   ↓
Event State
   ↓
Event Record
   ↓
data/events.csv
```

---

## 11. Current status

**Day 8 technical work:** COMPLETE

**Event ID generation:** WORKING

**Start time recording:** WORKING

**End time recording:** WORKING

**Duration calculation:** WORKING

**Region recording:** WORKING

**Motion-area recording:** WORKING

**CSV event storage:** WORKING

**Real test:** COMPLETED

**Saved-data verification:** COMPLETED

**Documentation:** COMPLETE

**Git commit:** PENDING

**GitHub push:** PENDING

---

## Day 8 conclusion

Day 8 gave Sentinel something it did not have before:

**memory.**

The system is no longer only reacting to what the camera sees right now.

It can record what happened and keep that information after the program stops.

The implementation is intentionally simple. A CSV file is not the final storage system for Sentinel, but it is a practical starting point and it works.

The real test also exposed another issue: several short events can be created during nearby activity. That is something the project can improve later instead of hiding it.

This is how Sentinel is being built:

**Build → Test → Observe → Improve → Document → Commit → Push.**
