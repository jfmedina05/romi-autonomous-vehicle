# Romi Autonomous Vehicle

An embedded robotics system built on the Pololu Romi 32U4 platform, focused on autonomous navigation, closed-loop control, hardware–software integration, and vision-based robot behavior. This project documents the development of a mobile robot capable of reliable motion, system-level coordination, video-based driving, and autonomous responses to visual road signs.

---

## Overview

This project explores the design and implementation of a mobile robot capable of both manual and autonomous operation. The system integrates motor control, encoder feedback, state-machine-based behavior, hardware design, Raspberry Pi camera streaming, OpenCV vision processing, Redis-based communication, and ArUco marker detection.

Across multiple development stages, the project evolves from basic motion control to a fully integrated robotics platform combining embedded systems, control theory, mechanical design, computer vision, and distributed system communication.

The final system moves toward a robot that can follow a line, receive operator input through a curses-based interface, stream live video from an onboard camera, and respond to visual road signs using ArUco markers.

---

## Project Goals

- Develop a robot capable of controlled autonomous movement
- Implement manual and programmatic control modes
- Use encoder feedback for closed-loop motor control
- Build reliable motion behaviors using state machines
- Integrate mechanical, electrical, and software subsystems
- Add live video feedback for remote robot operation
- Use computer vision to detect visual road signs
- Trigger autonomous robot behavior from detected ArUco markers

---

## Hardware / Platform

- Pololu Romi 32U4 Robot
- DC Motors with Encoders
- Raspberry Pi
- Raspberry Pi Camera V2.1
- Laptop / Operator Station
- Arduino-compatible embedded development environment
- Redis server for frame transmission
- OpenCV for video display and ArUco marker detection

---

## Key Features

- Closed-loop wheel speed control using encoder feedback
- State-machine-driven autonomous behavior
- Motion calibration for distance and turning accuracy
- Manual and autonomous control modes
- Mechanical system design for sensor integration
- Raspberry Pi Camera V2.1 mount integration
- Live robot camera feed for remote driving
- Redis-based image transmission from Raspberry Pi to laptop
- OpenCV display of live video frames
- Curses interface integration for operator control
- Real-time ArUco marker detection using OpenCV
- Autonomous behavior triggered by visual inputs
- Multi-platform robotics system using Arduino, Raspberry Pi, and laptop

---

## System Architecture

The system is distributed across three main platforms:

### 1. Romi Arduino

The Romi Arduino controls the robot’s physical motion and embedded behavior.

**Responsibilities:**

- Motor control
- Encoder feedback
- Line sensor interaction
- Line-following logic
- Manual driving commands
- Autonomous mode support
- Speed adjustments and stop behavior

---

### 2. Raspberry Pi

The Raspberry Pi acts as the onboard vision and communication computer.

**Responsibilities:**

- Camera capture using Raspberry Pi Camera V2.1
- Frame preprocessing using OpenCV
- Redis server hosting
- Frame transmission to the operator laptop
- ArUco marker detection
- Marker ID identification
- Frame annotation and communication

---

### 3. Laptop / Operator Station

The laptop acts as the remote control, display, and monitoring station.

**Responsibilities:**

- Curses-based driving interface
- Redis frame retrieval
- OpenCV video display
- Manual driving through camera feedback
- Display of detected ArUco markers and IDs
- Operator override and monitoring

---

## Labs and Documentation

| Lab | Focus |
|---|---|
| [Lab 1 — Initial Setup and Basic Square Driver](./Lab%201) | Initial setup, basic movement, and square-path driving |
| [Lab 2 — Closed-Loop Control](./Lab%202) | Encoder feedback and closed-loop motion control |
| [Lab 3 — Control Development](./Lab%203) | Continued control, calibration, and movement development |
| [Lab 4 — Motion Calibration](./Lab%204) | Progressive robot movement, calibration, and control refinement |
| [Lab 5 — Curses-Based Manual and Autonomous Driver](./Lab%205) | Manual/autonomous driving interface, telemetry, PID tuning, and logging |
| [Lab 6 — Camera Mount Design](./Lab%206) | Fusion 360 Raspberry Pi Camera V2.1 mount and hardware integration |
| [Lab 7 — Drive-by-Video Camera Driver](./Lab%207) | Raspberry Pi camera streaming, Redis frame transfer, OpenCV display, and laptop-side driving |
| [Lab 8 — ArUco Road Sign Detection](./Lab%208) | ArUco marker detection and autonomous robot behavior from visual signs |

---

## Featured Work

### Closed-Loop Motion Control

