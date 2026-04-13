# Romi Autonomous Vehicle

An embedded robotics project built around the Pololu Romi 32U4 platform, focused on autonomous navigation, manual control, closed-loop motion control, and state-machine-based behavior. This repository documents the progression of a semester-long robotics and embedded systems project.

## Overview
This project explores the design and implementation of a mobile robot capable of controlled movement through both programmed autonomy and user-directed operation. The work includes motor control, encoder feedback, turning calibration, state-machine logic, and closed-loop wheel-speed control.

## Project Goals
- Develop a mobile robot capable of autonomous movement
- Implement manual and programmed motion modes
- Use encoder feedback for closed-loop wheel-speed control
- Build reliable motion behaviors using embedded C/C++ and state machines

## Hardware / Platform
- Pololu Romi 32U4 robot
- Encoders
- DC motors
- Buttons and onboard hardware interfaces
- Arduino-compatible embedded development environment

## Key Features
- Closed-loop wheel speed control using encoder feedback
- Square-path driving behavior
- State-machine-driven motion sequencing
- Distance and turning calibration
- Manual and autonomous robot control workflows

## Repository Structure
- `Lab 1/` – GitHub setup and initial square driver program
- `Lab 2/` – closed-loop square driver with wheel-speed control
- `Lab 3/`, `Lab 4/`, `Lab 5/` – continued robotics and control development
- `README.md` – overall repository summary

## Technical Concepts Demonstrated
- Embedded programming
- Robotics control
- State machines
- PID / feedback-based control
- Motion calibration
- Sensor-informed autonomy

## What I Learned
- How to move from open-loop behavior to closed-loop control
- How encoder feedback improves motion reliability
- How to structure robotics behavior with state machines
- How calibration affects real-world autonomous motion performance

## Future Improvements
- Add obstacle detection or line-following behavior
- Improve path accuracy and turning consistency
- Add better documentation for each lab milestone
- Include wiring, architecture, and control diagrams
- Create a final integrated autonomous demo

## Why This Project Matters
This project represents hands-on embedded systems and robotics development, where software decisions directly affect physical system behavior. It strengthened my interest in control, autonomy, and intelligent embedded systems operating in real environments.
