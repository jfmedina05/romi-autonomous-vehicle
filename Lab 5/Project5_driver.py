#!/usr/bin/env python3

import curses
import csv
import time
from a_star import AStar

# =========================
# Constants
# =========================
MANUAL = "MANUAL"
AUTO = "AUTO"

SENSOR_COUNT = 6
CENTER = 2500
WEIGHTS = [0, 1000, 2000, 3000, 4000, 5000]

MAX_SPEED = 300
BASE_SPEED = 120
STEP = 25

LOOP_DELAY = 0.05
GRAPH_WIDTH = 60
GRAPH_HEIGHT = 15

# =========================
# Robot / PID state
# =========================
robot = AStar()

mode = MANUAL

left_cmd = 0
right_cmd = 0

Kp = 0.04
Ki = 0.0005
Kd = 0.02

integral = 0.0
last_error = 0.0

selected_gain = 0  # 0=Kp, 1=Ki, 2=Kd

logging_on = False
log_file = None
log_writer = None
log_filename = ""

error_history = []

start_time = time.time()


# =========================
# Helper functions
# =========================
def clamp(value, low, high):
    return max(low, min(high, value))


def stop_robot():
    global left_cmd, right_cmd
    left_cmd = 0
    right_cmd = 0
    robot.motors(0, 0)


def create_log_file():
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    return f"project5_log_{timestamp}.csv"


def start_logging():
    global logging_on, log_file, log_writer, log_filename
    if logging_on:
        return

    log_filename = create_log_file()
    log_file = open(log_filename, "w", newline="")
    log_writer = csv.writer(log_file)
    log_writer.writerow([
        "time_s",
        "mode",
        "left_speed",
        "right_speed",
        "line_error",
        "kp",
        "ki",
        "kd",
        "left_cmd",
        "right_cmd",
        "battery_mv"
    ])
    logging_on = True


def stop_logging():
    global logging_on, log_file, log_writer
    if log_file is not None:
        log_file.close()
    log_file = None
    log_writer = None
    logging_on = False


def read_line_error():
    """
    Uses AStar.read_analog() raw sensor values and computes a weighted position.
    Returns:
        sensors: tuple of 6 sensor values
        position: weighted line position 0..5000
        error: position - 2500
    """
    sensors = robot.read_analog()

    total = sum(sensors)
    if total <= 0:
        position = CENTER
    else:
        weighted_sum = 0
        for i in range(SENSOR_COUNT):
            weighted_sum += sensors[i] * WEIGHTS[i]
        position = weighted_sum / total

    error = position - CENTER
    return sensors, position, error


def run_pid(error):
    global integral, last_error

    integral += error
    integral = clamp(integral, -10000, 10000)

    derivative = error - last_error
    correction = Kp * error + Ki * integral + Kd * derivative

    left = int(BASE_SPEED - correction)
    right = int(BASE_SPEED + correction)

    left = clamp(left, -MAX_SPEED, MAX_SPEED)
    right = clamp(right, -MAX_SPEED, MAX_SPEED)

    last_error = error
    return left, right


def adjust_gain(amount):
    global Kp, Ki, Kd

    if selected_gain == 0:
        Kp = max(0.0, Kp + amount)
    elif selected_gain == 1:
        Ki = max(0.0, Ki + amount * 0.1)
    else:
        Kd = max(0.0, Kd + amount)


def log_row(t_s, error, battery_mv):
    if logging_on and log_writer is not None:
        log_writer.writerow([
            f"{t_s:.3f}",
            mode,
            left_cmd,
            right_cmd,
            f"{error:.3f}",
            f"{Kp:.6f}",
            f"{Ki:.6f}",
            f"{Kd:.6f}",
            left_cmd,
            right_cmd,
            battery_mv
        ])
        log_file.flush()


