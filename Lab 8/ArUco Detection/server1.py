from picamera2 import Picamera2
import cv2
import redis
import time
import struct
import sys
import numpy as np


# Server runs on the Pi, so Redis should be localhost
r = redis.Redis(
    host= "localhost",
    port=6379,
    db=0,
    password="e101class"
)


# Use the 4x4 dictionary.
# If your marker generator used a different one, change this line.
ARUCO_DICT_TYPE = cv2.aruco.DICT_4X4_50

# Set to True if your camera is upside down
FLIP_IMAGE = True


def setup_aruco_detector():
    aruco_dict = cv2.aruco.getPredefinedDictionary(ARUCO_DICT_TYPE)

    # New OpenCV versions
    if hasattr(cv2.aruco, "ArucoDetector"):
        parameters = cv2.aruco.DetectorParameters()
        detector = cv2.aruco.ArucoDetector(aruco_dict, parameters)
        return aruco_dict, parameters, detector

    # Older OpenCV versions
    parameters = cv2.aruco.DetectorParameters_create()
    detector = None
    return aruco_dict, parameters, detector


def detect_aruco_markers(img, aruco_dict, parameters, detector):
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

    if detector is not None:
        corners, ids, rejected = detector.detectMarkers(gray)
    else:
        corners, ids, rejected = cv2.aruco.detectMarkers(
            gray,
            aruco_dict,
            parameters=parameters
        )

    detected_id = -1
    action = "NONE"

    if ids is not None and len(ids) > 0:
        # Draw box around detected marker.
        # Since the image is RGB, this color is blue in RGB.
        cv2.aruco.drawDetectedMarkers(
            image=img,
            corners=corners,
            ids=ids,
            borderColor=(0, 0, 255)
        )

        detected_id = int(ids[0][0])

        if detected_id == 5:
            action = "STOP"
        elif detected_id == 6:
            action = "HIGH_SPEED"
        elif detected_id == 7:
            action = "LOW_SPEED"
        else:
            action = "UNKNOWN"

        cv2.putText(
            img,
            f"ID: {detected_id} | ACTION: {action}",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 255),
            2
        )
    else:
        cv2.putText(
            img,
            "No ArUco marker detected",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 255),
            2
        )

    return detected_id, action


def toRedis(r, img, key_name, frame_num, fps, detected_id, action):
    h, w = img.shape[:2]

    shape = struct.pack(">II", h, w)
    encoded = shape + img.tobytes()

    r.hset(key_name, mapping={
        "frame": frame_num,
        "image": encoded,
        "width": w,
        "height": h,
        "fps": fps,
        "aruco_id": detected_id,
        "aruco_action": action
    })


if __name__ == "__main__":
    frameWidth = 320
    frameHeight = 240

    # Optional resolution command:
    # python3 server1.py 320 240
    if len(sys.argv) == 3:
        frameWidth = int(sys.argv[1])
        frameHeight = int(sys.argv[2])

    print(f"Starting camera at {frameWidth}x{frameHeight}")

    aruco_dict, parameters, detector = setup_aruco_detector()

    picam2 = Picamera2()

    config = picam2.create_preview_configuration(
        main={
            "size": (frameWidth, frameHeight),
            "format": "RGB888"
        }
    )

    picam2.configure(config)
    picam2.start()

    time.sleep(2)

    count = 0
    last_time = time.time()

    while True:
        img = picam2.capture_array()

        if img is None or img.size == 0:
            print("Failed to capture frame")
            continue

        # Flip image if the camera is mounted upside down
        if FLIP_IMAGE:
            img = cv2.flip(img, -1)

        detected_id, action = detect_aruco_markers(
            img,
            aruco_dict,
            parameters,
            detector
        )

        current_time = time.time()
        delta_time = current_time - last_time
        last_time = current_time

        fps = 1.0 / delta_time if delta_time > 0 else 0.0

        toRedis(
            r,
            img,
            "latest",
            count,
            fps,
            detected_id,
            action
        )

        print(
            f"Frame: {count} | Resolution: {frameWidth}x{frameHeight} | "
            f"FPS: {fps:.2f} | ArUco ID: {detected_id} | Action: {action}"
        )

        count += 1
