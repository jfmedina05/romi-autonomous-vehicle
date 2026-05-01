import curses
import time
import csv
import redis
from a_star import AStar


# Redis is running on the same Pi as server1.py
r = redis.Redis(
    host="localhost",
    port=6379,
    db=0,
    password="e101class"
)


HIGH_SPEED = 170
LOW_SPEED = 75

STOP_TIME = 2.0
STOP_IGNORE_TIME = 10.0
MARKER_COOLDOWN = 3.0

# Manual driving correction
LEFT_SCALE = 1.00
RIGHT_SCALE = 0.90

MAX_MANUAL_CMD = 200


def create_graph(error, width=40):
    center = width // 2

    normalized = int((error / 30.0) * center)
    pos = max(0, min(width - 1, center + normalized))

    graph = ["-"] * width
    graph[center] = "|"
    graph[pos] = "O"
    return "".join(graph)


def safe_addstr(stdscr, y, x, text, attr=0):
    max_y, max_x = stdscr.getmaxyx()

    if y < 0 or y >= max_y:
        return

    if x < 0 or x >= max_x:
        return

    try:
        stdscr.addstr(y, x, str(text)[:max_x - x - 1], attr)
    except curses.error:
        pass


def safe_call(func, *args):
    try:
        func(*args)
        return True
    except OSError:
        return False


def clamp(value, low, high):
    return max(low, min(high, value))


def scale_manual_command(left, right):
    left = int(left * LEFT_SCALE)
    right = int(right * RIGHT_SCALE)

    left = clamp(left, -MAX_MANUAL_CMD, MAX_MANUAL_CMD)
    right = clamp(right, -MAX_MANUAL_CMD, MAX_MANUAL_CMD)

    return left, right


def read_marker_from_redis():
    try:
        marker = r.hget("latest", "aruco_id")
        action = r.hget("latest", "aruco_action")

        if marker is None:
            return -1, "NONE"

        marker_id = int(marker)
        marker_action = action.decode() if action else "NONE"

        return marker_id, marker_action

    except Exception:
        return -1, "NONE"


