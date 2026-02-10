# Lab 2 – Square Driver with Wheel Speed Control

## Discussion of Square Driver Program

Our square driver program controls the Romi robot to drive four equal sides and perform an in-place turn between each side. Motion is divided into three phases per side:

1. **Acceleration** – Motor speed increases gradually to reduce jerk.  
2. **Constant motion / deceleration** – Speed decreases smoothly before stopping.  
3. **Turn phase** – Left motor drives forward while right motor reverses to rotate the robot in place.  

To keep the robot moving straight, we applied a **motor scaling correction**:

```cpp
const float LEFT_MOTOR_SCALE  = 1.00;
const float RIGHT_MOTOR_SCALE = 1.12;
```

This compensates for the right motor being slightly weaker than the left.

---

## Approach to Tuning the Wheel Speed Controllers

Tuning focused on achieving smooth and repeatable motion:

- Gradual speed ramping was used instead of sudden commands.  
- The right motor scale factor was increased incrementally until straight motion was observed.  
- Multiple square runs were performed, and side lengths were measured after each adjustment.  
- Small adjustments to the turn speed were made until consistent 90° turns were achieved.  

Tuning was empirical: **adjust → run → measure → refine**.

---

## Challenges in Tuning the Wheel Speed Controllers

- The robot initially drifted due to motor imbalance.  
- Turning accuracy varied due to wheel slip during in-place rotation.  
- Battery voltage changes affected speed consistency.  
- Floor surface friction differences caused variation in side length.  

---

## Accuracy of Final Solution

### Measured Side Lengths

| Side | Measured Length |
|------|-----------------|
| 1    | 24 in |
| 2    | 25 in |
| 3    | 24.5 in |
| 4    | 24.5 in |

### Length Error (per side)

Target side = **24 in**

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

Visual inspection showed the robot returning close to its starting orientation after completing the square. Minor angular deviation was observed, estimated to be less than **5° total accumulated error** across all four turns.

---

## How Close to the Ideal Distance

The final average distance was **24.5 in**, which is **0.5 in above the ideal 24 in**, representing a **2.1% error**, which is within acceptable tolerance for open-loop motor control.

---

## Sources of Distance Error

- Wheel slip during turns  
- Uneven floor friction  
- Motor torque imbalance  
- Battery voltage variation  
- Lack of encoder-based closed-loop distance stopping  

---

## Demonstration Video

*(Insert link to narrated video or TA demonstration here)*

---
