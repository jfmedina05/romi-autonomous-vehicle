# Lab 3 – Line Sensor Characterization and Accuracy Analysis

---

## Discussion of Line Sensor Installation and Software

This program utilizes the Romi reflectance sensor array to detect and estimate the lateral position of a track line relative to the robot’s centerline. The array consists of six infrared (IR) emitter–detector pairs mounted beneath the front of the Romi chassis.

Each sensor emits IR light toward the surface and measures the intensity of reflected radiation. Light-colored surfaces such as the white background reflect a greater amount of IR radiation, while darker surfaces such as the black track line reflect significantly less. This contrast in reflectance allows the robot to distinguish between the line and the surrounding surface.

Sensor readings are processed using the **QTRSensors** library. During initialization, the sensors are calibrated by sweeping the array across both black and white surfaces to determine minimum and maximum reflectance values for each sensor. Subsequent readings are normalized based on these calibration values.

The function `readLineBlack()` is used to estimate the position of the detected line relative to the center of the sensor array using a weighted centroid calculation. The reported line position is centered by subtracting the midpoint value, producing a signed error where:

- **0** indicates the line is directly beneath the center of the robot  
- **Positive values** indicate the line is to the right of center  
- **Negative values** indicate the line is to the left of center  

This signed error value was recorded and used to evaluate sensor accuracy.

---

## Line Sensor Accuracy Measurements

Sensor accuracy was evaluated by positioning the robot over track lines of varying widths and translating the robot laterally in increments of **0.25 inches** relative to the line center.

The following line widths were tested:

- **0.125 in**
- **0.5 in**
- **0.75 in**
- **1.0 in**

At each displacement position, the robot was held stationary for approximately five seconds while the reported line position was recorded through the onboard microcontroller. Multiple readings were collected and averaged in order to reduce measurement noise.

The reported displacement was computed from the centered line position estimate and converted into physical units based on the known spacing between adjacent sensors. Measurement error at each position was calculated as:

Error = Reported Displacement − Actual Displacement

The resulting error values for each tested line width were plotted as a function of actual line displacement.

---

## Accuracy Results

The combined error plot compares the sensor-reported position error for each line width across the full displacement range. Ideally, the sensor-reported position would match the measured displacement, resulting in an error of zero.

Results indicate that the narrowest line width (**0.125 in**) produced the largest deviation from the expected response, particularly at larger displacements from the sensor array center. This behavior is likely due to insufficient sensor coverage of the narrow line.

The widest tested line (**1.0 in**) exhibited smoother sensor transitions but introduced systematic bias at larger lateral offsets, likely due to multiple sensors simultaneously detecting the line.

The **0.5 in** and **0.75 in** line widths produced comparatively smaller deviations across the displacement range, indicating improved agreement between reported and actual line positions.

---

## Recommended Track Line Width

Based on the observed measurement errors, a track line width of approximately **0.5 inches** produced the most accurate and consistent position estimates from the sensor array.

Narrower lines resulted in increased variability due to incomplete sensor detection of the line surface, while wider lines introduced systematic bias in the reported position due to simultaneous detection by multiple sensors.

Therefore, a track line width of approximately **0.5 inches** is recommended for optimal performance of the Romi reflectance sensor array in line-following applications.

---

## Demonstration Video

[Lab 3 Demonstration Video](https://indiana-my.sharepoint.com/:v:/g/personal/jfmedina_iu_edu/IQDYtCynyKqITYx1japxoAE6AXEUUOIj5QQJ8RlnAIRb8-E?e=kDgAjy&nav=eyJyZWZlcnJhbEluZm8iOnsicmVmZXJyYWxBcHAiOiJTdHJlYW1XZWJBcHAiLCJyZWZlcnJhbFZpZXciOiJTaGFyZURpYWxvZy1MaW5rIiwicmVmZXJyYWxBcHBQbGF0Zm9ybSI6IldlYiIsInJlZmVycmFsTW9kZSI6InZpZXcifX0%3D)
