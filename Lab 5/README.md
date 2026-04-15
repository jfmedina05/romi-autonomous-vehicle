# 🚗 Romi Autonomous Vehicle — Operator Interface & Data Logging (Project 5)

## 📌 Overview
This project implements a **terminal-based operator interface** for the Romi robot running on a Raspberry Pi. The system allows real-time interaction with the robot, including manual control, autonomous PID-based line following, telemetry visualization, and CSV data logging for analysis.

Built using Python and the **Curses library**, this interface provides a unified environment for **control, monitoring, and tuning**.

> This project fulfills all requirements outlined in Project 5: Operator Interface with Curses and Data Logging

---

## 🎯 Features

### 🕹️ Control Modes
- **Manual Mode**
  - Keyboard-based driving
  - Direct control of left/right motor speeds

- **Autonomous Mode (PID)**
  - Robot follows line using onboard PID controller
  - Controlled via I2C communication

### 🎛️ Live PID Tuning
- Adjust PID gains in real time:
  - `P / p` → Increase / decrease Kp  
  - `I / i` → Increase / decrease Ki  
  - `D / d` → Increase / decrease Kd  
- Immediate updates sent to robot without restarting

### 📊 Telemetry Display
- Real-time updates (~10 Hz refresh rate)
- Displays:
  - Motor speeds
  - Encoder values
  - Line sensor error
  - Battery voltage
  - Current mode

### 📈 Live ASCII Graph
- Visual representation of line error
- Centered at zero with dynamic movement
- Helps identify oscillations and tuning quality

### 📝 Data Logging (CSV)
- Toggle logging with keyboard input
- Automatically generates uniquely named files:
- log_YYYYMMDD_HHMMSS.csv

- Captures:
- Timestamp
- Mode
- Wheel speeds
- Line error
- PID values
- Motor commands
- Battery voltage

---

## 🏗️ System Architecture

The system is divided into two main components:

### 1. `ui.py`
- Handles:
- Curses UI rendering
- Keyboard input
- Mode switching
- Telemetry display
- Logging

### 2. `a.py`
- Handles:
- I2C communication with Romi
- Reading sensor + encoder data
- Writing motor commands
- Sending PID parameters

> The UI runs in a continuous loop (~10 Hz), refreshing even without user input to ensure real-time telemetry updates

---

## 🔄 Mode Switching Logic

- Press `m` → Switch to **Manual Mode**
- Disables autonomous control
- Resets motor speeds to zero

- Press `a` → Switch to **Autonomous Mode**
- Enables PID control on robot

⚠️ Important:
- Motor values are reset when switching modes to prevent sudden jumps

---

## 📊 Data Logging Format

Example CSV structure:
time_s,mode,left_speed,right_speed,line_error,kp,ki,kd,left_cmd,right_cmd,battery_mv


### Notes:
- Time is recorded as **elapsed time (seconds)** for easier plotting
- Logging safely closes file on exit
- Corrupted I2C values may appear and should be filtered during analysis

---

## 🎥 Demo Video

A full demonstration of the system (manual control, autonomous mode, PID tuning, live graph, and logging) is included below:

👉 *[Insert your demo video link here]*

---

## 📈 Example Insights (From Data)
- Stable battery range (~7V)
- Motor commands respond proportionally to error
- PID tuning directly impacts oscillation behavior
- Outliers in sensor data can occur due to I2C noise

---

## 🧠 Key Learnings
- Real-time UI requires **non-blocking input handling**
- PID tuning is significantly more efficient when done live
- I2C communication can introduce noise → requires filtering
- Separating control (robot) and interface (Pi) improves stability

---

### Controls

| Key | Action |
|-----|--------|
| `m` | Manual mode |
| `a` | Autonomous mode |
| `P/p` | Adjust Kp |
| `I/i` | Adjust Ki |
| `D/d` | Adjust Kd |
| `L` | Toggle logging |
| `q` | Quit |


## 📊 Future Improvements

- Add filtering for corrupted sensor values  
- Improve graph resolution  
- Add configurable refresh rate  
- Export plots automatically from logs  

---

## 📄 Report & Documentation

This implementation aligns with:

- UI + functionality requirements  
- Logging + CSV structure  
- Graph visualization  
- PID tuning system  

As specified in the Project 5 guidelines

---

## Video
[Lab 5 Demonstration Video](https://indiana-my.sharepoint.com/:v:/g/personal/jfmedina_iu_edu/IQB37IrWxBSBSrbIe3JLr7UsAVS4zFkF70RGzetWXUnAc94?e=yDt7e6&nav=eyJyZWZlcnJhbEluZm8iOnsicmVmZXJyYWxBcHAiOiJTdHJlYW1XZWJBcHAiLCJyZWZlcnJhbFZpZXciOiJTaGFyZURpYWxvZy1MaW5rIiwicmVmZXJyYWxBcHBQbGF0Zm9ybSI6IldlYiIsInJlZmVycmFsTW9kZSI6InZpZXcifX0%3D)
