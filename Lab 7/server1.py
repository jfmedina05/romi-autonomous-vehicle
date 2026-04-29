from picamera2 import Picamera2
import cv2
import redis
import time
import struct
import numpy as np

r = redis.Redis(
    host='ise-pi-999561.luddy.indiana.edu',
    port=6379,
    db=0,
    password='e101class'
)

def get_aruco_tools():
    dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)

    try:
        parameters = cv2.aruco.DetectorParameters()
        detector = cv2.aruco.ArucoDetector(dictionary, parameters)
        return dictionary, parameters, detector
    except AttributeError:
        parameters = cv2.aruco.DetectorParameters_create()
        return dictionary, parameters, None


def detect_aruco(img, detector, dictionary, parameters):
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

    if detector is not None:
        corners, ids, rejected = detector.detectMarkers(gray)
    else:
        corners, ids, rejected = cv2.aruco.detectMarkers(
            gray,
            dictionary,
            parameters=parameters
        )

    marker_detected = ids is not None and len(ids) > 0

    marker_id = -1
    marker_x = -1
    marker_y = -1
    error = 0
    command = "SEARCH"

    if marker_detected:
        cv2.aruco.drawDetectedMarkers(img, corners, ids, borderColor=(0, 255, 0))

        first_marker = corners[0][0]
        marker_id = int(ids[0][0])

        marker_x = int(np.mean(first_marker[:, 0]))
        marker_y = int(np.mean(first_marker[:, 1]))

        frame_center = img.shape[1] // 2
        error = marker_x - frame_center

        cv2.circle(img, (marker_x, marker_y), 8, (255, 0, 0), -1)

        if error < -60:
            command = "LEFT"
        elif error > 60:
            command = "RIGHT"
        else:
            command = "FORWARD"

        cv2.putText(
            img,
            f"ID: {marker_id} CMD: {command} ERR: {error}",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 255),
            2
        )
    else:
        cv2.putText(
            img,
            "NO ARUCO MARKER",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 255),
            2
        )

    return marker_detected, marker_id, marker_x, marker_y, error, command


def toRedis(r, img, n, fnum, detected, marker_id, marker_x, marker_y, error, command):
    h, w = img.shape[:2]

    shape = struct.pack('>II', h, w)
    encoded = shape + img.tobytes()

    r.hset(n, mapping={
        'frame': fnum,
        'image': encoded,
        'aruco_detected': int(detected),
        'aruco_id': marker_id,
        'aruco_x': marker_x,
        'aruco_y': marker_y,
        'aruco_error': error,
        'aruco_command': command
    })


if __name__ == '__main__':
    frameWidth = 640
    frameHeight = 480

    dictionary, parameters, detector = get_aruco_tools()

    picam2 = Picamera2()

    config = picam2.create_preview_configuration(
        main={
            "size": (frameWidth, frameHeight),
            "format": "RGB888"
        }
    )

    picam2.configure(config)
    picam2.start()

    count = 0
    time.sleep(2)

    while True:
        img = picam2.capture_array()

        if img is None or img.size == 0:
            print("Failed to capture frame")
            continue

        detected, marker_id, marker_x, marker_y, error, command = detect_aruco(
            img,
            detector,
            dictionary,
            parameters
        )

        toRedis(
            r,
            img,
            'latest',
            count,
            detected,
            marker_id,
            marker_x,
            marker_y,
            error,
            command
        )

        print(
            f"Frame {count} | Detected: {detected} | "
            f"ID: {marker_id} | x={marker_x} | error={error} | command={command}"
        )

        count += 1
