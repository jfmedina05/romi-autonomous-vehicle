#!/usr/bin/env python3

import curses
import csv
import os
import time
from collections import deque
from dataclasses import dataclass
from datetime import datetime

from a_star import AStar


LOG_DIR = "logs"

DRIVE_STEP = 100
PID_STEP_KP = 0.01
PID_STEP_KI = 0.0005
PID_STEP_KD = 0.005

UI_DT = 0.10
CONTROL_DT = 0.10
GRAPH_HISTORY = 120

MANUAL = "MANUAL"
AUTO = "AUTO"

SENSOR_COUNT = 6
CENTER = 2500
WEIGHTS = [0, 1000, 2000, 3000, 4000, 5000]

MAX_SPEED = 300
BASE_SPEED = 120


@dataclass
class Telemetry:
    time_s: float = 0.0
    mode: str = MANUAL
    left_speed: float = 0.0
    right_speed: float = 0.0
    left_cmd: int = 0
    right_cmd: int = 0
    line_error: float = 0.0
    kp: float = 0.04
    ki: float = 0.0005
    kd: float = 0.02
    enc_left: int = 0
    enc_right: int = 0
    battery_mv: int = 0
    sensors: list = None
    calibrated: bool = False

    def __post_init__(self):
        if self.sensors is None:
            self.sensors = [0, 0, 0, 0, 0, 0]


class CSVLogger:
    def __init__(self, log_dir=LOG_DIR):
        self.log_dir = log_dir
        os.makedirs(self.log_dir, exist_ok=True)
        self.file = None
        self.writer = None
        self.active = False
        self.filename = ""

    def start(self):
        if self.active:
            return self.filename

        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.filename = os.path.join(self.log_dir, f"lab5_log_{ts}.csv")
        self.file = open(self.filename, "w", newline="")
        self.writer = csv.writer(self.file)
        self.writer.writerow([
            "time_s", "mode", "left_speed", "right_speed", "line_error",
            "kp", "ki", "kd", "left_cmd", "right_cmd", "battery_mv",
            "enc_left", "enc_right", "s0", "s1", "s2", "s3", "s4", "s5"
        ])
        self.active = True
        return self.filename

    def log(self, t):
        if not self.active or self.writer is None:
            return

        self.writer.writerow([
            f"{t.time_s:.3f}",
            t.mode,
            f"{t.left_speed:.3f}",
            f"{t.right_speed:.3f}",
            f"{t.line_error:.3f}",
            f"{t.kp:.6f}",
            f"{t.ki:.6f}",
            f"{t.kd:.6f}",
            t.left_cmd,
            t.right_cmd,
            t.battery_mv,
            t.enc_left,
            t.enc_right,
            *t.sensors
        ])
        self.file.flush()

    def stop(self):
        if self.file:
            self.file.close()
        self.file = None
        self.writer = None
        self.active = False


