# Project Sentinel — Day 6

## Motion Location Detection

**Date:** 26 September 2026
**Project:** Project Sentinel
**Stage:** Day 6

---

## 1. What I wanted to improve

By Day 5, Sentinel could detect when an event started and ended.

The next question was:

> **Where did the change happen?**

The previous version treated the whole camera image as one area. That meant Sentinel could tell that something changed, but it could not give even a basic indication of where the activity was happening.

For Day 6, I decided to divide the camera view into four simple regions:

```text
+-------------------+-------------------+
|                   |                   |
|    TOP LEFT       |    TOP RIGHT      |
|                   |                   |
+-------------------+-------------------+
|                   |                   |
|   BOTTOM LEFT     |   BOTTOM RIGHT    |
|                   |                   |
+-------------------+-------------------+
```

The idea was to compare the amount of actual motion in each region and report the region with the strongest change.

---

## 2. First approach

The first version calculated the average frame difference for each region and selected the region with the largest value.

During testing, this worked sometimes, but it also produced some inconsistent results.

This exposed an important problem:

> The region with the largest average difference is not always the region containing the most useful movement.

So I changed the approach instead of simply repeating the same test.

---

## 3. Improved motion detection

The updated version first converts the frame to grayscale and applies a small Gaussian blur.

```python
gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

gray_frame = cv2.GaussianBlur(
    gray_frame,
    (5, 5),
    0
)
```

The blur helps reduce tiny changes and camera noise before comparing frames.

I then calculate the absolute difference between the previous and current frames:

```python
difference = cv2.absdiff(
    previous_frame,
    gray_frame
)
```

Instead of using the raw difference directly, I apply a pixel-level threshold:

```python
_, motion_mask = cv2.threshold(
    difference,
    25,
    255,
    cv2.THRESH_BINARY
)
```

This means very small pixel changes are ignored.

I also use a small morphological operation to remove isolated noise from the motion mask.

After that, the motion mask is divided into four regions.

---

## 4. Measuring motion by region

For each region, Sentinel counts the number of changed pixels.

It then converts that into a percentage:

```text
Changed pixels ÷ Total pixels × 100
```

This gives Sentinel a much more useful measurement.

For example:

```text
TOP LEFT       → 0.40%
TOP RIGHT      → 1.10%
BOTTOM LEFT    → 8.90%
BOTTOM RIGHT   → 0.60%
```

In that situation, BOTTOM LEFT would be the strongest region because a much larger percentage of that area actually changed.

---

## 5. Calibration during testing

The first improved version used:

```python
REGION_MOTION_THRESHOLD = 1.5
```

Testing showed that this was too sensitive.

Sentinel produced many small events between roughly:

```text
1.54% – 2.09%
```

These happened too frequently to treat as reliable movement.

At the same time, the tests also produced much stronger values such as:

```text
13.55%
29.73%
46.80%
```

Those values showed that genuine movement could produce substantially larger motion percentages.

So I increased the threshold to:

```python
REGION_MOTION_THRESHOLD = 3.0
```

I also reduced the number of confirmation frames from 3 to 2:

```python
START_CONFIRM_FRAMES = 2
```

This was done because the 5% threshold and 3-frame confirmation were too restrictive during the next test. Sentinel stopped responding properly to movement.

The final calibration used for the successful test was therefore:

```python
REGION_MOTION_THRESHOLD = 3.0
START_CONFIRM_FRAMES = 2
```

---

## 6. Final Day 6 test

After the calibration changes, I ran:

```text
python src/main.py
```

The verified output was:

```text
EVENT STARTED! Region: BOTTOM LEFT | Motion: 8.92%
EVENT ENDED
```

This confirmed that the improved system was able to detect a significant regional motion event and maintain the Day 5 event lifecycle.

The reported motion level of:

```text
8.92%
```

was comfortably above the configured 3.0% threshold.

---

## 7. What I learned

### Average difference is not enough

A single average change value for a region can be misleading.

Counting changed pixels gives Sentinel a better idea of how much of the region was actually affected.

### Thresholds need real testing

The first threshold looked reasonable in theory but produced too many small detections.

The actual webcam tests showed that I needed to adjust the threshold based on observed behaviour.

This was a useful reminder that computer-vision values cannot simply be guessed and expected to work everywhere.

### More sensitivity is not always better

When the threshold was too low, Sentinel became noisy.

When the threshold and confirmation requirements were too high, Sentinel became too difficult to trigger.

The goal is therefore not maximum sensitivity.

The goal is a useful balance between:

```text
Too sensitive → noise
Too strict    → missed movement
Balanced      → useful detection
```

---

## 8. Current limitations

The current system still has important limitations.

First, the camera is divided into only four large regions. This gives a rough location, not an exact position.

Second, Sentinel selects the region with the highest motion percentage. If several regions change at the same time, the reported region may not describe everything that happened.

Third, the system still detects visual change rather than understanding the object causing that change.

At this stage Sentinel cannot yet distinguish between:

```text
Person
Vehicle
Animal
Shadow
Lighting change
Other movement
```

It simply detects motion in the image.

These limitations are expected at this stage of the project.

---

## 9. Day 6 result

By the end of Day 6, Sentinel could:

* reduce small camera noise before motion analysis
* create a basic motion mask
* divide the camera into four regions
* measure the percentage of changed pixels in each region
* select the region with the strongest detected movement
* use the Day 5 event-state logic
* start an event when sufficient regional motion is detected
* end the event after the scene becomes quiet again

The current pipeline is now:

```text
Camera
   ↓
Frame Capture
   ↓
Grayscale
   ↓
Noise Reduction
   ↓
Frame Difference
   ↓
Motion Mask
   ↓
Four Regions
   ↓
Regional Motion Percentage
   ↓
Motion Threshold
   ↓
Event State
   ↓
EVENT STARTED
   ↓
EVENT ENDED
```

---

## 10. Current status

**Day 6 technical work:** COMPLETE

**Motion mask:** WORKING

**Regional analysis:** WORKING

**Event start/end:** WORKING

**Threshold calibration:** COMPLETED

**Final verified test:** COMPLETED

**Documentation:** COMPLETE

**Git commit:** PENDING

**GitHub push:** PENDING

---

## Day 6 conclusion

Day 6 was not just about adding another piece of code.

It was also about learning from the behaviour of the system.

The first version was too sensitive, the next version became too strict, and the final calibration gave a more usable result.

That is an important part of building Sentinel.

I am not trying to make the project look perfect on paper. I am testing it, finding where it behaves badly, and improving it based on what actually happens.

Sentinel now has a basic sense of **where motion is happening**, in addition to knowing that an event occurred.

The next stages can build on this foundation and eventually move toward identifying **what** caused the motion.

**Build → Test → Observe → Improve → Document → Commit → Push.**
