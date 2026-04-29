import cv2
import redis
import numpy as np
from time import time
import struct

def fromRedis(r, n):
    imdata = r.hgetall(n)

<<<<<<< HEAD
    endcoded = imdata[b'image']
=======
    encoded = imdata[b'image']
>>>>>>> e2d84a6dde96565a65a6a15578fe3f34409fc7a9
    fnum = imdata[b'frame']

    h, w = struct.unpack('>II', encoded[:8])

    a = np.frombuffer(encoded, dtype=np.uint8, offset=8).reshape(h, w, 3)

    return (fnum, a)

<<<<<<< HEAD
if __name__ == '__main__':
    r = redis.Redis(
            host = 'ise-pi-975824.luddy.indiana.edu',
            port = 6379,
            db = 0,
            password = 'e101class'
=======

if __name__ == '__main__':
    r = redis.Redis(
        host = 'ise-pi-999561.luddy.indiana.edu',#'ise-pi-975824.luddy.indiana.edu',
        port = 6379,
        db = 0,
        password = 'e101class'
>>>>>>> e2d84a6dde96565a65a6a15578fe3f34409fc7a9
    )

    key = 0
    last_time = 0

    while key != 27:
        time_temp = time()
<<<<<<< HEAD
        delta_time = int((time_temp = last_time) * 1000)
=======
        delta_time = int((time_temp - last_time) * 1000)
>>>>>>> e2d84a6dde96565a65a6a15578fe3f34409fc7a9
        last_time = time_temp

        fnum, img = fromRedis(r, 'latest')

        print(f"read image with shape {img.shape} frame={fnum} delta={delta_time} ms frame rate={int(1/(delta_time/1000))} fps")

        cv2.imshow('image', img)

        key = cv2.waitKey(1) & 0xFF
