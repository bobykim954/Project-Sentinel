# Project Sentinel — Day 2

**Date:** 22 September 2026
**Focus:** Live Camera Input Foundation

## Objective

The objective for Day 2 was to establish the first video-input layer of Project Sentinel by confirming that Python and OpenCV could successfully access a camera and process a live video stream.

## Environment Verification

The development environment was verified before beginning the camera test.

* **Python:** 3.14.7
* **OpenCV:** Installed and available inside the Sentinel virtual environment
* **NumPy:** Installed as an OpenCV dependency
* **Virtual environment:** `.venv`
* **Development environment:** Visual Studio Code

## Implementation

A Python program was created in:

```text
src/main.py
```

The program uses OpenCV's `VideoCapture()` interface to access the computer's camera, continuously read video frames, and display the live stream.

The program also includes basic checks to determine whether the camera can be opened and whether individual frames can be successfully read.

## Test Result

The camera test was executed successfully.

### Result

**PASS — Live camera stream successfully displayed.**

Sentinel was able to:

1. Access the camera.
2. Receive video frames.
3. Display the frames in real time.
4. Maintain the live stream until the user exited the program.

## Technical Significance

This test establishes the first working layer of Sentinel's computer-vision pipeline.

Current development pipeline:

```text
Camera
   ↓
OpenCV
   ↓
Frame Acquisition
   ↓
Sentinel Application
   ↓
Live Video Display
```

The computer webcam was used as the initial video source for testing. This is a development substitute for the existing Hikvision CCTV infrastructure.

The eventual production-oriented pipeline is expected to introduce a suitable capture or digital video interface between the analog CCTV cameras and Sentinel.

```text
Hikvision CCTV
      ↓
Video Signal
      ↓
Capture/DVR Interface
      ↓
Digital Video Stream
      ↓
Sentinel
      ↓
AI / Computer Vision
      ↓
Alerts & Analytics
```

## Key Learning

A surveillance AI system must first be capable of reliably receiving video before it can perform detection, tracking, anomaly analysis, or other intelligent operations.

Today's test therefore establishes the basic **video ingestion capability** required for later Sentinel components.

## Day 2 Milestone

**Milestone achieved: Live Camera Input**

Project Sentinel successfully acquired and displayed a real-time camera feed using Python and OpenCV.

**Status: COMPLETE ✅**
