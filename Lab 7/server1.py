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

def detect_line(img):
    """
    Detects a dark line in the lower part of the camera image.
    Returns: line_detected, cx, cy, mask
    """
    h, w = img.shape[:2]

    # Use bottom half of the image because the line is on the floor
    roi = img[h // 2:h, :]

    gray = cv2.cvtColor(roi, cv2.COLOR_RGB2GRAY)

    # Detect dark line
    _, mask = cv2.threshold(gray, 80, 255, cv2.THRESH_BINARY_INV)

    # Remove noise
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.erode(mask, kernel, iterations=1)
    mask = cv2.dilate(mask, kernel, iterations=2)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if len(contours) == 0:
        return False, -1, -1, mask

    largest = max(contours, key=cv2.contourArea)
    area = cv2.contourArea(largest)

    if area < 500:
        return False, -1, -1, mask

    M = cv2.moments(largest)

    if M["m00"] == 0:
        return False, -1, -1, mask

    cx = int(M["m10"] / M["m00"])
    cy = int(M["m01"] / M["m00"]) + h // 2

    return True, cx, cy, mask


def toRedis(r, a, n, fnum, line_detected, cx, cy):
    h, w = a.shape[:2]

    shape = struct.pack('>II', h, w)
    encoded = shape + a.tobytes()

    r.hset(n, mapping={
        'frame': fnum,
        'image': encoded,
        'line_detected': int(line_detected),
        'line_x': cx,
        'line_y': cy
    })


if __name__ == '__main__':
    frameWidth = 640
    frameHeight = 480

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

        line_detected, cx, cy, mask = detect_line(img)

        # Draw detection overlay
        if line_detected:
            cv2.circle(img, (cx, cy), 10, (255, 0, 0), -1)
            cv2.putText(img, "LINE DETECTED", (20, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
        else:
            cv2.putText(img, "NO LINE", (20, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        toRedis(r, img, 'latest', count, line_detected, cx, cy)

        count += 1
        print(f"Frame {count} | Line detected: {line_detected} | x={cx}, y={cy}")
