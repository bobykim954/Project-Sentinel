# Project Sentinel — Day 5

## Event Detection

**Date:** 25 September 2026
**Project:** Project Sentinel
**Stage:** Day 5

---

## 1. What I wanted to improve

On Day 4, Sentinel learned how to detect a significant change between two camera frames.

That worked, but testing exposed a problem.

If something kept moving in front of the camera, Sentinel could keep reporting:

```text
CHANGE DETECTED!
CHANGE DETECTED!
CHANGE DETECTED!
```

The problem is that several changed frames can actually belong to one real-world event.

For example, one person walking past the camera may cause many frames to change, but from a surveillance point of view, that should normally be treated as one event.

So on Day 5, the goal was to make Sentinel understand the basic idea of an **event**.

The new behaviour should be:

```text
No Activity
    ↓
Change Detected
    ↓
EVENT STARTED
    ↓
Activity Continues
    ↓
No Repeated Start Alerts
    ↓
Activity Stops
    ↓
EVENT ENDED
```

---

## 2. The idea behind the solution

I gave Sentinel a simple way to remember whether an event is already active.

The main variable is:

```python
event_active = False
```

At the beginning, there is no event.

When the change level reaches the detection threshold, Sentinel checks whether an event is already active.

If there is no active event, it starts one:

```python
if not event_active:
    event_active = True

    print(
        f"EVENT STARTED! Change level: {change_level:.2f}"
    )
```

Once `event_active` becomes `True`, Sentinel does not keep printing new `EVENT STARTED` messages for every changed frame.

This is what removes the repeated-alert problem from Day 4.

---

## 3. Deciding when an event has ended

The next problem was deciding when to stop an event.

A single frame with little change does not necessarily mean that activity has ended.

There can be small movements, camera noise, or other natural changes.

So I added a counter:

```python
no_change_frames = 0
```

and a limit:

```python
NO_CHANGE_FRAMES_TO_END = 30
```

When the scene remains below the change threshold, Sentinel counts those frames.

Once it reaches 30 consecutive frames without significant change, Sentinel ends the event:

```python
if no_change_frames >= NO_CHANGE_FRAMES_TO_END:
    event_active = False
    no_change_frames = 0

    print("EVENT ENDED")
```

This gives Sentinel a simple event lifecycle instead of treating every changed frame as a separate alert.

---

## 4. The updated detection flow

The Day 4 system was basically:

```text
Camera
   ↓
Current Frame
   ↓
Previous Frame
   ↓
Frame Difference
   ↓
Change Level
   ↓
Threshold
   ↓
CHANGE DETECTED
```

Day 5 extended it to:

```text
Camera
   ↓
Current Frame
   ↓
Previous Frame
   ↓
Frame Difference
   ↓
Change Level
   ↓
Threshold
   ↓
Event State
   ↓
EVENT STARTED
   ↓
Event Continues
   ↓
EVENT ENDED
```

The important difference is that Sentinel now keeps some state between frames.

---

## 5. Testing

I tested the updated program directly from PowerShell:

```text
python src/main.py
```

### First test

The first test produced:

```text
EVENT STARTED! Change level: 21.71
EVENT ENDED
EVENT STARTED! Change level: 21.40
EVENT ENDED
```

This showed that Sentinel could recognize more than one separate event.

After one event ended, it was able to return to an inactive state and detect another event later.

### Second test

I ran the program again with another controlled movement test.

The result was:

```text
EVENT STARTED! Change level: 20.30
EVENT ENDED
```

This was especially useful because only one start message appeared for the event.

There was no continuous stream of:

```text
EVENT STARTED!
EVENT STARTED!
EVENT STARTED!
```

That confirmed that the event-state logic was working for the test.

---

## 6. What I learned

### A change is not automatically a new event

This was one of the main lessons from Day 5.

A camera can produce many changed frames during one real-world activity.

For example:

```text
Person enters the scene
        ↓
Many frames change
        ↓
Person keeps moving
        ↓
Person leaves
```

That can represent one event even though hundreds of individual frames were different.

This means a useful surveillance system needs some logic above simple frame comparison.

---

### Sentinel now has memory

Before Day 5, Sentinel mainly evaluated each frame comparison independently.

Now it remembers whether an event is currently active:

```python
event_active = True
```

That small piece of state makes the system behave much more like an actual event detector.

---

### Ending an event needs some patience

I learned that an event should not be ended immediately just because one frame falls below the threshold.

Using a number of consecutive quiet frames gives Sentinel some stability.

In this version:

```python
NO_CHANGE_FRAMES_TO_END = 30
```

means Sentinel waits for 30 consecutive frames without significant change before declaring:

```text
EVENT ENDED
```

---

## 7. Current limitations

The system is still intentionally simple.

### Fixed threshold

The detector still uses:

```python
CHANGE_THRESHOLD = 20
```

This worked during the webcam tests, but it is not a universal value.

A real CCTV environment can behave differently because of:

* lighting changes
* shadows
* camera noise
* weather
* moving trees
* crowded areas
* different camera frame rates

The threshold will therefore need proper calibration later.

### No understanding of the object

Sentinel can currently say:

> Something changed in the scene.

It cannot yet say:

> A person moved near the entrance.

It also does not yet know whether the movement came from a person, vehicle, animal, shadow, or some other change.

### No location inside the frame

The current calculation produces one number for the whole frame.

So Sentinel knows that a significant change happened, but it does not yet know exactly where that change happened.

That is another area for future improvement.

---

## 8. What Day 5 accomplished

By the end of Day 5, Sentinel could:

* detect the beginning of an event
* remember that an event is already active
* avoid repeatedly starting the same event
* wait for a quiet period
* detect when the event has ended
* return to a state where another event can be detected

The result is a basic event lifecycle:

```text
IDLE
  ↓
EVENT STARTED
  ↓
EVENT ACTIVE
  ↓
EVENT ENDED
  ↓
IDLE
```

This is a small change compared with Day 4, but it makes the system much more useful.

---

## 9. Current status

**Day 5 technical work:** COMPLETE

**Event start detection:** WORKING

**Event state tracking:** WORKING

**Event end detection:** WORKING

**Repeated alert problem:** IMPROVED

**Real webcam testing:** COMPLETED

**Documentation:** COMPLETE

**Git commit:** PENDING

**GitHub push:** PENDING

---

## 10. Next direction

The next useful improvement is to make Sentinel understand **where** the activity is happening.

At the moment, the whole camera image is reduced to one change value.

A better approach would be to divide the camera view into areas and measure them separately.

For example:

```text
+-----------------------+
|         |             |
| Region  |   Region    |
|    1    |      2      |
|---------+-------------|
|         |             |
| Region  |   Region    |
|    3    |      4      |
+-----------------------+
```

Then Sentinel could begin answering a more useful question:

> **Which part of the scene changed?**

That will move the project closer to useful surveillance analytics instead of simple scene-change detection.

---

## Day 5 conclusion

Day 5 gave Sentinel a basic understanding of the difference between a **frame change** and an **event**.

The system is still simple, and it is not pretending to be a finished AI surveillance platform.

But it now has a small amount of memory, can recognize the beginning and end of activity, and has been tested with the actual webcam.

That gives us a solid base for the next stage.

**Build → Test → Observe → Document → Commit → Push.**

That remains the development workflow for Project Sentinel.
