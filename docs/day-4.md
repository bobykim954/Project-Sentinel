# Project Sentinel — Day 4

## Scene Change Detection

**Date:** September 2026
**Project:** Project Sentinel
**Stage:** Day 4

---

## 1. What I wanted to achieve

On Day 3, Sentinel could look at a camera frame and calculate its average brightness.

That was useful, but it was still very basic. Sentinel could tell me whether a frame was generally bright or dark, but it could not yet answer a more important surveillance question:

> **Did something actually change in the scene?**

So the goal for Day 4 was to make Sentinel compare the current camera frame with the previous one and detect when there was a significant change.

The basic idea was:

```text
Live Camera
     ↓
Current Frame
     ↓
Convert to Grayscale
     ↓
Compare with Previous Frame
     ↓
Calculate Difference
     ↓
Measure Change
     ↓
"CHANGE DETECTED"
```

This is still a simple computer-vision approach, but it is an important step toward the event detection system I eventually want Sentinel to have.

---

## 2. The approach

Instead of comparing the full colour information of two frames, I first converted each frame to grayscale.

```python
gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
```

This makes the comparison simpler because Sentinel is mainly interested in how much the image has changed, rather than the exact colour of every pixel.

I then kept the previous frame:

```python
previous_frame = None
```

Once Sentinel had both a previous frame and a current frame, I used OpenCV's absolute difference function:

```python
difference = cv2.absdiff(previous_frame, gray_frame)
```

This produces a new image showing how different the two frames are.

I then calculated the average difference:

```python
change_level = difference.mean()
```

This gives Sentinel one number representing how much the scene changed between the two frames.

Finally, I used a threshold to decide when the change was large enough to report:

```python
CHANGE_THRESHOLD = 20

if change_level >= CHANGE_THRESHOLD:
    print(f"CHANGE DETECTED! Level: {change_level:.2f}")
```

---

## 3. Testing the threshold

I did not want to choose a threshold completely at random.

First, I watched the values produced while the camera scene was relatively stable.

Most small changes were around:

```text
0.2 – 0.7
```

Some normal movement or smaller changes produced values around:

```text
1 – 12
```

Larger changes started reaching approximately:

```text
17 – 20+
```

Strong changes produced much larger values, including:

```text
54+
60+
65+
```

Based on these observations, I set:

```python
CHANGE_THRESHOLD = 20
```

The idea was to allow small natural changes in the camera image without immediately treating everything as an event.

This is only a starting threshold. A real CCTV environment will need proper calibration because lighting, shadows, camera position, image quality and normal activity will all affect the values.

---

## 4. Final test

After setting the threshold to 20, I ran the detector again and deliberately created changes in front of the camera.

Sentinel produced:

```text
CHANGE DETECTED! Level: 32.57
CHANGE DETECTED! Level: 40.63
CHANGE DETECTED! Level: 24.98
CHANGE DETECTED! Level: 23.02
CHANGE DETECTED! Level: 59.17
CHANGE DETECTED! Level: 30.76
CHANGE DETECTED! Level: 54.09
CHANGE DETECTED! Level: 22.65
```

These values were all above the threshold of 20, so Sentinel correctly treated them as significant scene changes.

This was the first point where the project started behaving more like a surveillance system rather than just a camera display.

---

## 5. What I learned

### Grayscale makes the comparison simpler

I don't need all three BGR colour channels just to determine whether the scene changed.

Grayscale gives me a simpler representation that is easier to compare.

### Difference gives Sentinel something measurable

Instead of simply saying:

> "The camera image looks different."

Sentinel now produces a numerical value such as:

```text
32.57
```

That number can then be used by the program to make decisions.

### A threshold turns measurement into a decision

The value itself is not yet an alert.

The threshold is what allows Sentinel to make a basic decision:

```text
Change level < 20
        ↓
Probably normal/small change

Change level >= 20
        ↓
Significant change detected
```

### Real testing matters

The threshold of 20 was not chosen just because it looked good in theory.

I tested the camera and looked at the actual values being produced.

That gave me a better starting point for the detector.

---

## 6. Current limitation

There is an obvious problem with the current version.

If someone walks in front of the camera for several seconds, Sentinel can print:

```text
CHANGE DETECTED!
CHANGE DETECTED!
CHANGE DETECTED!
CHANGE DETECTED!
```

Even though it may actually be one continuous event.

So at the moment, Sentinel can detect that something is changing, but it does not yet understand the difference between:

> "A new event has started"

and:

> "The same event is still happening."

That is something I need to improve.

---

## 7. What Day 4 accomplished

By the end of Day 4, Sentinel had moved from simply reading camera frames to performing a basic comparison between frames.

The current pipeline is:

```text
Camera
  ↓
Frame Capture
  ↓
Grayscale Conversion
  ↓
Previous Frame
  ↓
Frame Difference
  ↓
Average Change Level
  ↓
Threshold
  ↓
CHANGE DETECTED
```

This is still a simple system, but it is now becoming the foundation for the event-detection side of Project Sentinel.

---

## 8. Current status

**Day 4 technical work: COMPLETE**

**Documentation: COMPLETE**

**Git commit: PENDING**

**GitHub push: PENDING**

The next step is to commit this work and push it to GitHub before moving on.

---

## 9. Next step — Day 5

Day 5 will focus on making the detection more useful.

The first problem to solve is repeated alerts.

Instead of reporting every frame that crosses the threshold, Sentinel should begin to understand an event as something with a beginning and an end.

For example:

```text
No activity
     ↓
Change detected
     ↓
EVENT STARTED
     ↓
Activity continues
     ↓
Activity stops
     ↓
EVENT ENDED
```

This should make the system less noisy and closer to how a real surveillance system would handle events.

Later, Sentinel can go further and determine **where in the camera view the change happened**, rather than simply saying that something changed somewhere in the frame.

---

## Day 4 conclusion

Day 4 was the first real step toward making Sentinel react to what is happening in front of a camera.

It is not AI yet, and it is not pretending to be a finished surveillance system.

It is a small piece of computer vision that works, has been tested, and gives us something solid to build on.

**Build → Test → Observe → Document → Commit → Push.**

That is the workflow for Sentinel.
