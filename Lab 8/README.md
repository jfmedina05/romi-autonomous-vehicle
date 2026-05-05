# Lab 7 – Drive-by-Video Camera Driver

## Overview

In this lab, I expanded the Romi autonomous vehicle system by adding a video-based driving interface. The goal was to allow the robot to be driven from a laptop using only the live camera feed transmitted from the Raspberry Pi mounted on the robot.

This lab builds directly on the previous system components:

- Lab 5 curses-based manual/autonomous driver
- Lab 6 Raspberry Pi camera mount
- Raspberry Pi camera capture and processing
- Redis-based frame transmission
- Laptop-side OpenCV video display

The completed system allows an operator to drive the Romi through the curses interface while viewing live video from the robot’s onboard camera. The lab required video capture on the Pi, frame sharing through Redis, and local display on the laptop without relying on X Server forwarding.

---

## Objective

- Integrate the mounted Raspberry Pi Camera V2.1 into the Romi driving system
- Capture camera frames on the Raspberry Pi using `picamera2` and OpenCV
- Transmit video frames through an onboard Redis server
- Display video locally on a laptop using a Python/OpenCV client
- Drive the robot manually through video feedback and the curses interface
- Evaluate frame rate performance at multiple video resolutions

---

## System Architecture

The Lab 7 system is split across three platforms:

### 1. Romi Arduino

The Romi Arduino controls the robot’s physical motion. It receives driving commands from the Python driver and executes motor behavior, including manual driving and autonomous mode transitions.

**Responsibilities:**

- Motor control
- Line sensor interaction
- Manual driving commands
- Autonomous mode support

---

### 2. Raspberry Pi

The Raspberry Pi acts as the robot’s onboard vision and communication computer. It captures video from the mounted Pi Camera, preprocesses frames using OpenCV, and publishes them through Redis.

**Responsibilities:**

- Camera capture using `picamera2`
- Frame preprocessing using OpenCV
- Redis server hosting
- Frame transmission to the operator laptop

---

### 3. Laptop / Operator Station

The laptop acts as the remote control and display station. It runs the curses interface for driving and a Python video client that reads frames from Redis and displays them locally using OpenCV.

**Responsibilities:**

- Curses-based driving interface
- Redis frame retrieval
- OpenCV video display
- Manual driving through camera feedback

---

## Data Flow

```text
Pi Camera
   ↓
Raspberry Pi Camera Capture
   ↓
OpenCV Frame Processing
   ↓
Redis Server on Pi
   ↓
Laptop Python Client
   ↓
OpenCV Video Display
   ↓
Operator Drives Robot with Curses Interface
```

---

## Repository Structure

```text
Lab 7/
├── Camera Function/
│   ├── client.py
│   └── server1.py
│
├── Movement & UI Programs/
│   ├── Project_driver.py
│   ├── a_star.py
│   └── ui.py
│
└── README.md
```

---

## Folder Descriptions

| Folder/File | Description |
|---|---|
| `Camera Function/` | Camera streaming and Redis client/server programs |
| `Movement & UI Programs/` | Manual driving, UI control, and robot movement logic |
| `README.md` | Lab documentation and system overview |

---

## Key Features

- Remote driving through live robot camera feed
- Redis-based image transmission from Raspberry Pi to laptop
- OpenCV display of live video frames
- Curses interface integration for operator control
- System distributed across Arduino, Raspberry Pi, and laptop
- Foundation for future ArUco marker detection and autonomous road-sign behavior

---

## Video Performance Testing

The lab required testing three camera resolutions and comparing frame rate performance.

| Resolution | Purpose | Expected Tradeoff |
|---|---|---|
| 640 × 480 | Highest image detail | Lower frame rate, more processing load |
| 320 × 240 | Balanced quality and speed | Good compromise for driving |
| 160 × 120 | Fastest video response | Lower detail, better responsiveness |

---

## Recommendation

A medium resolution such as `320 × 240` is often the best practical choice for this system because it balances frame rate, visibility, and responsiveness. It provides enough visual information for the operator while reducing the processing and transmission load compared to `640 × 480`.

---

## What I Learned

- How to distribute a robotics system across multiple computing platforms
- How to stream camera data from a Raspberry Pi using Redis
- How OpenCV can be used for real-time video display
- How video resolution affects latency and frame rate
- How interface design affects operator control in robotic systems

---

## Future Improvements

- Add compression to improve video transmission performance
- Add frame timestamps to measure latency
- Improve synchronization between video feedback and control commands
- Integrate ArUco marker detection directly into the video pipeline
- Add screenshots or demo video thumbnails to the README

---

## Repository Context

This lab is part of a larger Romi Autonomous Vehicle project. It provides the video interface needed for the final system, where the robot follows a line and responds to visual ArUco road signs.
