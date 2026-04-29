from picamera2 import Picamera2
import cv2
import redis
import time
import struct
import sys


# Redis is running on the Pi, so use localhost on the Pi
r = redis.Redis(
    host="localhost",
    port=6379,
    db=0,
    password="e101class"
)


def toRedis(r, img, key_name, frame_num, fps):
    h, w = img.shape[:2]

    shape = struct.pack(">II", h, w)
    encoded = shape + img.tobytes()

    r.hset(key_name, mapping={
        "frame": frame_num,
        "image": encoded,
        "width": w,
        "height": h,
        "fps": fps
    })


if __name__ == "__main__":
    # Default resolution
    frameWidth = 640
    frameHeight = 480

    # Optional command-line resolution:
    # python3 server1.py 320 240
    if len(sys.argv) == 3:
        frameWidth = int(sys.argv[1])
        frameHeight = int(sys.argv[2])

    print(f"Starting camera at {frameWidth}x{frameHeight}")

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

        # Convert from RGB to BGR so OpenCV displays colors correctly
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

        current_time = time.time()
        delta_time = current_time - last_time
        last_time = current_time

        fps = 1.0 / delta_time if delta_time > 0 else 0.0

        toRedis(r, img, "latest", count, fps)

        print(f"Frame: {count} | Resolution: {frameWidth}x{frameHeight} | FPS: {fps:.2f}")

        count += 1
