# Project Sentinel — Day 14

## Person Detection

**Date:** 4 October 2026
**Project:** Project Sentinel
**Stage:** Day 14

---

## 1. Why I started person detection

Up to Day 13, Sentinel was mainly working with motion.

It could detect:

* movement
* event start and end
* approximate location
* motion area
* event metadata
* evidence
* event history
* analytics
* event priority

But there was still a major limitation.

Sentinel knew that something moved, but it did not know whether the movement came from a person, vehicle, bag, shadow, or something else.

For Day 14, I started the first object-detection stage.

The initial target was simple:

> **Detect people in the camera view.**

---

## 2. First detector attempt

The first attempt used OpenCV's older HOG pedestrian detector.

However, the installed OpenCV version in the project is OpenCV 5, and the expected HOG API was not available in the current environment.

The first test failed with:

```text
AttributeError: module 'cv2' has no attribute 'HOGDescriptor'
```

Instead of forcing an outdated approach into the project, I changed direction.

I moved to a YOLO ONNX model running through OpenCV's DNN module.

---

## 3. Adding the YOLO model

The project now contains:

```text
models/
└── yolo26n.onnx
```