def draw_graph(win, data):
    win.erase()
    height, width = win.getmaxyx()

    if height < 3 or width < 3:
        return

    win.box()

    mid_y = height // 2

    for x in range(1, width - 1):
        win.addch(mid_y, x, ord('-'))

    points = data[-(width - 2):]

    for i, e in enumerate(points):
        x = i + 1
        scaled = int((e / 2500.0) * ((height - 2) // 2))
        y = mid_y - scaled
        y = clamp(y, 1, height - 2)
        win.addch(y, x, ord('*'))

    win.refresh()


def draw_ui(stdscr, sensors, position, error, encoders, battery_mv):
    stdscr.erase()
    rows, cols = stdscr.getmaxyx()

    stdscr.addstr(0, 2, "Project 5 Operator Interface")
    stdscr.addstr(1, 2, f"Mode: {mode}")
    stdscr.addstr(1, 20, f"Logging: {'ON' if logging_on else 'OFF'}")
    stdscr.addstr(1, 40, f"Log File: {log_filename if logging_on else 'none'}")

    stdscr.addstr(3, 2, "Telemetry")
    stdscr.addstr(4, 4, f"Left Cmd:   {left_cmd:>5}")
    stdscr.addstr(5, 4, f"Right Cmd:  {right_cmd:>5}")
    stdscr.addstr(6, 4, f"Position:   {position:>8.2f}")
    stdscr.addstr(7, 4, f"Line Error: {error:>8.2f}")
    stdscr.addstr(8, 4, f"Encoders:   L={encoders[0]:>6}  R={encoders[1]:>6}")
    stdscr.addstr(9, 4, f"Battery:    {battery_mv:>5} mV")

    stdscr.addstr(11, 2, "Sensors")
    stdscr.addstr(
        12,
        4,
        f"S1={sensors[0]:>4} S2={sensors[1]:>4} S3={sensors[2]:>4} "
        f"S4={sensors[3]:>4} S5={sensors[4]:>4} S6={sensors[5]:>4}"
    )

    stdscr.addstr(14, 2, "PID")
    if selected_gain == 0:
        stdscr.addstr(15, 4, f"Kp = {Kp:.6f}  <", curses.A_REVERSE)
    else:
        stdscr.addstr(15, 4, f"Kp = {Kp:.6f}")

    if selected_gain == 1:
        stdscr.addstr(16, 4, f"Ki = {Ki:.6f}  <", curses.A_REVERSE)
    else:
        stdscr.addstr(16, 4, f"Ki = {Ki:.6f}")

    if selected_gain == 2:
        stdscr.addstr(17, 4, f"Kd = {Kd:.6f}  <", curses.A_REVERSE)
    else:
        stdscr.addstr(17, 4, f"Kd = {Kd:.6f}")

    stdscr.addstr(19, 2, "Controls")
    stdscr.addstr(20, 4, "m = manual mode")
    stdscr.addstr(21, 4, "a = autonomous mode")
    stdscr.addstr(22, 4, "Arrow keys = drive in manual mode")
    stdscr.addstr(23, 4, "space = stop")
    stdscr.addstr(24, 4, "[ and ] = select Kp/Ki/Kd")
    stdscr.addstr(25, 4, "- and + = decrease/increase selected gain")
    stdscr.addstr(26, 4, "l = start/stop logging")
    stdscr.addstr(27, 4, "q = quit")

    stdscr.refresh()

    graph_height = min(GRAPH_HEIGHT, rows - 5)
    graph_width = min(GRAPH_WIDTH, cols - 45)

    if graph_height >= 5 and graph_width >= 20:
        graph_win = curses.newwin(graph_height, graph_width, 3, max(45, cols - graph_width - 2))
        draw_graph(graph_win, error_history)


def handle_input(stdscr):
    global mode, left_cmd, right_cmd, selected_gain

    key = stdscr.getch()
    if key == -1:
        return True

    if key == ord('q'):
        return False

    elif key == ord('m'):
        mode = MANUAL
        stop_robot()

    elif key == ord('a'):
        mode = AUTO

    elif key == ord('l'):
        if logging_on:
            stop_logging()
        else:
            start_logging()

    elif key == ord(' '):
        stop_robot()

    elif key == ord('['):
        selected_gain = (selected_gain - 1) % 3

    elif key == ord(']'):
        selected_gain = (selected_gain + 1) % 3

    elif key in (ord('-'), ord('_')):
        adjust_gain(-0.001)

    elif key in (ord('+'), ord('=')):
        adjust_gain(0.001)

    elif mode == MANUAL:
        if key == curses.KEY_UP:
            left_cmd += STEP
            right_cmd += STEP
        elif key == curses.KEY_DOWN:
            left_cmd -= STEP
            right_cmd -= STEP
        elif key == curses.KEY_LEFT:
            left_cmd -= STEP
            right_cmd += STEP
        elif key == curses.KEY_RIGHT:
            left_cmd += STEP
            right_cmd -= STEP

        left_cmd = clamp(left_cmd, -MAX_SPEED, MAX_SPEED)
        right_cmd = clamp(right_cmd, -MAX_SPEED, MAX_SPEED)

    return True


def main(stdscr):
    global left_cmd, right_cmd

    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.keypad(True)

    robot.leds(0, 0, 1)

    running = True
    while running:
        running = handle_input(stdscr)

        sensors, position, error = read_line_error()
        encoders = robot.read_encoders()
        battery_mv = robot.read_battery_millivolts()[0]

        if mode == AUTO:
            left_cmd, right_cmd = run_pid(error)

        robot.motors(left_cmd, right_cmd)

        error_history.append(error)
        if len(error_history) > 200:
            error_history.pop(0)

        t_s = time.time() - start_time
        log_row(t_s, error, battery_mv)
        draw_ui(stdscr, sensors, position, error, encoders, battery_mv)

        time.sleep(LOOP_DELAY)

    stop_robot()
    stop_logging()
    robot.leds(0, 0, 0)


if __name__ == "__main__":
    curses.wrapper(main)