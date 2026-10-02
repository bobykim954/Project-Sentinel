# Project Sentinel — Day 9

## Event Evidence Capture

**Date:** 2 October 2026
**Project:** Project Sentinel
**Stage:** Day 9

---

## 1. What I wanted to improve

On Day 8, Sentinel learned how to keep a history of detected events.

It could record things like:

* when an event started
* when it ended
* where it happened
* the detected motion area
* how long it lasted

That was useful, but there was still a missing piece.

If Sentinel says that an event happened, it would be much more useful to also have a picture of what the camera saw at that moment.

So the goal for Day 9 was:

> **Save visual evidence when an event starts.**

The new flow is:

```text
Motion detected
      ↓
Event confirmed
      ↓
Create event ID
      ↓
Capture camera frame
      ↓
Save evidence image
      ↓
Continue event
      ↓
Event ends
      ↓
Save event record
```

---

## 2. Creating an evidence folder

I added a new folder inside the project data directory:

```text
data/
├── events.csv
└── evidence/
```

The program creates the folder automatically if it does not exist.

Each saved image uses the event ID as its filename.

For example:

```text
EVT-20261002-132119-717016.jpg
```

This makes it possible to connect an event record in `events.csv` with its corresponding image.

---

## 3. Capturing the evidence

When an event is confirmed, Sentinel generates an event ID and saves the current camera frame.

The evidence file is created using:

```python
evidence_filename = event_id + ".jpg"
```

and then:

```python
cv2.imwrite(
    event_evidence_path,
    original_frame
)
```

I deliberately save the original frame before drawing the debugging information and bounding box on it.

This means the evidence image represents what the camera actually saw, rather than just being a screenshot of the program window.

---

## 4. Test run

I ran the updated program and generated two events.

The first event produced:

```text
Evidence saved: data/evidence\EVT-20261002-132119-717016.jpg
EVENT STARTED! ID: EVT-20261002-132119-717016 | Region: BOTTOM LEFT | Area: 5294
EVENT ENDED | ID: EVT-20261002-132119-717016 | Duration: 3.60s
```

The second event produced:

```text
Evidence saved: data/evidence\EVT-20261002-132124-597336.jpg
EVENT STARTED! ID: EVT-20261002-132124-597336 | Region: TOP LEFT | Area: 2982
EVENT ENDED | ID: EVT-20261002-132124-597336 | Duration: 2.27s
```

This showed that Sentinel could create separate evidence files for separate events.

---

## 5. Verifying the evidence files

After stopping the program, I checked the evidence directory.

The result showed two JPEG files:

```text
EVT-20261002-132119-717016.jpg
EVT-20261002-132124-597336.jpg
```

Their file sizes were approximately:

```text
89 KB
90 KB
```

This confirmed that the files were actually created on disk.

---

## 6. Verifying the event history

I also checked:

```powershell
Get-Content data\events.csv
```

The two new events had been added successfully:

```text
EVT-20261002-132119-717016,2026-10-02 13:21:19,2026-10-02 13:21:23,BOTTOM LEFT,5294,3.60
EVT-20261002-132124-597336,2026-10-02 13:21:24,2026-10-02 13:21:26,TOP LEFT,2981,2.27
```

This is important because the event history and evidence files now share the same event IDs.

For example:

```text
Event:
EVT-20261002-132119-717016

Evidence:
EVT-20261002-132119-717016.jpg
```

This gives us a simple connection between an event and its visual evidence.

---

## 7. What I learned

### An event becomes more useful when there is evidence

Before Day 9, Sentinel could tell me something happened.

Now it can keep a picture associated with that event.

That makes the event record more useful for future investigation and analysis.

---

### Event IDs can connect different parts of the system

The same ID is now used for:

```text
Event history
    +
Evidence image
```

This will become increasingly useful as Sentinel grows.

Later, the same ID could also connect:

```text
Event
 +
Snapshot
 +
Video clip
 +
Alert
 +
Camera
```

without having to build the whole system at once.

---

### The simplest storage method is still enough for now

I'm still using:

```text
CSV + JPEG
```

instead of introducing a database or more complicated storage system.

For the current stage, this is enough to prove that Sentinel can generate and preserve event evidence.

More advanced storage can come later when the project actually needs it.

---

## 8. Current limitations

The current evidence system only saves **one image when the event starts**.

It does not yet save:

* a full video clip
* multiple images during the event
* the exact camera source
* object type
* confidence score
* a description of what caused the event

The snapshot also represents the scene at the moment the event is confirmed. It is not a full record of everything that happened during the event.

These are future improvements rather than problems I need to solve immediately.

---

## 9. What Day 9 accomplished

By the end of Day 9, Sentinel could:

* detect an event
* generate a unique event ID
* capture the current camera frame
* save that frame as a JPEG
* name the image using the event ID
* record the event in `events.csv`
* connect the event record to its evidence file
* preserve the evidence after the program stops

The pipeline is now:

```text
Camera
   ↓
Motion Detection
   ↓
Motion Localization
   ↓
Event State
   ↓
Event ID
   ↓
Evidence Snapshot
   ↓
Event History
```

---

## 10. Current status

**Day 9 technical work:** COMPLETE

**Event ID generation:** WORKING

**Evidence folder:** WORKING

**JPEG snapshot capture:** WORKING

**Evidence naming:** WORKING

**Event history logging:** WORKING

**Event/evidence connection:** WORKING

**Real webcam test:** COMPLETED

**Evidence files verified:** COMPLETED

**CSV records verified:** COMPLETED

**Documentation:** COMPLETE

**Git commit:** PENDING

**GitHub push:** PENDING

---

## Day 9 conclusion

Day 9 added something important to Sentinel: **evidence**.

The system can now detect an event and keep a picture from that moment instead of only printing a message in the terminal.

It is still a basic implementation, but it gives us a foundation for something much more useful later.

The next step can build on this by making the stored events easier to review and work with.

The development process remains:

**Build → Test → Observe → Improve → Document → Commit → Push.**
