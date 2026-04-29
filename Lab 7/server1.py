from picamera2 import Picamera2
import cv2
import redis
import time
import struct
import numpy as np

r = redis.Redis(
        host = 'ise-pi-975824.luddy.indiana.edu',
        port = 6379,
        db = 0,
        password = 'e101class'
)

def toRedis(r, a, n, fnum):
    h, w = a.shape[:2]

    shape = struct.pack('>II', h, w)
    encoded = shape + a.tobytes()

    r.hmset(n, {
        'frame': fnum,
        'image': encoded
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

    key = 0
    count = 0

    time.sleep(2)

    while key != 27:
        img = picam2.capture_array()

        if img is None or img.size == 0:
            print("Failed to capture frame")
            continue

        toRedis(r, img, 'latest', count)

        count += 1
        print(count)

        key = cv2.waitKey(1) & 0xFF