- Implemented encoder-based feedback for precise wheel speed control
- Improved motion accuracy and repeatability compared to open-loop systems
- Used feedback data to support more reliable real-world robot movement

---

### Autonomous Navigation & State Machines

- Designed structured state-machine logic for predictable robot behavior
- Enabled controlled movement sequences such as square-path navigation
- Built a foundation for more advanced autonomous robot decision-making

---

### Camera Mount Design  
#### [Lab 6 — Frictionless Design](./Lab%206)

- Designed a custom camera mount using Fusion 360 for a Raspberry Pi Camera V2.1
- Ensured camera alignment along the robot centerline and within physical constraints
- Implemented a **frictionless design** for clean mechanical integration and stability
- Enabled future vision-based navigation using ArUco marker detection

---

### Drive-by-Video Camera Driver  
#### [Lab 7](./Lab%207)

In [Lab 7](./Lab%207), I expanded the Romi autonomous vehicle system by adding a video-based driving interface. The goal was to allow the robot to be driven from a laptop using only the live camera feed transmitted from the Raspberry Pi mounted on the robot.

This lab built directly on previous system components:

- [Lab 5](./Lab%205) curses-based manual/autonomous driver
- [Lab 6](./Lab%206) Raspberry Pi camera mount
- Raspberry Pi camera capture and processing
- Redis-based frame transmission
- Laptop-side OpenCV video display

The completed system allows an operator to drive the Romi through the curses interface while viewing live video from the robot’s onboard camera. The lab required video capture on the Pi, frame sharing through Redis, and local display on the laptop without relying on X Server forwarding.

**Lab 7 Objectives:**

- Integrate the mounted Raspberry Pi Camera V2.1 into the Romi driving system
- Capture camera frames on the Raspberry Pi using `picamera2` and OpenCV
- Transmit video frames through an onboard Redis server
- Display video locally on a laptop using a Python/OpenCV client
- Drive the robot manually through video feedback and the curses interface
- Evaluate frame rate performance at multiple video resolutions

**Lab 7 Data Flow:**

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

**Video Performance Testing:**

| Resolution | Purpose | Expected Tradeoff |
|---|---|---|
| 640 × 480 | Highest image detail | Lower frame rate, more processing load |
| 320 × 240 | Balanced quality and speed | Good compromise for driving |
| 160 × 120 | Fastest video response | Lower detail, better responsiveness |

**Recommendation:**

A medium resolution such as `320 × 240` is often the best practical choice for this system because it balances frame rate, visibility, and responsiveness. It provides enough visual information for the operator while reducing the processing and transmission load compared to `640 × 480`.

---

### ArUco Road Sign Detection & Autonomous Behavior  
#### [Lab 8](./Lab%208)

In [Lab 8](./Lab%208), I expanded the Romi autonomous vehicle system by integrating ArUco marker detection into the robot’s video and control pipeline. This built on [Lab 7](./Lab%207)’s drive-by-video system and moved the robot closer to the final project goal: a line-following robot that can respond to visual road signs.

The system uses ArUco markers as visual commands that trigger different robot behaviors, allowing the robot to operate more autonomously without direct operator input.

**Lab 8 Objectives:**

- Add ArUco marker detection to the Romi vision system
- Detect visual road signs using the robot-mounted camera
- Identify marker IDs and associate them with robot behavior
- Support autonomous response to stop, high-speed, and low-speed signs
- Integrate vision, control, and motion into a unified system

**Road Sign Behavior:**

| Marker ID | Action | Behavior |
|---|---|---|
| ID 5 | Stop | Come to a complete stop, then resume movement |
| ID 6 | High Speed | Switch to high-speed line following |
| ID 7 | Low Speed | Switch to low-speed line following |

These behaviors are triggered automatically when the robot detects the corresponding marker.

**Lab 8 Data Flow:**

```text
Pi Camera
   ↓
OpenCV Frame Capture
   ↓
ArUco Marker Detection
   ↓
Marker ID Identification
   ↓
Behavior Decision Logic
   ↓
Robot Control Command
   ↓
Romi Motion Execution
```

---

## Repository Structure

