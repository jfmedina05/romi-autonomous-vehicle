# Romi Autonomous Vehicle

An embedded robotics system built on the Pololu Romi 32U4 platform, focused on autonomous navigation, closed-loop control, and hardware–software integration. This project documents the development of a mobile robot capable of reliable motion, system-level coordination, and extensibility toward vision-based autonomy.

---

## Overview
This project explores the design and implementation of a mobile robot capable of both manual and autonomous operation. The system integrates motor control, encoder feedback, state-machine-based behavior, and hardware design to achieve accurate and repeatable movement in real-world conditions.

Across multiple development stages, the project evolves from basic motion control to a fully integrated robotics platform combining embedded systems, control theory, and mechanical design.

---

## Project Goals
- Develop a robot capable of controlled autonomous movement  
- Implement manual and programmatic control modes  
- Use encoder feedback for closed-loop motor control  
- Build reliable motion behaviors using state machines  
- Integrate mechanical, electrical, and software subsystems  

---

## Hardware / Platform
- Pololu Romi 32U4 Robot  
- DC Motors with Encoders  
- Raspberry Pi (for extended capabilities)  
- Pi Camera V2.1 (Lab 6 integration)  
- Arduino-compatible embedded development environment  

---

## Key Features
- Closed-loop wheel speed control using encoder feedback  
- State-machine-driven autonomous behavior  
- Motion calibration for distance and turning accuracy  
- Manual and autonomous control modes  
- Mechanical system design for sensor integration (camera mount)  

---

## Featured Work

### Closed-Loop Motion Control
- Implemented encoder-based feedback for precise wheel speed control  
- Improved motion accuracy and repeatability compared to open-loop systems  

---

### Autonomous Navigation & State Machines
- Designed structured state-machine logic for predictable robot behavior  
- Enabled controlled movement sequences such as square-path navigation  

---

### Camera Mount Design (Lab 6 – Frictionless Design)
- Designed a custom camera mount using Fusion 360 for a Raspberry Pi Camera V2.1  
- Ensured camera alignment along the robot centerline and within physical constraints  
- Implemented a **frictionless design** for clean mechanical integration and stability  
- Enabled future vision-based navigation using ARUCO marker detection  

---

## Repository Structure
- `Lab 1/` – Initial setup and basic square driver  
- `Lab 2/` – Closed-loop control with encoder feedback  
- `Lab 3/ – Lab 5/` – Progressive control, calibration, and autonomy  
- `Lab 6/` – Camera mount design and system integration  
- `README.md` – Project overview and documentation  

---

## Technical Concepts Demonstrated
- Embedded systems programming (C/C++)  
- Closed-loop control systems  
- State-machine architecture  
- Robotics motion control and calibration  
- Hardware–software co-design  
- Mechanical design using CAD (Fusion 360)  

---

## What I Learned
- Transitioning from open-loop to closed-loop control systems  
- How feedback systems improve reliability in physical systems  
- Designing structured, scalable behavior using state machines  
- The importance of calibration in real-world robotics  
- Integrating mechanical design with embedded systems  

---

## Future Improvements
- Add line-following or vision-based navigation  
- Integrate real-time camera processing using Raspberry Pi  
- Improve trajectory control and path accuracy  
- Add obstacle detection and sensor fusion  
- Develop a fully autonomous navigation pipeline  

---

## Why This Project Matters
This project represents a complete embedded robotics system where software, hardware, and mechanical design intersect. It demonstrates the ability to design, build, and integrate real-world systems under constraints—skills directly applicable to robotics, embedded systems, and intelligent device development.
