# Lab 6 – Camera Mount Design (Frictionless Design)

## Overview
In this lab, I designed and implemented a custom camera mount for the Romi 32U4 robot to support vision-based navigation using a Raspberry Pi Camera V2.1. The mount was created using Fusion 360 and fabricated for integration with the robot platform.

This lab focuses on mechanical design, system integration, and ensuring reliable camera positioning for future computer vision tasks such as ARUCO marker detection.

---

## Objective
- Design a mount to securely attach a Raspberry Pi Camera V2.1 to the Romi robot  
- Ensure proper camera positioning for computer vision applications  
- Integrate the mount within the physical and spatial constraints of the robot  
- Develop a clean and efficient mechanical design using CAD tools  

---

## Design & Implementation

### CAD Design (Fusion 360)

<p align="center">
  <img src="assets/lab6-CAD/lab6-CAD-front.png" width="300"/>
  <img src="assets/lab6-CAD/lab6-CAD-side.png" width="300"/>
  <img src="assets/lab6-CAD/lab6-CAD-top.png" width="300"/>
</p>

---

### Final Implementation (Real Robot)

<p align="center">
  <img src="assets/lab6-Real/lab6-front.jpg" width="300"/>
  <img src="assets/lab6-Real/lab6-side.jpg" width="300"/>
  <img src="assets/lab6-Real/lab6-top.jpg" width="300"/>
</p>

---

## System Integration
The final design supports integration between:

- Mechanical system (camera mount + chassis)  
- Embedded system (Raspberry Pi)  
- Vision system (camera sensor)  

This enables future implementation of vision-based navigation and perception tasks.

---

## Results
- Successfully designed and mounted a camera system on the Romi robot  
- Achieved proper alignment and positioning for vision applications  
- Maintained structural integrity within robot constraints  
- Enabled future expansion into computer vision and autonomous behavior  

---

## What I Learned
- How to design mechanical components under real-world constraints  
- The importance of spatial alignment in robotics systems  
- How hardware design directly impacts sensing and perception  
- Integration of CAD design with embedded systems  

---

## Future Improvements
- Add adjustable camera angle for tuning field of view  
- Reduce material usage to optimize weight  
- Improve cable management for cleaner integration  
- Add vibration damping for more stable image capture  

---

## Repository Context
This lab is part of a larger Romi autonomous vehicle project, combining embedded systems, control, and hardware design to build a fully integrated robotics platform.
