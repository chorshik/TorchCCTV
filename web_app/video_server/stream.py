import time

from stream_zmq.client_req import Client
import cv2


class WebClient():
    def __init__(self, hostname):
        self.client = Client(moc=True, address="tcp://{}:{}".format('127.0.0.1', 9998), num='1', cam=False)
        self.hostname = hostname

    def get_frame(self):
        try:
            msg, frame = self.client.send_msg(msg=bytes(self.hostname, 'UTF-8'))
            time.sleep(0.02)
            if frame is None:
                return None
            ret, frame_jpg = cv2.imencode('.jpg', frame)
            return frame_jpg.tobytes()

        except Exception as e:
            pass
