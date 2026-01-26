# Lab 1 — Square Driver Program

**Team Members:**  
- Jaiden Medina  
- Brady Adams  

---

## Overview
This lab focused on developing a square driver program for the Romi robot. The objective was to make the robot drive in a 2×2 square using an open-loop control strategy and to evaluate the accuracy of the final motion.

---

## Approaches Attempted

### 1. Equal Motor Speeds
Our initial approach set both motors to identical speeds.

**Result:**  
Although the robot moved successfully, it consistently veered left. This revealed hardware variation between motors (torque/speed mismatch). The robot did not produce straight paths, so this approach was not sufficient.

---

### 2. Independent Motor Trimming
We then tried adjusting (trimming) each motor’s speed independently after setting a base speed.

**Result:**  
This reduced the veering effect but caused inconsistent corrections. The robot followed a zig-zag pattern rather than a straight line, which prevented accurate square traversal.

---

### 3. Motor Speed Scaling (Final Approach)
The final solution scaled the right motor speed relative to the left motor.  
We applied a scaling factor of:

**Result:**  
This approach produced straight-line motion and consistent turning. For turns, the motors were driven at equal and opposite speeds (e.g., +105 and −105), allowing near 90° pivot turns. This method successfully allowed the robot to complete a 2×2 square.

---

## Final Program Behavior

- Straight segments:  
  Motors accelerated to a speed of **155**, then decelerated back to zero.

- Turns:  
  Left motor = **105**, Right motor = **−105**

The system operated using **open-loop control**, meaning no sensors were used for correction.

---

## Accuracy Evaluation

| Side | Measured Length (cm) | Length Error (cm) | Measured Angle (°) | Angle Error (°) |
|------|----------------------|-------------------|--------------------|-----------------|
| 1    | TBD                  | TBD               | TBD                | TBD             |
| 2    | TBD                  | TBD               | TBD                | TBD             |
| 3    | TBD                  | TBD               | TBD                | TBD             |
| 4    | TBD                  | TBD               | TBD                | TBD             |
| Average    | TBD                  | TBD               | TBD                | TBD             |                 

---

## Possible Sources of Error

- Manufacturing variation between motors  
- Wheel traction differences  
- Uneven floor surface  
- Measurement inaccuracies when marking the square  
- Robot starting misalignment  
- Battery voltage drop during operation  
- Open-loop control (no feedback correction)

---

## Demonstration Video

Narrated robot run:  
**[Insert video link here]**
