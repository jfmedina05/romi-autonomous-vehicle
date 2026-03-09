# Lab 4 – PID Line Following Robot

## Course
**ENGR-E 321 – Advanced Cyber-Physical Systems**

## Team Members
- Jaiden Medina  
- Brady Adams  

---

# Project Overview

This project implements a **PID-based line following controller** on the **Romi 32U4 robot**. The robot uses a **QTR reflectance sensor array** to detect the position of a black line on the track and adjusts the motor speeds to remain centered on the line.

The goal of this lab was to:

- Implement a **PID control loop**
- Tune **P, PD, and PID controllers**
- Log controller performance data
- Graph **error vs time**
- Determine the **fastest reliable line following strategy**

---

# Hardware

## Robot Platform
- Romi 32U4 Robot

## Sensors
- Pololu QTR Reflectance Sensor Array (6 sensors used)

## Actuators
- Romi DC Motors

## Additional Components
- LCD Display  
- Buzzer  
- Button A  

---

# Software Architecture

The robot operates in three main states:

```
WAIT_CALIBRATE
WAIT_START
RUNNING
```

### WAIT_CALIBRATE
The robot waits for the user to press **Button A** to begin sensor calibration.

### WAIT_START
After calibration, the robot waits to be placed on the track and started.

### RUNNING
The PID controller runs continuously and the robot actively follows the line.

---

# PID Control Loop

The control loop performs the following steps:

```
1. Read line position from the sensor array
2. Compute tracking error relative to the center of the robot
3. Calculate P, I, and D terms
4. Compute the correction value
5. Adjust left and right motor speeds
6. Log error and motor speeds
```

---

# PID Gains

The tuned controller gains used in the final implementation were:

```
Kp = 0.04
Ki = 0.0005
Kd = 0.02
```

The controller output is calculated as:

```
correction = P + I + D
```

Motor commands are calculated using differential steering:

```
leftSpeed  = baseSpeed - correction
rightSpeed = baseSpeed + correction
```

This causes the robot to steer back toward the center of the line.

---

# Controller Experiments

Three controller configurations were tested.

---

## P Controller

Configuration:

```
Kp > 0
Ki = 0
Kd = 0
```

Characteristics:

- Fast response
- Large oscillations
- Overshoot during turns

---

## PD Controller

Configuration:

```
Kp > 0
Ki = 0
Kd > 0
```

Characteristics:

- Reduced oscillation
- Faster stabilization
- Improved turning performance

---

## PID Controller

Configuration:

```
Kp > 0
Ki > 0
Kd > 0
```

Characteristics:

- More accurate tracking
- Corrects steady-state error
- Slightly slower response during sharp turns

---

# Error vs Time Graphs

The robot logged the following data during each run:

- Time
- Tracking error
- Left motor speed
- Right motor speed

This data was exported and plotted to evaluate controller performance.

---

## P Controller — Error vs Time

![P Controller Error vs Time](Images/p_controller_error_vs_time.png)

Discussion:

The P controller responds quickly to changes in error but tends to overshoot the line during turns. This causes oscillations around the line before stabilizing.

---

## PD Controller — Error vs Time

![PD Controller Error vs Time](Images/pd_controller_error_vs_time.png)

Discussion:

The PD controller reduces oscillation by reacting to the rate of change of the error. This allows the robot to stabilize more quickly after encountering a disturbance such as a turn.

---

## PID Controller — Error vs Time

![PID Controller Error vs Time](Images/pid_controller_error_vs_time.png)

Discussion:

The PID controller improves overall accuracy by correcting accumulated error. However, the integral component can sometimes slow the system response during large disturbances.

---

# Results

From the experimental data and observations:

- The **P controller** reacted quickly but produced significant oscillations.
- The **PD controller** reduced oscillations and improved stability.
- The **PID controller** improved steady-state accuracy but sometimes slowed response during sharp turns.

The **PD controller produced the fastest reliable line-following performance**.

---

# Videos

## P Controller Demonstration

Add your video link here:

```
[Insert P Controller Video Link]
```

---

## PD Controller Demonstration

Add your video link here:

```
[Insert PD Controller Video Link]
```

---

## PID Controller Demonstration

Add your video link here:

```
[Insert PID Controller Video Link]
```

---

# Running the Robot

1. Upload the Arduino code to the Romi robot.
2. Press **Button A** to start sensor calibration.
3. Move the robot across the line during calibration.
4. Place the robot on the track.
5. Press **Button A** to start line following.
6. Press **Button A** again to stop and print the logged data.

---

# Repository Structure

```
Lab4/
│
├── Code/
│   └── line_follower.ino
│
├── Data/
│   ├── P_controller_data.csv
│   ├── PD_controller_data.csv
│   └── PID_controller_data.csv
│
├── Images/
│   ├── p_controller_error.png
│   ├── pd_controller_error.png
│   └── pid_controller_error.png
│
├── Videos/
│   ├── p_controller_demo.mp4
│   ├── pd_controller_demo.mp4
│   └── pid_controller_demo.mp4
│
└── Report/
    └── Lab4_Report.pdf
```

---

# Relationship to Lab 3

In **Lab 3**, the QTR line sensor array was installed and tested to measure the position of the line relative to the robot. The sensor system reports how far the detected line is from the center of the sensor array.

In **Lab 4**, that measurement becomes the **feedback signal for the PID controller**. The robot continuously reads the line position, computes an error relative to the center of the track, and adjusts motor speeds accordingly. By combining the sensing system from Lab 3 with the feedback controller developed in this lab, the robot can dynamically correct its motion and maintain stable tracking of the line.

---

# Conclusion

This lab demonstrated how PID controllers can significantly improve the performance of a line-following robot.

Key findings:

- **P Controller:** fast but unstable  
- **PD Controller:** faster and more stable, but less accurate over time  
- **PID Controller:** accurate but slower response during sharp changes  

Ultimately, the **PD controller provided the fastest reliable line-following performance**.
