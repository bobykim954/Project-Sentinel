# Project Sentinel — Day 10

## Event Metadata and Camera Identification

**Date:** 2 October 2026
**Project:** Project Sentinel
**Stage:** Day 10

---

## 1. What I wanted to improve

By Day 9, Sentinel could detect an event, save an evidence image, and keep a history of the event.

However, the event record was still missing some information that will become important once Sentinel starts working with more than one camera.

The current system eventually needs to answer questions such as:

> Which camera saw this event?

and:

> Where exactly was the detected motion inside the camera frame?

So on Day 10, I extended the event record to include camera information and the coordinates of the detected bounding box.

---

## 2. New event information

The event history now contains:

```text
event_id
camera_id
start_time
end_time
region
motion_area
bbox_x
bbox_y
bbox_width
bbox_height
evidence_path
duration_seconds
```

The new fields are mainly:

```text
camera_id
bbox_x
bbox_y
bbox_width
bbox_height
evidence_path
```

This gives each event more context.

For example:

```text
Camera: CAM-01
Region: BOTTOM LEFT
Bounding box:
x = 17
y = 242
width = 57
height = 90
```

---

## 3. Preparing for multiple cameras

For now, the webcam is identified as:

```python
CAMERA_ID = "CAM-01"
```

This is not because Sentinel has only one camera permanently
