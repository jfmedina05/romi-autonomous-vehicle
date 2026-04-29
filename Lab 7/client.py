import cv2
import redis
import numpy as np
from time import time
import struct

def fromRedis(r, n):
    imdata = r.hgetall(n)

    encoded = imdata[b'image']
    fnum = int(imdata[b'frame'])

    h, w = struct.unpack('>II', encoded[:8])

    # .copy() makes the image writable for cv2.putText()
    img = np.frombuffer(encoded, dtype=np.uint8, offset=8).reshape(h, w, 3).copy()

    line_detected = int(imdata.get(b'line_detected', 0))
    line_x = int(imdata.get(b'line_x', -1))
    line_y = int(imdata.get(b'line_y', -1))

    return fnum, img, line_detected, line_x, line_y


if __name__ == '__main__':
    r = redis.Redis(
        host='ise-pi-999561.luddy.indiana.edu',
        port=6379,
        db=0,
        password='e101class'
    )

    key = 0
    last_time = time()
    mode = "MANUAL"

    while key != 27:
        current_time = time()
        delta_time = current_time - last_time
        last_time = current_time

        fnum, img, line_detected, line_x, line_y = fromRedis(r, 'latest')

        fps = 1 / delta_time if delta_time > 0 else 0

        if line_detected:
            mode = "AUTO"
            r.set("mode", "AUTO")
        else:
            r.set("mode", mode)

        text = f"Frame: {fnum} | FPS: {fps:.2f} | Mode: {mode} | Line: {line_detected}"

        cv2.putText(
            img,
            text,
            (20, img.shape[0] - 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2
        )

        cv2.imshow('Romi Video Driver', img)

        print(text)

        key = cv2.waitKey(1) & 0xFF

        if key == ord('m'):
            mode = "MANUAL"
            r.set("mode", "MANUAL")

        elif key == ord('a'):
            mode = "AUTO"
            r.set("mode", "AUTO")

    cv2.destroyAllWindows()