```text
Romi Autonomous Vehicle/
├── Lab 1/
│   └── Initial setup and basic square driver
│
├── Lab 2/
│   └── Closed-loop control with encoder feedback
│
├── Lab 3/ - Lab 5/
│   └── Progressive control, calibration, and autonomy
│
├── Lab 6/
│   └── Camera mount design and system integration
│
├── Lab 7/
│   ├── Camera Function/
│   │   ├── client.py
│   │   └── server1.py
│   │
│   ├── Movement & UI Programs/
│   │   ├── Project_driver.py
│   │   ├── a_star.py
│   │   └── ui.py
│   │
│   └── README.md
│
├── Lab 8/
│   ├── ArUco Detection/
│   │   └── Server & Client Programs/
│   │       ├── client.py
│   │       └── server1.py
│   │
│   ├── Movement & UI Programs/
│   │   ├── Arduino Program/
│   │   │   └── Lab8_E321.ino
│   │   │
│   │   └── Driver Program & UI/
│   │       ├── Project_driver.py
│   │       ├── a_star.py
│   │       └── ui.py
│   │
│   └── README.md
└── README.md
```

---

## Folder Descriptions

| Folder/File | Description |
|---|---|
| [Lab 1](./Lab%201) | Initial setup and basic square driver |
| [Lab 2](./Lab%202) | Closed-loop control with encoder feedback |
| [Lab 3](./Lab%203) | Progressive control and calibration development |
| [Lab 4](./Lab%204) | Continued robot control, tuning, and movement development |
| [Lab 5](./Lab%205) | Curses-based manual/autonomous driver, telemetry, PID tuning, and logging |
| [Lab 6](./Lab%206) | Camera mount design and system integration |
| [Lab 7](./Lab%207) | Drive-by-video camera driver and Redis-based video streaming |
| [Lab 7 / Camera Function](./Lab%207/Camera%20Function) | Camera streaming and Redis client/server programs |
| [Lab 7 / Movement & UI Programs](./Lab%207/Movement%20%26%20UI%20Programs) | Manual driving, UI control, and robot movement logic |
| [Lab 8](./Lab%208) | ArUco road sign detection and autonomous behavior integration |
| [Lab 8 / ArUco Detection](./Lab%208/ArUco%20Detection) | Camera streaming, marker detection, and communication programs |
| [Lab 8 / ArUco Detection / Server & Client Programs](./Lab%208/ArUco%20Detection/Server%20%26%20Client%20Programs) | Handles video transmission and processing |
| [Lab 8 / Movement & UI Programs](./Lab%208/Movement%20%26%20UI%20Programs) | Robot control logic and user interface |
| [Lab 8 / Arduino Program](./Lab%208/Movement%20%26%20UI%20Programs/Arduino%20Program) | Embedded code for robot behavior |
| [Lab 8 / Driver Program & UI](./Lab%208/Movement%20%26%20UI%20Programs/Driver%20Program%20%26%20UI) | Python control and UI interface |
| [README.md](./README.md) | Overall project documentation |

---

## Technical Concepts Demonstrated

- Embedded systems programming using C/C++
- Python-based robot control
- Closed-loop control systems
- Encoder feedback and motor calibration
- State-machine architecture
- Robotics motion control
- Hardware–software co-design
- Mechanical design using CAD and Fusion 360
- Raspberry Pi camera integration
- Distributed robotics architecture
- Redis-based image transmission
- OpenCV video display
- ArUco marker detection
- Vision-triggered autonomous behavior
- Manual override through terminal UI design

---

## What I Learned

- Transitioning from open-loop to closed-loop control systems
- How feedback systems improve reliability in physical systems
- Designing structured, scalable behavior using state machines
- The importance of calibration in real-world robotics
- Integrating mechanical design with embedded systems
- How to distribute a robotics system across multiple computing platforms
- How to stream camera data from a Raspberry Pi using Redis
- How OpenCV can be used for real-time video display
- How video resolution affects latency and frame rate
- How to integrate computer vision into a robotics system
- How visual data can directly control robot behavior
- How to use ArUco markers for reliable object detection
- How to connect perception, decision-making, and motion

---

## Future Improvements

- Improve line-following reliability and tuning
- Add compression to improve video transmission performance
- Add frame timestamps to measure latency
- Improve synchronization between video feedback and control commands
- Improve ArUco detection accuracy under varying lighting conditions
- Add filtering to prevent repeated marker triggers
- Introduce detection confidence thresholds
- Add visual overlays highlighting detected markers
- Improve transition logic between different robot states
- Add obstacle detection and sensor fusion
- Develop a fully autonomous navigation pipeline

---

## Why This Project Matters

This project represents a complete embedded robotics system where software, hardware, mechanical design, and computer vision intersect. It demonstrates the ability to design, build, and integrate real-world systems under constraints.

The project began with basic motion control and evolved into a distributed robotics platform capable of live video streaming, operator control, visual perception, and autonomous behavior. These skills are directly applicable to robotics, embedded systems, intelligent devices, autonomous vehicles, and hardware–software integration.
