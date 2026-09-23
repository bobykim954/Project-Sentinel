# Project Sentinel — Day 3

## Day 3: Frame Inspection and Brightness Analysis

**Date:** 23 September 2026

### Objective

The goal of Day 3 was to move Project Sentinel beyond simply displaying a live camera feed.

Sentinel needed to begin **inspecting individual video frames** and extracting measurable information from them.

### What Was Built

The camera stream was processed frame by frame using OpenCV.

Sentinel was taught to inspect:

* Frame width
* Frame height
* Number of color channels
* Average brightness of the entire frame

The camera produced frames at:

* **Width:** 640 pixels
* **Height:** 480 pixels
* **Channels:** 3 (BGR)

Each frame therefore contains:

**640 × 480 = 307,200 pixels**

With three color channels, each frame contains:

**307,200 × 3 = 921,600 channel values**

### Frame Inspection

OpenCV represents a frame as an array.

The frame dimensions were obtained using:

```python
height, width, channels = frame.shape
```

The project also uses a frame counter so that diagnostic information is printed every 30 frames instead of flooding the terminal.

```python
frame_count = frame_count + 1

if frame_count % 30 == 0:
```

### Brightness Analysis

Sentinel calculates the average brightness of the complete frame using:

```python
brightness = frame.mean()
```

This converts the visual information in the frame into a numerical measurement.

### Test Results

A normal camera scene produced average brightness values around:

**109–111**

When the webcam lens was covered, brightness dropped to approximately:

**12**

After uncovering the camera, brightness increased again:

**97 → 110**

This demonstrated that Sentinel can detect a significant change in the visual environment through numerical frame analysis.

### What Was Learned

Day 3 established several important computer-vision concepts:

1. A video stream is a continuous sequence of individual frames.
2. Each frame is represented as numerical data.
3. OpenCV uses BGR channel ordering for standard color images.
4. `frame.shape` provides the dimensions and channel count.
5. Individual pixels can be accessed from the frame array.
6. `frame.mean()` can be used to calculate average brightness.
7. A physical environmental change can be converted into measurable numerical data.

### Sentinel Progress

Day 2 allowed Sentinel to **receive and display camera data**.

Day 3 allowed Sentinel to **inspect and measure camera data**.

This is an important transition toward the eventual Sentinel intelligence pipeline:

**Camera → Frames → Measurements → Scene Analysis → Detection → Intelligence → Alerts**

### Status

**Day 3 technical objective: COMPLETE ✅**

The frame inspection and brightness analysis tests passed successfully.

### Next Direction

The next stage will move from simple brightness measurement toward detecting **changes in the scene**.

This will begin the foundation for more meaningful computer-vision tasks such as:

* Motion/change detection
* Object detection
* Activity analysis
* Anomaly detection

Day 3 establishes the foundation required for Sentinel to start understanding what is happening inside a video stream rather than merely displaying it.
