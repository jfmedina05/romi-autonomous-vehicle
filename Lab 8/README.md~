# Lab 8 – ArUco Road Sign Detection & Autonomous Behavior

## Overview

In this lab, I expanded the Romi autonomous vehicle system by integrating ArUco marker detection into the robot’s video and control pipeline. This builds on Lab 7’s drive-by-video system and moves the robot closer to the final project goal: a line-following robot that can respond to visual “road signs.”

The system uses ArUco markers as visual commands that trigger different robot behaviors, allowing the robot to operate more autonomously without direct operator input.

---

## Objective

- Add ArUco marker detection to the Romi vision system
- Detect visual road signs using the robot-mounted camera
- Identify marker IDs and associate them with robot behavior
- Support autonomous response to stop, high-speed, and low-speed signs
- Integrate vision, control, and motion into a unified system

---

## System Architecture

The Lab 8 system integrates perception, control, and motion across three platforms:

### 1. Romi Arduino

The Arduino controls the robot’s physical behavior, including motor control, line following, and execution of commands triggered by detected markers.

**Responsibilities:**

- Motor control
- Line-following logic
- Manual and autonomous mode support
- Speed adjustments and stop behavior

---

### 2. Raspberry Pi

The Raspberry Pi handles vision processing and communication. It captures frames from the camera, detects ArUco markers, and processes the results for use by the system.

**Responsibilities:**

- Camera capture using Pi Camera
- ArUco marker detection using OpenCV
- Frame processing and annotation
- Communication with the laptop system

---

### 3. Laptop / Operator Station

The laptop displays the live video feed and runs the curses interface, allowing the operator to monitor robot behavior and intervene if needed.

**Responsibilities:**

- Display live camera feed
- Show detected markers and IDs
- Provide manual control interface
- Indicate autonomous actions

---

## Road Sign Behavior

The robot responds to detected ArUco markers as follows:

| Marker ID | Action | Behavior |
|---|---|---|
| ID 5 | Stop | Come to a complete stop, then resume movement |
| ID 6 | High Speed | Switch to high-speed line following |
| ID 7 | Low Speed | Switch to low-speed line following |

These behaviors are triggered automatically when the robot detects the corresponding marker.

---

## Data Flow

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
Lab 8/
├── ArUco Detection/
│   └── Server & Client Programs/
│       ├── client.py
│       └── server1.py
│
├── Movement & UI Programs/
│   ├── Arduino Program/
│   │   └── Lab8_E321.ino
│   │
│   └── Driver Program & UI/
│       ├── Project_driver.py
│       ├── a_star.py
│       └── ui.py
│
└── README.md
```

---

## Folder Descriptions

| Folder/File | Description |
|---|---|
| `ArUco Detection/` | Camera streaming, detection, and communication programs |
| `Server & Client Programs/` | Handles video transmission and processing |
| `Movement & UI Programs/` | Robot control logic and user interface |
| `Arduino Program/` | Embedded code for robot behavior |
| `Driver Program & UI/` | Python control and UI interface |
| `README.md` | Lab documentation and system overview |

---

## Key Features

- Real-time ArUco marker detection using OpenCV
- Autonomous behavior triggered by visual inputs
- Integration with existing video streaming system
- Manual override capability through curses interface
- Multi-platform robotics system: Arduino, Raspberry Pi, and laptop

---

## What I Learned

- How to integrate computer vision into a robotics system
- How visual data can directly control robot behavior
- How to use ArUco markers for reliable object detection
- How to connect perception, decision-making, and motion
- How to design a distributed robotics architecture

---

## Future Improvements

- Improve detection accuracy under varying lighting conditions
- Add filtering to prevent repeated marker triggers
- Introduce detection confidence thresholds
- Add visual overlays highlighting detected markers
- Improve transition logic between different robot states

---

## Repository Context

This lab is part of the Romi Autonomous Vehicle project and represents the transition from remote-controlled driving to perception-driven autonomous behavior. It enables the robot to interpret visual signals and respond intelligently in real time.