class HardwareController:
    def __init__(self):
        self.robot = AStar()   # Uses your existing a_star.py over I2C
        self.start_time = time.time()

        self.left_cmd = 0
        self.right_cmd = 0

        self.kp = 0.04
        self.ki = 0.0005
        self.kd = 0.02

        self.integral = 0.0
        self.last_error = 0.0

        self.mode = MANUAL
        self.calibrated = True   # with your current AStar interface, no explicit calibrate API

        self.prev_enc_left = 0
        self.prev_enc_right = 0
        self.prev_speed_time = time.time()

        self.last_button_a = False

        self.telemetry = Telemetry(kp=self.kp, ki=self.ki, kd=self.kd)

    def stop(self):
        self.left_cmd = 0
        self.right_cmd = 0
        self.robot.motors(0, 0)

    def set_manual_motors(self, left, right):
        self.left_cmd = int(max(-MAX_SPEED, min(MAX_SPEED, left)))
        self.right_cmd = int(max(-MAX_SPEED, min(MAX_SPEED, right)))
        self.robot.motors(self.left_cmd, self.right_cmd)

    def set_mode_manual(self):
        self.mode = MANUAL
        self.stop()

    def set_mode_auto(self):
        self.mode = AUTO

    def set_pid(self, kp, ki, kd):
        self.kp = max(0.0, kp)
        self.ki = max(0.0, ki)
        self.kd = max(0.0, kd)

    def read_button_a_pressed(self):
        a, _, _ = self.robot.read_buttons()
        pressed = bool(a)
        edge = pressed and not self.last_button_a
        self.last_button_a = pressed
        return edge

    def compute_line_error(self, sensors):
        total = sum(sensors)
        if total <= 0:
            position = CENTER
        else:
            weighted_sum = 0
            for i in range(SENSOR_COUNT):
                weighted_sum += sensors[i] * WEIGHTS[i]
            position = weighted_sum / total

        error = position - CENTER
        return position, error

    def run_pid(self, error):
        self.integral += error
        self.integral = max(-10000.0, min(10000.0, self.integral))

        derivative = error - self.last_error
        correction = self.kp * error + self.ki * self.integral + self.kd * derivative

        left = int(BASE_SPEED - correction)
        right = int(BASE_SPEED + correction)

        left = max(-MAX_SPEED, min(MAX_SPEED, left))
        right = max(-MAX_SPEED, min(MAX_SPEED, right))

        self.left_cmd = left
        self.right_cmd = right
        self.robot.motors(left, right)

        self.last_error = error

    def update_telemetry(self):
        sensors = list(self.robot.read_analog())
        enc_left, enc_right = self.robot.read_encoders()
        battery = self.robot.read_battery_millivolts()[0]

        position, line_error = self.compute_line_error(sensors)

        if self.mode == AUTO:
            self.run_pid(line_error)

        now = time.time()
        dt = now - self.prev_speed_time
        if dt > 0:
            left_speed = (enc_left - self.prev_enc_left) / dt
            right_speed = (enc_right - self.prev_enc_right) / dt
        else:
            left_speed = 0.0
            right_speed = 0.0

        self.prev_enc_left = enc_left
        self.prev_enc_right = enc_right
        self.prev_speed_time = now

        self.telemetry = Telemetry(
            time_s=now - self.start_time,
            mode=self.mode,
            left_speed=left_speed,
            right_speed=right_speed,
            left_cmd=self.left_cmd,
            right_cmd=self.right_cmd,
            line_error=line_error,
            kp=self.kp,
            ki=self.ki,
            kd=self.kd,
            enc_left=enc_left,
            enc_right=enc_right,
            battery_mv=battery,
            sensors=sensors,
            calibrated=self.calibrated
        )
        return self.telemetry

    def shutdown(self):
        try:
            self.stop()
            self.robot.leds(0, 0, 0)
        except Exception:
            pass


def safe_addstr(win, y, x, text, attr=0):
    h, w = win.getmaxyx()
    if 0 <= y < h and 0 <= x < w:
        try:
            win.addstr(y, x, str(text)[:max(0, w - x - 1)], attr)
        except curses.error:
            pass


def draw_box(win, y, x, h, w, title=""):
    if h < 2 or w < 2:
        return

    for i in range(x, x + w):
        try:
            win.addch(y, i, ord('-'))
            win.addch(y + h - 1, i, ord('-'))
        except curses.error:
            pass

    for j in range(y, y + h):
        try:
            win.addch(j, x, ord('|'))
            win.addch(j, x + w - 1, ord('|'))
        except curses.error:
            pass

    for cy, cx in [(y, x), (y, x + w - 1), (y + h - 1, x), (y + h - 1, x + w - 1)]:
        try:
            win.addch(cy, cx, ord('+'))
        except curses.error:
            pass

    if title:
        safe_addstr(win, y, x + 2, f"[{title}]")


