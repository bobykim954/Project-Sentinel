# Project Sentinel — Day 7

## Motion Localization with Bounding Boxes

**Date:** 2 October 2026
**Project:** Project Sentinel
**Stage:** Day 7

---

## 1. What I wanted to improve

By Day 6, Sentinel could detect motion and give a rough indication of which quarter of the camera view contained the strongest movement.

The problem was that the four regions were still quite large.

For example, Sentinel could say:

```text
BOTTOM LEFT
```

but that did not tell me exactly where inside the bottom-left area the movement was happening.

For Day 7, I wanted Sentinel to get a little more precise.

The goal was to detect the actual area of changed pixels and draw a box around the main motion area.

The idea was:

```text
Camera
   ↓
Frame Difference
   ↓
Motion Mask
   ↓
Find Motion Areas
   ↓
Select Main Motion Area
   ↓
Draw Bounding Box
   ↓
Estimate Region
   ↓
Event
```

---

## 2. Using contours

Instead of only calculating the amount of change in each large region, I used OpenCV contours.

The motion mask is first created from the difference between consecutive grayscale frames.

Then OpenCV looks for connected areas inside that mask:

```python
contours, _ = cv2.findContours(
    motion_mask,
    cv2.RETR_EXTERNAL,
    cv2.CHAIN_APPROX_SIMPLE
)
```

Each contour represents an area where Sentinel detected connected motion.

I then measured the size of each contour and kept the largest useful one.

---

## 3. Filtering small motion areas

Not every changed pixel represents useful movement.

Camera noise and very small changes can create tiny contours, so I added:

```python
MIN_CONTOUR_AREA = 800
```

A contour smaller than this value is ignored.

This gives Sentinel a simple way to remove some small unwanted motion areas.

---

## 4. The first bounding-box test

The first Day 7 version successfully detected motion areas and produced bounding boxes.

However, during testing I noticed that sometimes **two or even three boxes** appeared around what looked like one moving subject.

This made sense because a moving person can produce several disconnected areas of changed pixels.

For example:

```text
Arm movement  → one motion area
Body movement → another motion area
Edges/shadows → another motion area
```

So the detector was working, but the visual result was not always clean.

I recorded this as a limitation instead of treating the first result as finished.

---

## 5. Improving the motion mask

To deal with nearby motion areas being separated, I added morphological processing.

First, small isolated noise is removed.

Then nearby motion areas are joined using morphological closing and dilation.

The idea is:

```text
Separate motion blobs
        ↓
Join nearby blobs
        ↓
Larger connected motion area
        ↓
One main bounding box
```

The updated processing uses:

```python
motion_mask = cv2.morphologyEx(
    motion_mask,
    cv2.MORPH_CLOSE,
    merge_kernel
)

motion_mask = cv2.dilate(
    motion_mask,
    merge_kernel,
    iterations=1
)
```

This made the motion mask less fragmented.

---

## 6. Selecting the main motion area

After the motion mask is cleaned, Sentinel searches for the largest useful contour.

The contour is converted into a bounding rectangle:

```python
x, y, box_width, box_height = largest_box
```

The rectangle is then drawn on the camera image:

```python
cv2.rectangle(
    frame,
    (x, y),
    (x + box_width, y + box_height),
    (255, 255, 255),
    2
)
```

This means the camera window can now show where Sentinel believes the main motion is happening.

---

## 7. Keeping the region information

I did not remove the Day 6 regional logic.

Instead, the centre of the bounding box is used to determine its approximate region.

The camera is still divided into:

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

This gives Sentinel both:

```text
Approximate region
+
Specific motion box
```

That is more useful than the Day 6 region label by itself.

---

## 8. Testing

I tested the updated version using the webcam.

The program produced the following results:

```text
EVENT STARTED! Region: TOP RIGHT | Area: 877
EVENT ENDED

EVENT STARTED! Region: TOP LEFT | Area: 3592
EVENT ENDED

EVENT STARTED! Region: BOTTOM LEFT | Area: 3960
```

The different area values show that Sentinel was detecting motion areas of different sizes depending on how much of the image changed.

The final event was still active when I stopped the program, so there was no `EVENT ENDED` message for that last event.

---

## 9. Visual result

During testing, the bounding box was visible in the camera window and generally appeared around the moving area.

This confirmed that the contour-based approach was doing more than simply producing numbers in the terminal.

Sentinel was now able to show a visual estimate of where the motion was occurring.

The result is still only an approximate motion location and should not be treated as object tracking.

---

## 10. What I learned

### Motion is made up of pixels, not objects

At this stage, Sentinel does not know that it is looking at a person.

It only sees groups of pixels that changed between frames.

That explains why one moving person can sometimes create more than one contour.

---

### Filtering is important

Without filtering, small changes create many useless motion areas.

The contour-area limit and morphological processing help make the detector more useful.

---

### One large box is easier to work with

Rather than displaying every tiny motion contour, selecting the largest useful motion area gives Sentinel a simpler result to work with.

It also gives us a foundation for later features such as evidence snapshots and event records.

---

### Testing exposed a real weakness

The first version sometimes produced two or three boxes.

Instead of ignoring that problem, I changed the motion-mask processing to join nearby areas before selecting the main contour.

That reduced the fragmentation of motion areas.

This is a useful part of the development process because the improvement came directly from testing.

---

## 11. Current limitations

The current system has several limitations.

The bounding box represents the largest detected motion area, not necessarily an actual person or vehicle.

If several unrelated things move at the same time, Sentinel may choose only one of them.

The four-region classification is still only approximate.

The detector can also be affected by lighting changes, shadows, camera noise, and objects moving in the background.

Most importantly, Sentinel still does not understand **what** is inside the bounding box.

At this point it can say:

```text
There is a significant moving area here.
```

It cannot yet reliably say:

```text
A person is here.
```

That will require object-detection techniques later.

---

## 12. Day 7 result

By the end of Day 7, Sentinel could:

* compare consecutive camera frames
* create a motion mask
* remove small isolated noise
* detect connected motion areas
* filter out very small motion areas
* merge nearby motion areas
* select the largest useful motion area
* draw a bounding box around that area
* estimate the approximate camera region
* continue using the Day 5 event start/end logic

The updated pipeline is:

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
Morphological Cleanup
   ↓
Contour Detection
   ↓
Largest Useful Motion Area
   ↓
Bounding Box
   ↓
Approximate Region
   ↓
Event State
```

---

## 13. Current status

**Day 7 technical work:** COMPLETE

**Motion mask:** WORKING

**Contour detection:** WORKING

**Motion-area filtering:** WORKING

**Nearby-motion merging**
