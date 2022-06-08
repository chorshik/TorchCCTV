import errno
import time
import cv2
import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))
import definitions
from stream_zmq.client_req import Client
file = './video_plug.mp4'


def send_frame(camera, capture, loop, i):
    try:
        while True:
            ret, frame = capture.read()
            time.sleep(0.03)
            if ret:
                frame = cv2.resize(frame, (640, 480))
                camera.send_image(camera.hostname, frame)
            else:
                if loop:
                    capture = cv2.VideoCapture(file)
                else:
                    break

    except Exception as e:
        print(e)
        print(f"DISCONNECTED FROM SERVER")
        camera.close()

        # i += 1
        # if i > 5:
        #     camera.close()
        # else:
        #     camera.reset_connection()
        #     send_frame(camera, capture, loop, i)


if __name__ == "__main__":
    camera = Client(moc=True, address="tcp://{}:{}".format('127.0.0.1', 9999), num='1', cam=True)
    i = 0
    camera_addr = 0
    loop = False
    if camera.moc:
        if os.path.isfile(file):
            capture = cv2.VideoCapture(file)
            loop = True
        else:
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), file)
    else:
        capture = cv2.VideoCapture(camera_addr)

    time.sleep(0.5)

    send_frame(camera, capture, loop, i)