def draw_error_graph(win, values, y, x, h, w):
    draw_box(win, y, x, h, w, "Line Error Graph")
    if h < 5 or w < 6 or not values:
        return

    plot_top = y + 1
    plot_bottom = y + h - 2
    plot_left = x + 1
    plot_right = x + w - 2
    plot_h = plot_bottom - plot_top + 1
    plot_w = plot_right - plot_left + 1
    mid_row = plot_top + plot_h // 2

    for col in range(plot_left, plot_right + 1):
        try:
            win.addch(mid_row, col, ord('.'))
        except curses.error:
            pass

    max_abs = max(1.0, max(abs(v) for v in values))
    recent = list(values)[-plot_w:]

    for i, val in enumerate(recent):
        col = plot_left + i
        scaled = int((val / max_abs) * ((plot_h - 1) / 2))
        row = mid_row - scaled
        row = max(plot_top, min(plot_bottom, row))
        try:
            win.addch(row, col, ord('*'))
        except curses.error:
            pass


def run_ui(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(1)

    ctrl = None
    logger = CSVLogger()
    error_history = deque(maxlen=GRAPH_HISTORY)
    last_msg = "Starting..."
    last_control_time = time.time()

    try:
        ctrl = HardwareController()
        ctrl.robot.leds(0, 0, 1)
        last_msg = "I2C connection opened"
    except Exception as e:
        stdscr.erase()
        safe_addstr(stdscr, 2, 2, "Hardware startup failed", curses.A_BOLD)
        safe_addstr(stdscr, 4, 2, str(e))
        safe_addstr(stdscr, 6, 2, "Check I2C wiring, power, and address 0x14.")
        safe_addstr(stdscr, 8, 2, "Press any key to exit.")
        stdscr.nodelay(False)
        stdscr.getch()
        return

    while True:
        now = time.time()
        key = stdscr.getch()

        if key == 27:
            break

        if ctrl.read_button_a_pressed():
            last_msg = "Button A pressed"

        if key in (ord('m'), ord('M')):
            ctrl.set_mode_manual()
            last_msg = "MANUAL mode"

        elif key in (ord('t'), ord('T')):
            ctrl.set_mode_auto()
            last_msg = "AUTO mode"

        elif key in (ord('w'), ord('W')) and ctrl.mode == MANUAL:
            ctrl.set_manual_motors(DRIVE_STEP, DRIVE_STEP)
            last_msg = "Forward"

        elif key in (ord('s'), ord('S')) and ctrl.mode == MANUAL:
            ctrl.set_manual_motors(-DRIVE_STEP, -DRIVE_STEP)
            last_msg = "Backward"

        elif key in (ord('a'), ord('A')) and ctrl.mode == MANUAL:
            ctrl.set_manual_motors(-DRIVE_STEP, DRIVE_STEP)
            last_msg = "Turn left"

        elif key in (ord('d'), ord('D')) and ctrl.mode == MANUAL:
            ctrl.set_manual_motors(DRIVE_STEP, -DRIVE_STEP)
            last_msg = "Turn right"

        elif key in (ord('x'), ord('X')):
            ctrl.stop()
            last_msg = "Stop"

        elif key == ord('u'):
            ctrl.set_pid(ctrl.kp + PID_STEP_KP, ctrl.ki, ctrl.kd)
            last_msg = f"Kp = {ctrl.kp:.4f}"

        elif key == ord('j'):
            ctrl.set_pid(ctrl.kp - PID_STEP_KP, ctrl.ki, ctrl.kd)
            last_msg = f"Kp = {ctrl.kp:.4f}"

        elif key == ord('i'):
            ctrl.set_pid(ctrl.kp, ctrl.ki + PID_STEP_KI, ctrl.kd)
            last_msg = f"Ki = {ctrl.ki:.4f}"

        elif key == ord('k'):
            ctrl.set_pid(ctrl.kp, ctrl.ki - PID_STEP_KI, ctrl.kd)
            last_msg = f"Ki = {ctrl.ki:.4f}"

        elif key == ord('o'):
            ctrl.set_pid(ctrl.kp, ctrl.ki, ctrl.kd + PID_STEP_KD)
            last_msg = f"Kd = {ctrl.kd:.4f}"

        elif key == ord('l'):
            ctrl.set_pid(ctrl.kp, ctrl.ki, ctrl.kd - PID_STEP_KD)
            last_msg = f"Kd = {ctrl.kd:.4f}"

        elif key in (ord('r'), ord('R')):
            if logger.active:
                logger.stop()
                last_msg = "Logging stopped"
            else:
                name = logger.start()
                last_msg = f"Logging started: {name}"

        if now - last_control_time >= CONTROL_DT:
            last_control_time = now
            try:
                telemetry = ctrl.update_telemetry()
                error_history.append(telemetry.line_error)
                if logger.active:
                    logger.log(telemetry)
            except Exception as e:
                last_msg = f"I2C error: {e}"
                ctrl.stop()

        t = ctrl.telemetry

        stdscr.erase()
        h, w = stdscr.getmaxyx()

        safe_addstr(stdscr, 0, 2, "P5 - Operator Interface", curses.A_BOLD)
        safe_addstr(stdscr, 1, 2, "Backend: I2C AStar")
        safe_addstr(stdscr, 2, 2, f"Mode: {t.mode}")
        safe_addstr(stdscr, 3, 2, f"Calibrated: {'YES' if t.calibrated else 'NO'}")
        safe_addstr(stdscr, 4, 2, f"Logging: {'ON' if logger.active else 'OFF'}")
        safe_addstr(stdscr, 5, 2, f"CSV: {logger.filename if logger.filename else 'None'}")

        draw_box(stdscr, 7, 2, 15, 42, "Telemetry")
        safe_addstr(stdscr, 8, 4,  f"time_s      : {t.time_s:.3f}")
        safe_addstr(stdscr, 9, 4,  f"left_speed  : {t.left_speed:.2f}")
        safe_addstr(stdscr, 10, 4, f"right_speed : {t.right_speed:.2f}")
        safe_addstr(stdscr, 11, 4, f"left_cmd    : {t.left_cmd}")
        safe_addstr(stdscr, 12, 4, f"right_cmd   : {t.right_cmd}")
        safe_addstr(stdscr, 13, 4, f"line_error  : {t.line_error:.2f}")
        safe_addstr(stdscr, 14, 4, f"enc_left    : {t.enc_left}")
        safe_addstr(stdscr, 15, 4, f"enc_right   : {t.enc_right}")
        safe_addstr(stdscr, 16, 4, f"battery_mv  : {t.battery_mv}")
        safe_addstr(stdscr, 17, 4, f"sensors     : {t.sensors}")
        safe_addstr(stdscr, 18, 4, f"Kp          : {t.kp:.4f}")
        safe_addstr(stdscr, 19, 4, f"Ki          : {t.ki:.4f}")
        safe_addstr(stdscr, 20, 4, f"Kd          : {t.kd:.4f}")

        graph_x = 46
        graph_y = 7
        graph_w = max(30, w - graph_x - 2)
        graph_h = 12
        if graph_x + graph_w < w and graph_y + graph_h < h:
            draw_error_graph(stdscr, error_history, graph_y, graph_x, graph_h, graph_w)

        help_y = 24
        if help_y < h - 6:
            draw_box(stdscr, help_y, 2, min(8, h - help_y - 2), w - 4, "Controls")
            safe_addstr(stdscr, help_y + 1, 4, "m=manual   t=auto   w/s=forward/back   a/d=left/right   x=stop")
            safe_addstr(stdscr, help_y + 2, 4, "u/j=Kp +/-   i/k=Ki +/-   o/l=Kd +/-   r=log toggle   ESC=quit")

        safe_addstr(stdscr, h - 2, 2, f"Status: {last_msg}")
        stdscr.refresh()
        time.sleep(UI_DT)

    if ctrl is not None:
        ctrl.shutdown()
    logger.stop()


if __name__ == "__main__":
    try:
        curses.wrapper(run_ui)
    except KeyboardInterrupt:
        pass