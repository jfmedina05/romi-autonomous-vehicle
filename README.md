# E321-S26

**Course Repository - Spring 2026**

**Team Members:**
- Jaiden Medina
- Brady Adams

---

## Lab 1 - Github + Romi Robot Setup & Square Driver Program

### Completed Tasks
- [x] Created private IU Github repository: **E321-S26**
- [x] Added required collaborators
- [x] Created `Lab 1` directory & committed Arduino program
- [x] Updated `README.md` file in lab 1 directory with discussion of square driver program

---

## Lab 2 - Closed-Loop Square Driver with Wheel Speed Control

### Completed Tasks
- [x] Implemented closed-loop wheel speed control using encoder feedback
- [x] Developed square-driving state machine
- [x] Implemented PID-based wheel speed controller
- [x] Calibrated encoder distance conversion (`MM_PER_COUNT`)
- [x] Tuned motor scaling factors
- [x] Calibrated 90° turning using encoder tick counts
- [x] Evaluated distance and angular accuracy

### Summary

The Romi robot drives in a **2 ft square path** using a closed-loop wheel speed controller and encoder feedback.

The motion controller operates as a **state machine**:

- **WAIT_START** – Waits for Button A press  
- **DRIVE_SIDE** – Drives forward one side of the square  
- **TURN_90** – Performs an in-place 90° turn  
- **DONE** – Stops after completing all four sides  

Wheel speed control combines:

- Feedforward motor command  
- PID speed correction  
- Slew rate limiting  
- Straightness correction using encoder differences  

Motor imbalance was compensated using:

```cpp
const float LEFT_MOTOR_SCALE  = 1.00;
const float RIGHT_MOTOR_SCALE = 1.12;
```

Distance traveled is calculated from encoder counts using:

```cpp
float MM_PER_COUNT = 0.15625f;
```

Turns are controlled by counting encoder ticks:

```cpp
int TURN_90_COUNTS = 760;
```

### Accuracy Results

Target Side Length = **24 in**

| Side | Measured Length | Error (in) | % Error |
|------|-----------------|------------|---------|
| 1    | 24.0            | 0.0        | 0%      |
| 2    | 25.0            | +1.0       | 4.2%    |
| 3    | 24.5            | +0.5       | 2.1%    |
| 4    | 24.5            | +0.5       | 2.1%    |

Average Side Length = **24.5 in**  
Average Percent Error = **2.1%**

The robot returned close to its starting orientation after completing the square, indicating minimal cumulative angular drift (<5°).

### Demonstration Video

[Lab 2 Demonstration Video](https://indiana-my.sharepoint.com/:v:/g/personal/jfmedina_iu_edu/IQDaAcXq-6zMTbLDtQx9KY89AS88-Z-BiEQzFpZRx7JBHYE)

---

## Lab 3 - Line Sensor Characterization and Accuracy Analysis

### Completed Tasks
- [x] Installed Romi reflectance sensor array
- [x] Implemented calibration using QTRSensors library
- [x] Estimated lateral track line position
- [x] Converted sensor output to displacement measurements
- [x] Evaluated measurement accuracy across multiple line widths
- [x] Determined optimal track width for line-following

### Summary

This lab utilized the Romi reflectance sensor array to estimate the lateral position of a track line relative to the robot’s centerline using six infrared emitter–detector pairs.

Sensor readings were calibrated using the **QTRSensors** library to determine minimum and maximum reflectance values. The function:

```cpp
readLineBlack()
```

was used to compute the position of the detected line via a weighted centroid calculation. The reported value was centered to produce a signed error where:

- **0** → line centered under robot  
- **Positive** → line right of center  
- **Negative** → line left of center  

Sensor accuracy was evaluated by laterally translating the robot in **0.25 in increments** across track lines of varying widths:

- 0.125 in  
- 0.5 in  
- 0.75 in  
- 1.0 in  

Error was calculated as:

```text
Error = Reported Displacement − Actual Displacement
```

### Results

- **0.125 in line:** Largest deviation due to insufficient sensor coverage  
- **1.0 in line:** Systematic bias from simultaneous multi-sensor detection  
- **0.5 in / 0.75 in lines:** Smallest deviation across displacement range  

### Recommended Track Line Width

A track width of approximately **0.5 inches** produced the most accurate and consistent lateral position estimates for line-following applications.

### Demonstration Video

[Lab 3 Demonstration Video](https://indiana-my.sharepoint.com/:v:/g/personal/jfmedina_iu_edu/IQDYtCynyKqITYx1japxoAE6AXEUUOIj5QQJ8RlnAIRb8-E)

---

## Lab 4 - PID Line Following Controller

### Completed Tasks
- [x] Implemented PID-based line-following controller
- [x] Integrated QTR line sensor system from Lab 3
- [x] Logged controller error and wheel speeds
- [x] Tuned **P**, **PD**, and **PID** control strategies
- [x] Analyzed controller performance using error vs time graphs
- [x] Determined fastest reliable line-following configuration

### Summary

This lab implemented a **PID-based line-following controller** on the Romi robot. The robot uses the reflectance sensor array from Lab 3 to measure the position of a black line relative to the center of the robot.

The line sensor returns a value between **0 and 5000** corresponding to the position of the detected line across the sensor array. This value is converted into a signed tracking error:

```cpp
error = CENTER - position;
```

where:

- **error = 0** → line centered under robot  
- **positive error** → line to the left  
- **negative error** → line to the right  

The controller calculates a steering correction using:

```cpp
correction = P + I + D
```

Motor commands are generated using differential drive:

```cpp
leftSpeed  = baseSpeed - correction;
rightSpeed = baseSpeed + correction;
```

This allows the robot to continuously adjust its heading and remain centered on the line.

### Controller Comparison

Three controller configurations were tested:

**P Controller**
- Fast response
- Large oscillations
- Overshoot during turns

**PD Controller**
- Reduced oscillation
- Faster stabilization
- Best performance for high-speed tracking

**PID Controller**
- Improved steady-state accuracy
- Slightly slower response during sharp disturbances

### Results

Error vs time plots were generated from logged data to evaluate how quickly the robot returned to the line after encountering disturbances such as turns in the track.

The results showed that:

- **P control** produced fast response but unstable tracking
- **PID control** improved accuracy but slowed recovery slightly
- **PD control** provided the best balance between stability and responsiveness

### Optimal Control Strategy

The **PD controller produced the fastest reliable line-following performance** while maintaining stable tracking of the line.

### Demonstration Videos

**P Controller**

[Lab 4 P-Controller Demonstration](https://indiana-my.sharepoint.com/personal/jfmedina_iu_edu/_layouts/15/stream.aspx?id=%2Fpersonal%2Fjfmedina%5Fiu%5Fedu%2FDocuments%2FAttachments%2Fp%5Fcontroller%5Fdemo%2Emp4)

**PD Controller**

[Lab 4 PD-Controller Demonstration](https://indiana-my.sharepoint.com/personal/jfmedina_iu_edu/_layouts/15/stream.aspx?id=%2Fpersonal%2Fjfmedina%5Fiu%5Fedu%2FDocuments%2FAttachments%2Fpd%5Fcontroller%5Fdemo%2Emp4)

**PID Controller**

[Lab 4 PID-Controller Demonstration](https://indiana-my.sharepoint.com/personal/jfmedina_iu_edu/_layouts/15/stream.aspx?id=%2Fpersonal%2Fjfmedina%5Fiu%5Fedu%2FDocuments%2FAttachments%2Fpid%5Fcontroller%5Fdemo%2Emp4)
