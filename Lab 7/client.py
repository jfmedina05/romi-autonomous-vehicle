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

    img = np.frombuffer(
        encoded,
        dtype=np.uint8,
        offset=8
    ).reshape(h, w, 3).copy()

    detected = int(imdata.get(b'aruco_detected', 0))
    marker_id = int(imdata.get(b'aruco_id', -1))
    marker_x = int(imdata.get(b'aruco_x', -1))
    marker_y = int(imdata.get(b'aruco_y', -1))
    error = int(imdata.get(b'aruco_error', 0))
    command = imdata.get(b'aruco_command', b'SEARCH').decode()

    return fnum, img, detected, marker_id, marker_x, marker_y, error, command


if __name__ == '__main__':
    r = redis.Redis(
        host='ise-pi-999561.luddy.indiana.edu',
        port=6379,
        db=0,
        password='e101class'
    )

    key = 0
    last_time = time()

    while key != 27:
        current_time = time()
        delta_time = current_time - last_time
        last_time = current_time

        fnum, img, detected, marker_id, marker_x, marker_y, error, command = fromRedis(
            r,
            'latest'
        )

        fps = 1 / delta_time if delta_time > 0 else 0

        text = (
            f"Frame: {fnum} | FPS: {fps:.2f} | "
            f"Aruco: {detected} | ID: {marker_id} | Command: {command}"
        )

        cv2.putText(
            img,
            text,
            (20, img.shape[0] - 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2
        )

        cv2.imshow('Romi ArUco Video Driver', img)

        print(text)

        key = cv2.waitKey(1) & 0xFF

    cv2.destroyAllWindows()
