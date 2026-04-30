import curses
import time
import csv
from a_star import AStar


def create_graph(error, width=40):
    center = width // 2
    normalized = int((error / 30.0) * center)
    pos = max(0, min(width - 1, center + normalized))

    graph = ["-"] * width
    graph[center] = "|"
    graph[pos] = "O"
    return "".join(graph)


def main(stdscr):
    romi = AStar()
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.keypad(True)
    stdscr.timeout(100)

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

        if char == ord("q"):
            break

        elif char == ord("m"):
            mode = "MANUAL"
            romi.set_auto_mode(False)
            romi.motors(0, 0)
            current_left, current_right = 0, 0
            status_msg = "Switched to Manual Control."

        elif char == ord("a"):
            mode = "AUTO (PID)"
            romi.set_auto_mode(True)
            status_msg = "PID loop running. Calibrate first."

        elif char == ord("c"):
            status_msg = "Calibrating..."
            stdscr.addstr(18, 0, f"Status: {status_msg}                   ")
            stdscr.refresh()
            romi.trigger_calibration()
            while romi.check_if_calibrating():
                time.sleep(0.5)
            status_msg = "Calibration complete."

        elif char == ord("L") or char == ord("l"):
            if is_logging:
                is_logging = False
                if csv_file:
                    csv_file.close()
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
                    "left_cmd",
                    "right_cmd",
                    "battery_mv",
                ])
                is_logging = True
                start_time = time.time()
                status_msg = f"Logging started: {log_filename}"

        elif char == ord("P"):
            kp = round(kp + 0.1, 2)
            romi.write_pid(kp, ki, kd)

        elif char == ord("p"):
            kp = max(0.0, round(kp - 0.1, 2))
            romi.write_pid(kp, ki, kd)

        elif char == ord("I"):
            ki = round(ki + 0.05, 2)
            romi.write_pid(kp, ki, kd)

        elif char == ord("i"):
            ki = max(0.0, round(ki - 0.05, 2))
            romi.write_pid(kp, ki, kd)

        elif char == ord("D"):
            kd = round(kd + 0.1, 2)
            romi.write_pid(kp, ki, kd)

        elif char == ord("d"):
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
            elif char == ord(" "):
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
                t,
                mode,
                encoders[0],
                encoders[1],
                round(error, 2),
                kp,
                ki,
                kd,
                l_cmd,
                r_cmd,
                batt[0],
            ])

        stdscr.clear()

        stdscr.addstr(1, 0, f"CURRENT MODE: {mode}", curses.A_REVERSE)
        stdscr.addstr(2, 0, f"Logging: {'ACTIVE (' + log_filename + ')' if is_logging else 'INACTIVE'}")

        stdscr.addstr(4, 0, "[m] Manual  [a] Auto/PID  [c] Calibrate  [L] Toggle Logging  [q] Quit")
        stdscr.addstr(5, 0, "Driving: Arrows (Drive), Space (Stop)")
        stdscr.addstr(6, 0, "Tune PID: [P/p] Kp +/- | [I/i] Ki +/- | [D/d] Kd +/-")

        stdscr.addstr(9, 0, f"Battery : {batt[0]} mV")
        stdscr.addstr(10, 0, f"Sensors : {sensors}")
        stdscr.addstr(11, 0, f"Encoders: L = {encoders[0]} | R = {encoders[1]}")
        stdscr.addstr(12, 0, f"MotorCmd: L = {l_cmd} | R = {r_cmd}")
        stdscr.addstr(13, 0, f"PID Set : Kp={kp:.2f} | Ki={ki:.2f} | Kd={kd:.2f}")

        stdscr.addstr(15, 0, "--- Line Error Graph ---")
        stdscr.addstr(16, 0, f"Error: {error:6.2f} [{create_graph(error)}]")

        stdscr.addstr(18, 0, f"Status: {status_msg}")
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
