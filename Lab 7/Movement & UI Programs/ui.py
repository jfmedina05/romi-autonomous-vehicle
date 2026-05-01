import curses
import time
import csv
from a import AStar


def create_error_bar(error, width=41):
    max_error = 30.0
    center = width // 2
    scaled = int((error / max_error) * center)
    pos = max(0, min(width - 1, center + scaled))

    bar = ["-"] * width
    bar[center] = "|"
    bar[pos] = "O"
    return "".join(bar)


def create_speedometer(value, min_val=-300, max_val=300, width=24):
    value = max(min_val, min(max_val, value))
    ratio = (value - min_val) / (max_val - min_val)
    fill = int(ratio * width)

    bar = ["-"] * width
    for i in range(fill):
        if 0 <= i < width:
            bar[i] = "="

    return "[" + "".join(bar) + f"] {value:>4}"


def draw_box(stdscr, y, x, h, w, title=""):
    if h < 2 or w < 2:
        return

    stdscr.addstr(y, x, "+" + "-" * (w - 2) + "+")
    for row in range(y + 1, y + h - 1):
        stdscr.addstr(row, x, "|")
        stdscr.addstr(row, x + w - 1, "|")
    stdscr.addstr(y + h - 1, x, "+" + "-" * (w - 2) + "+")

    if title:
        title_text = f" {title} "
        title_x = x + max(2, (w - len(title_text)) // 2)
        if title_x + len(title_text) < x + w - 1:
            stdscr.addstr(y, title_x, title_text)


def safe_addstr(stdscr, y, x, text, attr=0):
    max_y, max_x = stdscr.getmaxyx()
    if 0 <= y < max_y and 0 <= x < max_x:
        stdscr.addstr(y, x, text[: max_x - x - 1], attr)


def main(stdscr):
    romi = AStar()

    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.keypad(True)
    stdscr.timeout(100)

    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_CYAN, -1)     # borders/titles
    curses.init_pair(2, curses.COLOR_GREEN, -1)    # normal/manual
    curses.init_pair(3, curses.COLOR_YELLOW, -1)   # auto/warning
    curses.init_pair(4, curses.COLOR_RED, -1)      # stop/error
    curses.init_pair(5, curses.COLOR_MAGENTA, -1)  # logging
    curses.init_pair(6, curses.COLOR_BLACK, curses.COLOR_WHITE)  # banner

    mode = "MANUAL"
    status_msg = "Ready."
    is_logging = False
    log_filename = ""
    csv_file = None
    csv_writer = None
    start_time = 0

    romi.set_auto_mode(False)
    time.sleep(0.01)
    romi.motors(0, 0)

    kp, ki, kd = 1.7, 0.3, 1.2
    romi.write_pid(kp, ki, kd)

    current_left, current_right = 0, 0

    while True:
        char = stdscr.getch()

        if char == ord('q'):
            break

        elif char == ord('m'):
            mode = "MANUAL"
            romi.set_auto_mode(False)
            romi.motors(0, 0)
            current_left, current_right = 0, 0
            status_msg = "Switched to Manual Control."

        elif char == ord('a'):
            mode = "AUTO (PID)"
            romi.set_auto_mode(True)
            status_msg = "PID loop running. Calibrate first."

        elif char == ord('c'):
            status_msg = "Calibrating..."
            romi.trigger_calibration()
            while romi.check_if_calibrating():
                stdscr.clear()
                safe_addstr(stdscr, 1, 2, " ROMI PROJECT 5 ", curses.color_pair(6))
                safe_addstr(stdscr, 3, 2, "Calibration in progress...", curses.color_pair(3))
                stdscr.refresh()
                time.sleep(0.2)
            status_msg = "Calibration complete."

        elif char == ord('L') or char == ord('l'):
            if is_logging:
                is_logging = False
                if csv_file:
                    csv_file.close()
                    csv_file = None
                status_msg = f"Saved log to {log_filename}"
            else:
                log_filename = f"log_{time.strftime('%Y%m%d_%H%M%S')}.csv"
                csv_file = open(log_filename, 'w', newline='')
                csv_writer = csv.writer(csv_file)
                csv_writer.writerow([
                    "time_s", "mode", "left_enc", "right_enc", "line_error",
                    "kp", "ki", "kd", "left_cmd", "right_cmd", "battery_mv"
                ])
                is_logging = True
                start_time = time.time()
                status_msg = f"Logging started: {log_filename}"

        elif char == ord('P'):
            kp = round(kp + 0.1, 2)
            romi.write_pid(kp, ki, kd)
        elif char == ord('p'):
            kp = max(0.0, round(kp - 0.1, 2))
            romi.write_pid(kp, ki, kd)
        elif char == ord('I'):
            ki = round(ki + 0.05, 2)
            romi.write_pid(kp, ki, kd)
        elif char == ord('i'):
            ki = max(0.0, round(ki - 0.05, 2))
            romi.write_pid(kp, ki, kd)
        elif char == ord('D'):
            kd = round(kd + 0.1, 2)
            romi.write_pid(kp, ki, kd)
        elif char == ord('d'):
            kd = max(0.0, round(kd - 0.1, 2))
            romi.write_pid(kp, ki, kd)

        elif mode == "MANUAL" and char != -1:
            target_left, target_right = current_left, current_right

            if char == curses.KEY_UP:
                target_left, target_right = 100, 100
                status_msg = "Driving forward"
            elif char == curses.KEY_DOWN:
                target_left, target_right = -100, -100
                status_msg = "Driving reverse"
            elif char == curses.KEY_LEFT:
                target_left, target_right = -75, 75
                status_msg = "Turning left"
            elif char == curses.KEY_RIGHT:
                target_left, target_right = 75, -75
                status_msg = "Turning right"
            elif char == ord(' '):
                target_left, target_right = 0, 0
                status_msg = "Motors stopped"

            if target_left != current_left or target_right != current_right:
                romi.motors(target_left, target_right)
                current_left, current_right = target_left, target_right

        sensors = romi.read_analog()
        time.sleep(0.01)
        encoders = romi.read_encoders()
        time.sleep(0.01)
        batt = romi.read_battery_millivolts()
        time.sleep(0.01)
        error, l_cmd, r_cmd = romi.read_p5_telemetry()

        if is_logging and csv_writer:
            t = round(time.time() - start_time, 2)
            csv_writer.writerow([
                t, mode, encoders[0], encoders[1], round(error, 2),
                kp, ki, kd, l_cmd, r_cmd, batt[0]
            ])

        stdscr.clear()
        max_y, max_x = stdscr.getmaxyx()

        safe_addstr(stdscr, 0, 0, " " * (max_x - 1), curses.color_pair(6))
        title = "ROMI PROJECT 5  |  OPERATOR INTERFACE"
        safe_addstr(stdscr, 0, max(0, (max_x - len(title)) // 2), title, curses.color_pair(6))

        draw_box(stdscr, 2, 2, 5, max_x - 4, "SYSTEM")
        draw_box(stdscr, 8, 2, 8, max_x // 2 - 3, "TELEMETRY")
        draw_box(stdscr, 8, max_x // 2, 8, max_x - (max_x // 2) - 2, "CONTROL / PID")
        draw_box(stdscr, 17, 2, 7, max_x - 4, "SPEEDOMETERS")
        draw_box(stdscr, 25, 2, 5, max_x - 4, "LINE ERROR")
        draw_box(stdscr, 31, 2, 4, max_x - 4, "STATUS")

        mode_attr = curses.color_pair(2) if mode == "MANUAL" else curses.color_pair(3)
        log_attr = curses.color_pair(5) if is_logging else curses.color_pair(4)

        safe_addstr(stdscr, 3, 4, f"Mode: {mode}", mode_attr)
        safe_addstr(stdscr, 3, 28, f"Logging: {'ACTIVE' if is_logging else 'INACTIVE'}", log_attr)
        safe_addstr(stdscr, 4, 4, "[m] Manual   [a] Auto   [c] Calibrate   [L] Log   [q] Quit", curses.color_pair(1))
        safe_addstr(stdscr, 5, 4, "Drive: Arrow Keys   Stop: Space", curses.color_pair(1))

        safe_addstr(stdscr, 9, 4,  f"Battery : {batt[0]} mV", curses.color_pair(2))
        safe_addstr(stdscr, 10, 4, f"Encoders: L={encoders[0]}   R={encoders[1]}", curses.color_pair(2))
        safe_addstr(stdscr, 11, 4, f"Motors  : L={l_cmd}   R={r_cmd}", curses.color_pair(2))
        safe_addstr(stdscr, 12, 4, f"Sensors : {sensors}", curses.color_pair(2))

        safe_addstr(stdscr, 9,  max_x // 2 + 2, f"Kp: {kp:.2f}   [P/p]", curses.color_pair(3))
        safe_addstr(stdscr, 10, max_x // 2 + 2, f"Ki: {ki:.2f}   [I/i]", curses.color_pair(3))
        safe_addstr(stdscr, 11, max_x // 2 + 2, f"Kd: {kd:.2f}   [D/d]", curses.color_pair(3))
        safe_addstr(stdscr, 12, max_x // 2 + 2, f"Current Error: {error:6.2f}", curses.color_pair(3))

        safe_addstr(stdscr, 18, 4, "LEFT  CMD ", curses.color_pair(1))
        safe_addstr(stdscr, 19, 4, create_speedometer(l_cmd), curses.color_pair(2))

        safe_addstr(stdscr, 21, 4, "RIGHT CMD ", curses.color_pair(1))
        safe_addstr(stdscr, 22, 4, create_speedometer(r_cmd), curses.color_pair(2))

        error_attr = curses.color_pair(4) if abs(error) > 15 else curses.color_pair(3)
        safe_addstr(stdscr, 26, 4, f"Error: {error:6.2f}", error_attr)
        safe_addstr(stdscr, 27, 4, "[" + create_error_bar(error, width=max(20, min(60, max_x - 12))) + "]", curses.color_pair(1))
        safe_addstr(stdscr, 28, 4, "Left of center = robot drifting left | Right of center = robot drifting right", curses.color_pair(1))

        status_attr = curses.color_pair(2)
        if "stopped" in status_msg.lower() or "saved" in status_msg.lower():
            status_attr = curses.color_pair(4)
        elif "calibr" in status_msg.lower() or "running" in status_msg.lower():
            status_attr = curses.color_pair(3)

        safe_addstr(stdscr, 32, 4, status_msg, status_attr)
        if is_logging:
            safe_addstr(stdscr, 33, 4, f"Log file: {log_filename}", curses.color_pair(5))

        stdscr.refresh()

    if csv_file:
        csv_file.close()

    romi.set_auto_mode(False)
    romi.motors(0, 0)


if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        pass
