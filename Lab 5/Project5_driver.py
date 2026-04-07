import curses
import csv
import os
import time
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime

from a_star import AStar


LOG_DIR = "logs"

DRIVE_STEP = 100
PID_STEP_KP = 0.01
PID_STEP_KI = 0.0005
PID_STEP_KD = 0.005
MAX_MOTOR_CMD = 150

UI_DT = 0.05
CONTROL_DT = 0.05
GRAPH_HISTORY = 160
I2C_ADDRESS = 20


@dataclass
class Telemetry:
    time_s: float = 0.0
    mode: str = "MANUAL"
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
    sensors: list = field(default_factory=lambda: [0, 0, 0, 0, 0, 0])
    calibrated: bool = False


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

    def log(self, t: Telemetry):
        if not self.active or self.writer is None:
            return
        self.writer.writerow([
            f"{t.time_s:.3f}", t.mode, f"{t.left_speed:.3f}", f"{t.right_speed:.3f}", t.line_error,
            f"{t.kp:.6f}", f"{t.ki:.6f}", f"{t.kd:.6f}", t.left_cmd, t.right_cmd, t.battery_mv,
            t.enc_left, t.enc_right, *t.sensors
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
        self.robot = AStar(address=I2C_ADDRESS)
        if not self.robot.check():
            raise RuntimeError("A-Star not found at I2C address 0x14")

        self.start_time = time.time()
        self.prev_enc_left, self.prev_enc_right = self.robot.read_encoders()
        self.prev_speed_time = time.time()

        self.left_cmd = 0
        self.right_cmd = 0
        self.kp, self.ki, self.kd = self.robot.read_pid()
        self.telemetry = Telemetry(kp=self.kp, ki=self.ki, kd=self.kd)
        self.last_button_a = False

    @staticmethod
    def clamp_motor(value):
        return max(-MAX_MOTOR_CMD, min(MAX_MOTOR_CMD, int(value)))

    @staticmethod
    def mode_name(mode_value):
        return "AUTO" if mode_value == 1 else "MANUAL"

    def set_manual_motors(self, left, right):
        self.left_cmd = self.clamp_motor(left)
        self.right_cmd = self.clamp_motor(right)
        self.robot.motors(self.left_cmd, self.right_cmd)

    def stop(self):
        self.left_cmd = 0
        self.right_cmd = 0
        self.robot.motors(0, 0)

    def set_mode_manual(self):
        self.robot.write_mode(0)
        self.stop()

    def set_mode_auto(self):
        self.stop()
        self.robot.write_mode(1)

    def set_pid(self, kp, ki, kd):
        self.kp = max(0.0, float(kp))
        self.ki = max(0.0, float(ki))
        self.kd = max(0.0, float(kd))
        self.robot.write_pid(self.kp, self.ki, self.kd)

    def read_button_a_pressed(self):
        a, _, _ = self.robot.read_buttons()
        pressed = bool(a)
        edge = pressed and not self.last_button_a
        self.last_button_a = pressed
        return edge

    def update_telemetry(self):
        mode_value = self.robot.read_mode()
        mode = self.mode_name(mode_value)

        enc_left, enc_right = self.robot.read_encoders()
        battery = self.robot.read_battery_millivolts()
        analog = list(self.robot.read_analog())
        calibrated = self.robot.read_calibrated()
        line_error = self.robot.read_line_error()
        auto_left, auto_right = self.robot.read_auto_speeds()

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

        display_left = auto_left if mode == "AUTO" else self.left_cmd
        display_right = auto_right if mode == "AUTO" else self.right_cmd

        self.telemetry = Telemetry(
            time_s=now - self.start_time,
            mode=mode,
            left_speed=left_speed,
            right_speed=right_speed,
            left_cmd=display_left,
            right_cmd=display_right,
            line_error=line_error,
            kp=self.kp,
            ki=self.ki,
            kd=self.kd,
            enc_left=enc_left,
            enc_right=enc_right,
            battery_mv=battery,
            sensors=analog,
            calibrated=calibrated,
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
        safe_addstr(win, y, x + 2, f"[{title}]", curses.A_BOLD)


def draw_error_graph(win, values, y, x, h, w):
    draw_box(win, y, x, h, w, "Line Error Graph")
    if h < 5 or w < 8 or not values:
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

    recent = list(values)[-plot_w:]
    max_abs = max(1.0, max(abs(v) for v in recent))
    safe_addstr(win, y + h - 1, x + 2, f"range +/-{max_abs:.0f}")

    for i, val in enumerate(recent):
        col = plot_left + i
        scaled = int((val / max_abs) * ((plot_h - 1) / 2))
        row = max(plot_top, min(plot_bottom, mid_row - scaled))
        try:
            win.addch(row, col, ord('*'))
        except curses.error:
            pass


def apply_key(ctrl: HardwareController, logger: CSVLogger, key, last_msg):
    if key == -1:
        return last_msg, False

    if key == 27:
        return "Exit requested", True

    if key in (ord('m'), ord('M')):
        ctrl.set_mode_manual()
        return "MANUAL mode", False

    if key in (ord('t'), ord('T')):
        if ctrl.telemetry.calibrated:
            ctrl.set_mode_auto()
            return "AUTO mode", False
        return "Calibrate first with Button A on Romi", False

    if key in (ord('w'), ord('W')) and ctrl.telemetry.mode == "MANUAL":
        ctrl.set_manual_motors(DRIVE_STEP, DRIVE_STEP)
        return "Forward", False

    if key in (ord('s'), ord('S')) and ctrl.telemetry.mode == "MANUAL":
        ctrl.set_manual_motors(-DRIVE_STEP, -DRIVE_STEP)
        return "Backward", False

    if key in (ord('a'), ord('A')) and ctrl.telemetry.mode == "MANUAL":
        ctrl.set_manual_motors(-DRIVE_STEP, DRIVE_STEP)
        return "Turn left", False

    if key in (ord('d'), ord('D')) and ctrl.telemetry.mode == "MANUAL":
        ctrl.set_manual_motors(DRIVE_STEP, -DRIVE_STEP)
        return "Turn right", False

    if key in (ord('x'), ord('X'), ord(' ')):
        ctrl.stop()
        return "Stop", False

    if key == ord('u'):
        ctrl.set_pid(ctrl.kp + PID_STEP_KP, ctrl.ki, ctrl.kd)
        return f"Kp = {ctrl.kp:.4f}", False

    if key == ord('j'):
        ctrl.set_pid(ctrl.kp - PID_STEP_KP, ctrl.ki, ctrl.kd)
        return f"Kp = {ctrl.kp:.4f}", False

    if key == ord('i'):
        ctrl.set_pid(ctrl.kp, ctrl.ki + PID_STEP_KI, ctrl.kd)
        return f"Ki = {ctrl.ki:.4f}", False

    if key == ord('k'):
        ctrl.set_pid(ctrl.kp, ctrl.ki - PID_STEP_KI, ctrl.kd)
        return f"Ki = {ctrl.ki:.4f}", False

    if key == ord('o'):
        ctrl.set_pid(ctrl.kp, ctrl.ki, ctrl.kd + PID_STEP_KD)
        return f"Kd = {ctrl.kd:.4f}", False

    if key == ord('l'):
        ctrl.set_pid(ctrl.kp, ctrl.ki, ctrl.kd - PID_STEP_KD)
        return f"Kd = {ctrl.kd:.4f}", False

    if key in (ord('r'), ord('R')):
        if logger.active:
            logger.stop()
            return "Logging stopped", False
        filename = logger.start()
        return f"Logging started: {filename}", False

    return last_msg, False


def draw_ui(stdscr, ctrl: HardwareController, logger: CSVLogger, error_history, last_msg):
    stdscr.erase()
    h, w = stdscr.getmaxyx()
    t = ctrl.telemetry

    safe_addstr(stdscr, 0, 2, "P5 - Operator Interface", curses.A_BOLD)
    safe_addstr(stdscr, 1, 2, "Backend: I2C / PololuRPiSlave @ 0x14")
    safe_addstr(stdscr, 2, 2, f"Mode: {t.mode}")
    safe_addstr(stdscr, 3, 2, f"Calibrated: {'YES' if t.calibrated else 'NO'}")
    safe_addstr(stdscr, 4, 2, f"Logging: {'ON' if logger.active else 'OFF'}")
    safe_addstr(stdscr, 5, 2, f"CSV: {logger.filename if logger.filename else 'None'}")

    draw_box(stdscr, 7, 2, 15, 42, "Telemetry")
    safe_addstr(stdscr, 8, 4, f"time_s      : {t.time_s:.3f}")
    safe_addstr(stdscr, 9, 4, f"left_speed  : {t.left_speed:.2f}")
    safe_addstr(stdscr, 10, 4, f"right_speed : {t.right_speed:.2f}")
    safe_addstr(stdscr, 11, 4, f"left_cmd    : {t.left_cmd}")
    safe_addstr(stdscr, 12, 4, f"right_cmd   : {t.right_cmd}")
    safe_addstr(stdscr, 13, 4, f"line_error  : {t.line_error}")
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
    help_h = min(8, max(0, h - help_y - 2))
    if help_h >= 4:
        draw_box(stdscr, help_y, 2, help_h, w - 4, "Controls")
        safe_addstr(stdscr, help_y + 1, 4, "Button A on Romi = calibrate sensors")
        safe_addstr(stdscr, help_y + 2, 4, "m=manual  t=auto  w/s=forward/back  a/d=left/right  x or space=stop")
        safe_addstr(stdscr, help_y + 3, 4, "u/j=Kp +/-  i/k=Ki +/-  o/l=Kd +/-  r=log toggle  ESC=quit")

    safe_addstr(stdscr, h - 2, 2, f"Status: {last_msg}")
    stdscr.refresh()


def run_ui(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(1)

    ctrl = HardwareController()
    logger = CSVLogger()
    error_history = deque([0.0], maxlen=GRAPH_HISTORY)

    last_msg = "Connected. Press Button A on Romi to calibrate, then press t for AUTO."
    last_control_time = 0.0

    try:
        while True:
            key = stdscr.getch()
            last_msg, should_exit = apply_key(ctrl, logger, key, last_msg)
            if should_exit:
                break

            if ctrl.read_button_a_pressed():
                last_msg = "Button A pressed on Romi"

            now = time.time()
            if now - last_control_time >= CONTROL_DT:
                last_control_time = now
                telemetry = ctrl.update_telemetry()
                error_history.append(telemetry.line_error)
                if logger.active:
                    logger.log(telemetry)

            draw_ui(stdscr, ctrl, logger, error_history, last_msg)
            time.sleep(UI_DT)
    finally:
        ctrl.shutdown()
        logger.stop()


if __name__ == "__main__":
    try:
        curses.wrapper(run_ui)
    except KeyboardInterrupt:
        pass