def main(stdscr):
    romi = AStar()

    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.keypad(True)
    stdscr.timeout(100)

    mode = "MANUAL"
    status_msg = "Ready."
    marker_msg = "No marker detected."

    is_logging = False
    log_filename = ""
    csv_file = None
    csv_writer = None
    start_time = 0

    # Arduino PID values
    kp = 1.2
    ki = 0.0
    kd = 0.8

    base_speed = LOW_SPEED

    current_left, current_right = 0, 0

    sensors = (0, 0, 0, 0, 0, 0)
    encoders = (0, 0)
    batt = (0,)
    error = 0.0
    l_cmd = 0
    r_cmd = 0

    stop_until = 0
    ignore_stop_until = 0

    last_marker_id = -1
    last_marker_time = 0

    try:
        romi.set_auto_mode(False)
        time.sleep(0.1)

        romi.motors(0, 0)
        time.sleep(0.1)

        romi.write_pid(kp, ki, kd)
        time.sleep(0.1)

        romi.set_base_speed(base_speed)
        time.sleep(0.1)

        status_msg = "Startup complete. Press c to calibrate, then a for AUTO."

    except OSError:
        status_msg = "Startup I2C error. Check Romi power/reset, then continue."

    while True:
        char = stdscr.getch()

        if char == ord("q"):
            break

        elif char == ord("m"):
            mode = "MANUAL"
            stop_until = 0
            marker_msg = "Manual mode. Ignoring road signs."

            if safe_call(romi.set_auto_mode, False):
                time.sleep(0.05)
                safe_call(romi.motors, 0, 0)
                current_left, current_right = 0, 0
                l_cmd, r_cmd = 0, 0
                status_msg = "Switched to Manual Control."
            else:
                status_msg = "I2C error switching to manual."

        elif char == ord("a"):
            mode = "AUTO (PID)"
            stop_until = 0

            safe_call(romi.write_pid, kp, ki, kd)
            time.sleep(0.05)

            safe_call(romi.set_base_speed, base_speed)
            time.sleep(0.05)

            if safe_call(romi.set_auto_mode, True):
                status_msg = "AUTO mode running on Arduino PID."
            else:
                status_msg = "I2C error switching to auto."

        elif char == ord("c"):
            status_msg = "Calibrating..."
            safe_addstr(stdscr, 23, 0, f"Status: {status_msg}")
            stdscr.refresh()

            try:
                romi.trigger_calibration()
                time.sleep(0.1)

                while romi.check_if_calibrating():
                    time.sleep(0.5)

                status_msg = "Calibration complete. Press a for AUTO."

            except OSError:
                status_msg = "I2C error during calibration. Try again."

        elif char == ord("L") or char == ord("l"):
            if is_logging:
                is_logging = False
                if csv_file:
                    csv_file.close()
                    csv_file = None
                status_msg = f"Saved log to {log_filename}"
            else:
                log_filename = f"log_{time.strftime('%Y%m%d_%H%M%S')}.csv"
                csv_file = open(log_filename, "w", newline="")
                csv_writer = csv.writer(csv_file)
                csv_writer.writerow([
                    "time_s",
                    "mode",
                    "left_enc",
                    "right_enc",
                    "line_error",
                    "kp",
                    "ki",
                    "kd",
                    "base_speed",
                    "left_cmd",
                    "right_cmd",
                    "battery_mv",
                    "marker",
                ])
                is_logging = True
                start_time = time.time()
                status_msg = f"Logging started: {log_filename}"

        elif char == ord("P"):
            kp = round(kp + 0.1, 2)
            if safe_call(romi.write_pid, kp, ki, kd):
                status_msg = f"Kp increased to {kp:.2f}"
            else:
                status_msg = "I2C error writing Kp."

        elif char == ord("p"):
            kp = max(0.0, round(kp - 0.1, 2))
            if safe_call(romi.write_pid, kp, ki, kd):
                status_msg = f"Kp decreased to {kp:.2f}"
            else:
                status_msg = "I2C error writing Kp."

        elif char == ord("I"):
            ki = round(ki + 0.05, 2)
            if safe_call(romi.write_pid, kp, ki, kd):
                status_msg = f"Ki increased to {ki:.2f}"
            else:
                status_msg = "I2C error writing Ki."

        elif char == ord("i"):
            ki = max(0.0, round(ki - 0.05, 2))
            if safe_call(romi.write_pid, kp, ki, kd):
                status_msg = f"Ki decreased to {ki:.2f}"
            else:
                status_msg = "I2C error writing Ki."

        elif char == ord("D"):
            kd = round(kd + 0.1, 2)
            if safe_call(romi.write_pid, kp, ki, kd):
                status_msg = f"Kd increased to {kd:.2f}"
            else:
                status_msg = "I2C error writing Kd."

        elif char == ord("d"):
            kd = max(0.0, round(kd - 0.1, 2))
            if safe_call(romi.write_pid, kp, ki, kd):
                status_msg = f"Kd decreased to {kd:.2f}"
            else:
                status_msg = "I2C error writing Kd."

        elif char == ord("H"):
            base_speed = HIGH_SPEED
            if safe_call(romi.set_base_speed, base_speed):
                status_msg = f"High speed set: {base_speed}"
            else:
                status_msg = "I2C error setting high speed."

        elif char == ord("G"):
            base_speed = LOW_SPEED
            if safe_call(romi.set_base_speed, base_speed):
                status_msg = f"Low speed set: {base_speed}"
            else:
                status_msg = "I2C error setting low speed."

        elif mode == "MANUAL" and char != -1:
            target_left, target_right = current_left, current_right

            if char == curses.KEY_UP:
                target_left, target_right = 130, 130
                status_msg = "Driving forward"

            elif char == curses.KEY_DOWN:
                target_left, target_right = -130, -130
                status_msg = "Driving reverse"

            elif char == curses.KEY_LEFT:
                target_left, target_right = -100, 100
                status_msg = "Turning left"

            elif char == curses.KEY_RIGHT:
                target_left, target_right = 100, -100
                status_msg = "Turning right"

            elif char == ord(" "):
                target_left, target_right = 0, 0
                status_msg = "Motors stopped"

            if target_left != current_left or target_right != current_right:
                scaled_left, scaled_right = scale_manual_command(
                    target_left,
                    target_right
                )

                if safe_call(romi.motors, scaled_left, scaled_right):
                    current_left, current_right = target_left, target_right
                    l_cmd, r_cmd = scaled_left, scaled_right
                else:
                    status_msg = "I2C motor command failed. Retrying..."

        # Read telemetry from Arduino.
        try:
            sensors = romi.read_analog()
            time.sleep(0.03)

            encoders = romi.read_encoders()
            time.sleep(0.03)

            batt = romi.read_battery_millivolts()
            time.sleep(0.03)

            error, l_cmd, r_cmd = romi.read_p5_telemetry()
            time.sleep(0.03)

        except OSError:
            status_msg = "I2C read failed briefly. Retrying..."

            sensors = (0, 0, 0, 0, 0, 0)
            encoders = (0, 0)
            batt = (0,)
            error = 0.0
            l_cmd = 0
            r_cmd = 0

            time.sleep(0.1)

        # Project 8 marker handling only in AUTO mode.
        marker_id, marker_action = read_marker_from_redis()
        now = time.time()

        if mode == "AUTO (PID)" and marker_id in [5, 6, 7]:
            new_marker_event = (
                marker_id != last_marker_id or
                now - last_marker_time > MARKER_COOLDOWN
            )

            if new_marker_event:
                last_marker_id = marker_id
                last_marker_time = now

                if marker_id == 5:
                    if now >= ignore_stop_until:
                        marker_msg = "ID 5 STOP sign detected."
                        status_msg = "STOP sign: stopping for 2 seconds."

                        stop_until = now + STOP_TIME
                        ignore_stop_until = now + STOP_TIME + STOP_IGNORE_TIME

                        safe_call(romi.set_auto_mode, False)
                        time.sleep(0.05)
                        safe_call(romi.motors, 0, 0)
                    else:
                        marker_msg = "ID 5 STOP ignored during cooldown."

                elif marker_id == 6:
                    base_speed = HIGH_SPEED
                    marker_msg = "ID 6 HIGH SPEED sign detected."
                    status_msg = f"High speed set: {base_speed}"

                    safe_call(romi.set_base_speed, base_speed)
                    time.sleep(0.05)

                    safe_call(romi.write_pid, kp, ki, kd)
                    time.sleep(0.05)

                elif marker_id == 7:
                    base_speed = LOW_SPEED
                    marker_msg = "ID 7 LOW SPEED sign detected."
                    status_msg = f"Low speed set: {base_speed}"

                    safe_call(romi.set_base_speed, base_speed)
                    time.sleep(0.05)

                    safe_call(romi.write_pid, kp, ki, kd)
                    time.sleep(0.05)

        # Stop sign timer. Resume Arduino auto after STOP_TIME.
        if mode == "AUTO (PID)" and stop_until > 0:
            if time.time() < stop_until:
                safe_call(romi.set_auto_mode, False)
                safe_call(romi.motors, 0, 0)
                l_cmd, r_cmd = 0, 0
            else:
                stop_until = 0

                safe_call(romi.set_base_speed, base_speed)
                time.sleep(0.05)

                safe_call(romi.write_pid, kp, ki, kd)
                time.sleep(0.05)

                if safe_call(romi.set_auto_mode, True):
                    status_msg = "Stop complete. Resuming AUTO. Ignoring stop signs for 10 seconds."
                else:
                    status_msg = "I2C error resuming auto."

        elif mode == "MANUAL":
            stop_until = 0

        if is_logging and csv_writer:
            t = round(time.time() - start_time, 2)
            csv_writer.writerow([
                t,
                mode,
                encoders[0],
                encoders[1],
                round(error, 2),
                kp,
                ki,
                kd,
                base_speed,
                l_cmd,
                r_cmd,
                batt[0],
                marker_id,
            ])

        stop_cooldown_left = max(0, int(ignore_stop_until - time.time()))

        stdscr.clear()

        safe_addstr(stdscr, 1, 0, f"CURRENT MODE: {mode}", curses.A_REVERSE)
        safe_addstr(stdscr, 2, 0, f"Logging: {'ACTIVE (' + log_filename + ')' if is_logging else 'INACTIVE'}")

        safe_addstr(stdscr, 4, 0, "[m] Manual  [a] Arduino Auto/PID  [c] Calibrate  [L] Logging  [q] Quit")
        safe_addstr(stdscr, 5, 0, "Driving: Arrows (Drive), Space (Stop)")
        safe_addstr(stdscr, 6, 0, "Tune PID: [P/p] Kp +/- | [I/i] Ki +/- | [D/d] Kd +/- | [H/G] High/Low Speed")

        safe_addstr(stdscr, 8, 0, "--- Project 8 ArUco Road Signs ---")
        safe_addstr(stdscr, 9, 0, f"Marker : {marker_msg}")
        safe_addstr(stdscr, 10, 0, f"Action : {marker_action}")
        safe_addstr(stdscr, 11, 0, f"Base Speed: {base_speed}")
        safe_addstr(stdscr, 12, 0, f"Stop Timer: {'ACTIVE' if stop_until > 0 else 'INACTIVE'}")
        safe_addstr(stdscr, 13, 0, f"Stop Cooldown: {stop_cooldown_left}s")

        safe_addstr(stdscr, 15, 0, f"Battery : {batt[0]} mV")
        safe_addstr(stdscr, 16, 0, f"Sensors : {sensors}")
        safe_addstr(stdscr, 17, 0, f"Encoders: L = {encoders[0]} | R = {encoders[1]}")
        safe_addstr(stdscr, 18, 0, f"MotorCmd: L = {l_cmd} | R = {r_cmd}")
        safe_addstr(stdscr, 19, 0, f"PID Set : Kp={kp:.2f} | Ki={ki:.2f} | Kd={kd:.2f}")

        safe_addstr(stdscr, 21, 0, "--- Line Error Graph ---")
        safe_addstr(stdscr, 22, 0, f"Error: {error:6.2f} [{create_graph(error)}]")

        safe_addstr(stdscr, 24, 0, f"Status: {status_msg}")

        try:
            stdscr.refresh()
        except curses.error:
            pass

        time.sleep(0.05)

    if csv_file:
        csv_file.close()

    try:
        romi.set_auto_mode(False)
        time.sleep(0.05)
        romi.motors(0, 0)
    except OSError:
        pass


if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        pass
