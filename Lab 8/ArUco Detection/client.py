import cv2
import redis
import numpy as np
from time import time
import struct


PI_HOST = "ise-pi-999561.luddy.indiana.edu"
# PI_HOST = "ise-pi-975824.luddy.indiana.edu"


def fromRedis(r, key_name):
    imdata = r.hgetall(key_name)

    if not imdata or b"image" not in imdata:
        return None, None, None, None, None, None, None

    encoded = imdata[b"image"]
    frame_num = int(imdata[b"frame"])

    h, w = struct.unpack(">II", encoded[:8])

    img = np.frombuffer(
        encoded,
        dtype=np.uint8,
        offset=8
    ).reshape(h, w, 3).copy()

    server_fps = float(imdata.get(b"fps", 0.0))
    aruco_id = int(imdata.get(b"aruco_id", -1))
    aruco_action = imdata.get(b"aruco_action", b"NONE").decode()

    return frame_num, img, w, h, server_fps, aruco_id, aruco_action


if __name__ == "__main__":
    r = redis.Redis(
        host=PI_HOST,
        port=6379,
        db=0,
        password="e101class"
    )

    key = 0
    last_time = time()

    print("Waiting for camera frames from Redis...")

    while key != 27:
        frame_num, img, w, h, server_fps, aruco_id, aruco_action = fromRedis(
            r,
            "latest"
        )

        if img is None:
            print("No image found yet. Make sure server1.py is running on the Pi.")
            key = cv2.waitKey(100) & 0xFF
            continue

        current_time = time()
        delta_time = current_time - last_time
        last_time = current_time

        client_fps = 1.0 / delta_time if delta_time > 0 else 0.0

        text1 = f"Frame: {frame_num} | Resolution: {w}x{h}"
        text2 = f"Server FPS: {server_fps:.2f} | Client FPS: {client_fps:.2f}"
        text3 = f"ArUco ID: {aruco_id} | Action: {aruco_action}"

        cv2.putText(
            img,
            text1,
            (20, h - 70),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2
        )

        cv2.putText(
            img,
            text2,
            (20, h - 45),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2
        )

        cv2.putText(
            img,
            text3,
            (20, h - 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2
        )

        print(
            f"Frame: {frame_num} | Resolution: {w}x{h} | "
            f"Server FPS: {server_fps:.2f} | Client FPS: {client_fps:.2f} | "
            f"ArUco ID: {aruco_id} | Action: {aruco_action}"
        )

        cv2.imshow("Lab 8 ArUco Camera View", img)

        key = cv2.waitKey(1) & 0xFF

    cv2.destroyAllWindows()
