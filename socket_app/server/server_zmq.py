import time
from datetime import datetime
from threading import Thread

import imutils
import cv2
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))
import definitions
from stream_zmq.server_rep import ServerHub


class Server():
    def __init__(self, address_image_hub, address_client_hub):
        self.image_hub = ServerHub(address=address_image_hub)
        self.client_hub = ServerHub(address=address_client_hub)

        self.frameDict = {}
        self.lastActive = {}
        self.lastActiveCheck = datetime.now()

        # храним ожидаемое число клиентов, период активности
        # вычисляем длительность ожидания между проверкой на активность устройства

        self.ESTIMATED_NUM_PIS = 4
        self.ACTIVE_CHECK_PERIOD = 10
        self.ACTIVE_CHECK_SECONDS = self.ESTIMATED_NUM_PIS * self.ACTIVE_CHECK_PERIOD

    def remove_not_active_camera(self):
        if (datetime.now() - self.lastActiveCheck).seconds > self.ACTIVE_CHECK_SECONDS:
            for (hostname, ts) in list(self.lastActive.items()):
                if (datetime.now() - ts).seconds > self.ACTIVE_CHECK_SECONDS:
                    print("[INFO] lost connection to {}".format(hostname))
                    self.lastActive.pop(hostname)
                    self.frameDict.pop(hostname)

                self.lastActiveCheck = datetime.now()

    def remove_not_active_client(self):
        pass

    def get_frames(self):
        while True:
            (hostname, frame) = self.image_hub.recv_image()
            self.image_hub.send_reply(b'OK')

            # notify about new connection
            if hostname not in self.lastActive.keys():
                print("[INFO] receiving data from {}...".format(hostname))

            # last time activity for device
            self.lastActive[hostname] = datetime.now()

            cv2.putText(frame, hostname, (10, 25),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

            self.frameDict[hostname] = frame

            self.remove_not_active_camera()

    def send_camera_frames(self):
        while True:
            msg = self.client_hub.recv_msg()
            time.sleep(0.02)
            if msg in self.frameDict:
                self.client_hub.send_image(self.frameDict[msg], 'OK')
            else:
                self.client_hub.send_msg(msg='camera not found')

    def send_all_cameras_frames(self):
        pass


if __name__ == "__main__":
    server = Server(address_image_hub="tcp://{}:{}".format('127.0.0.1', 9999),
                    address_client_hub="tcp://{}:{}".format('127.0.0.1', 9998))

    thread_get_frames = Thread(target=server.get_frames, args=(), daemon=False)
    thread_get_frames.start()
    thread_get_frames = Thread(target=server.send_camera_frames(), args=(), daemon=False)
    thread_get_frames.start()
