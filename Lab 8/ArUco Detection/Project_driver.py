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


HIGH_SPEED = 180
LOW_SPEED = 100
STOP_TIME = 2.0
MARKER_COOLDOWN = 3.0


def create_graph(error, width=40):
    center = width // 2
    normalized = int((error / 30.0) * center)
    pos = max(0, min(width - 1, center + normalized))

    graph = ["-"] * width
    graph[center] = "|"
    graph[pos] = "O"
    return "".join(graph)


def safe_call(func, *args):
    try:
        func(*args)
        return True
    except OSError:
        return False


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

    kp, ki, kd = 1.7, 0.3, 1.2
    base_speed = HIGH_SPEED

    current_left, current_right = 0, 0

    sensors = (0, 0, 0, 0, 0, 0)
    encoders = (0, 0)
    batt = (0,)
    error = 0.0
    l_cmd = 0
    r_cmd = 0

    stop_until = 0
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

        status_msg = "Startup complete."

    except OSError:
        status_msg = "Startup I2C error. Check Romi power/reset, then continue."

    while True:
        char = stdscr.getch()

        if char == ord("q"):
            break

        elif char == ord("m"):
            mode = "MANUAL"

            if safe_call(romi.set_auto_mode, False):
                time.sleep(0.05)
                safe_call(romi.motors, 0, 0)
                current_left, current_right = 0, 0
                status_msg = "Switched to Manual Control."
            else:
                status_msg = "I2C error switching to manual."

        elif char == ord("a"):
            mode = "AUTO (PID)"

            safe_call(romi.set_base_speed, base_speed)

            if safe_call(romi.set_auto_mode, True):
                status_msg = "AUTO mode running."
            else:
                status_msg = "I2C error switching to auto."

        elif char == ord("c"):
            status_msg = "Calibrating..."
            stdscr.addstr(18, 0, f"Status: {status_msg}                   ")
            stdscr.refresh()

            try:
                romi.trigger_calibration()
                time.sleep(0.1)

                while romi.check_if_calibrating():
                    time.sleep(0.5)

                status_msg = "Calibration complete."

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

            elif char == ord(" "):
                target_left, target_right = 0, 0
                status_msg = "Motors stopped"

            if target_left != current_left or target_right != current_right:
                if safe_call(romi.motors, target_left, target_right):
                    current_left, current_right = target_left, target_right
                else:
                    status_msg = "I2C motor command failed. Retrying..."

        # Project 8 marker handling
        marker_id, marker_action = read_marker_from_redis()
        now = time.time()

        if marker_id in [5, 6, 7]:
            new_marker_event = (
                marker_id != last_marker_id or
                now - last_marker_time > MARKER_COOLDOWN
            )

            if new_marker_event:
                last_marker_id = marker_id
                last_marker_time = now

                if marker_id == 5:
                    marker_msg = "ID 5 STOP sign detected."
                    status_msg = "STOP sign: stopping for 2 seconds."
                    stop_until = now + STOP_TIME

                    safe_call(romi.set_auto_mode, False)
                    time.sleep(0.05)
                    safe_call(romi.motors, 0, 0)

                elif marker_id == 6:
                    base_speed = HIGH_SPEED
                    marker_msg = "ID 6 HIGH SPEED sign detected."
                    status_msg = f"High speed set: {base_speed}"

                    safe_call(romi.set_base_speed, base_speed)

                elif marker_id == 7:
                    base_speed = LOW_SPEED
                    marker_msg = "ID 7 LOW SPEED sign detected."
                    status_msg = f"Low speed set: {base_speed}"

                    safe_call(romi.set_base_speed, base_speed)

        # Resume after stop sign if the robot was in AUTO mode
        if stop_until > 0:
            if time.time() < stop_until:
                safe_call(romi.set_auto_mode, False)
                safe_call(romi.motors, 0, 0)
            else:
                stop_until = 0
                if mode == "AUTO (PID)":
                    safe_call(romi.set_base_speed, base_speed)
                    time.sleep(0.05)
                    safe_call(romi.set_auto_mode, True)
                    status_msg = "Stop complete. Resuming AUTO mode."

        # Protected I2C telemetry reads
        try:
            sensors = romi.read_analog()
            time.sleep(0.05)

            encoders = romi.read_encoders()
            time.sleep(0.05)

            batt = romi.read_battery_millivolts()
            time.sleep(0.05)

            error, l_cmd, r_cmd = romi.read_p5_telemetry()
            time.sleep(0.05)

        except OSError:
            status_msg = "I2C read failed briefly. Retrying..."

            sensors = (0, 0, 0, 0, 0, 0)
            encoders = (0, 0)
            batt = (0,)
            error = 0.0
            l_cmd = 0
            r_cmd = 0

            time.sleep(0.1)

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

        stdscr.clear()

        stdscr.addstr(1, 0, f"CURRENT MODE: {mode}", curses.A_REVERSE)
        stdscr.addstr(2, 0, f"Logging: {'ACTIVE (' + log_filename + ')' if is_logging else 'INACTIVE'}")

        stdscr.addstr(4, 0, "[m] Manual  [a] Auto/PID  [c] Calibrate  [L] Toggle Logging  [q] Quit")
        stdscr.addstr(5, 0, "Driving: Arrows (Drive), Space (Stop)")
        stdscr.addstr(6, 0, "Tune PID: [P/p] Kp +/- | [I/i] Ki +/- | [D/d] Kd +/-")

        stdscr.addstr(8, 0, "--- Project 8 ArUco Road Signs ---")
        stdscr.addstr(9, 0, f"Marker : {marker_msg}")
        stdscr.addstr(10, 0, f"Action : {marker_action}")
        stdscr.addstr(11, 0, f"Base Speed: {base_speed}")
        stdscr.addstr(12, 0, f"Stop Timer: {'ACTIVE' if stop_until > 0 else 'INACTIVE'}")

        stdscr.addstr(14, 0, f"Battery : {batt[0]} mV")
        stdscr.addstr(15, 0, f"Sensors : {sensors}")
        stdscr.addstr(16, 0, f"Encoders: L = {encoders[0]} | R = {encoders[1]}")
        stdscr.addstr(17, 0, f"MotorCmd: L = {l_cmd} | R = {r_cmd}")
        stdscr.addstr(18, 0, f"PID Set : Kp={kp:.2f} | Ki={ki:.2f} | Kd={kd:.2f}")

        stdscr.addstr(20, 0, "--- Line Error Graph ---")
        stdscr.addstr(21, 0, f"Error: {error:6.2f} [{create_graph(error)}]")

        stdscr.addstr(23, 0, f"Status: {status_msg}")
        stdscr.refresh()

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
