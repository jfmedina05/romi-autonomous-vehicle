# Lab 2 – Closed-Loop Square Driver with Wheel Speed Control

## Discussion of Square Driver Program

This program drives the Romi robot in a **square path** using **closed-loop wheel speed control** and encoder feedback. Each side of the square is targeted to be **2 ft (609.6 mm)** long.

The control system operates as a **state machine**:

- **WAIT_START** – Waits for Button A press  
- **DRIVE_SIDE** – Drives forward one side of the square  
- **TURN_90** – Performs an in-place 90° turn  
- **DONE** – Stops after completing all four sides  

### Motion Control Strategy

Motion uses a **PID-based wheel speed controller** combined with:

- **Feedforward motor command** (`BASE_FEEDFORWARD`)  
- **PID speed correction** (`pidDelta()`)  
- **Slew rate limiting** to smooth command changes  
- **Straightness correction** using encoder differences  

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

---

## Approach to Tuning the Wheel Speed Controllers

Tuning followed an iterative experimental process:

1. **Feedforward first** – Set a baseline motor command so wheels move smoothly.  
2. **PID gains next** – Adjusted \(K_p\) and \(K_i\) until speed tracking was stable without oscillation.  
3. **Slew rate limit** – Prevented jerky acceleration.  
4. **Straightness correction (STRAIGHT_K)** – Adjusted until the robot drove straight.  
5. **Distance calibration** – Adjusted `MM_PER_COUNT` using measured travel distance.  
6. **Turn calibration** – Adjusted `TURN_90_COUNTS` until turns were near 90°.

---

## Challenges in Tuning the Wheel Speed Controllers

- Motor torque imbalance caused drifting.
- Encoder noise made derivative control unstable, so \(K_d = 0\).
- Wheel slip during turns affected angle accuracy.
- Small battery voltage changes altered motor speed.
- Finding the correct `MM_PER_COUNT` required multiple test runs.

---

## Accuracy of Final Solution

### Measured Side Lengths

| Side | Measured Length |
|------|-----------------|
| 1    | 24 in |
| 2    | 25 in |
| 3    | 24.5 in |
| 4    | 24.5 in |

### Length Error

Target = **24 in**

| Side | Error (in) | % Error |
|------|------------|---------|
| 1 | 0.0 | 0% |
| 2 | +1.0 | 4.2% |
| 3 | +0.5 | 2.1% |
| 4 | +0.5 | 2.1% |

**Average side length**

\[
\frac{24 + 25 + 24.5 + 24.5}{4} = 24.5 \text{ in}
\]

**Average percent error**

\[
\frac{24.5 - 24}{24} \times 100 = 2.1\%
\]

---

### Track Angle Error

The robot returned close to its starting orientation after completing the square. Visual estimation indicated a small cumulative angular error (<5° total), likely from minor slip during turns.

---

## How Close to the Ideal Distance

The robot achieved an average side length of **24.5 in**, which is **0.5 in above the ideal 24 in**, representing a **2.1% error** — very good for a small mobile robot operating on a flat surface.

---

## Sources of Distance Error

- Wheel slip during turns  
- Uneven floor friction  
- Motor torque imbalance  
- Battery voltage variation  
- Encoder quantization  
- Approximate `MM_PER_COUNT` calibration  

---

## Demonstration Video

(https://indiana-my.sharepoint.com/:v:/g/personal/jfmedina_iu_edu/IQDYtCynyKqITYx1japxoAE6AXEUUOIj5QQJ8RlnAIRb8-E?e=kDgAjy&nav=eyJyZWZlcnJhbEluZm8iOnsicmVmZXJyYWxBcHAiOiJTdHJlYW1XZWJBcHAiLCJyZWZlcnJhbFZpZXciOiJTaGFyZURpYWxvZy1MaW5rIiwicmVmZXJyYWxBcHBQbGF0Zm9ybSI6IldlYiIsInJlZmVycmFsTW9kZSI6InZpZXcifX0%3D)*

---
