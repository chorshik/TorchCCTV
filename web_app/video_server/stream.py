import time
import asyncio

from stream_zmq.client_req import Client
from stream_zmq.async_client import AsyncClient
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


class AsyncWebClient():
    def __init__(self, moc, address, cam, path, key_name, server_pub_key, hostname):
        self.client = AsyncClient(moc=moc, address=address, cam=cam,
                                  path=path, key_name=key_name, server_pub_key=server_pub_key)
        self.hostname = hostname

    async def get_frames(self):
        try:
            while True:
                frame, msg = await self.client.send_msg(msg=bytes(self.hostname, 'UTF-8'))
                await asyncio.sleep(0.02)
                if msg == 'camera not found':
                    print(f"Client close connection")
                    self.client.close()
                else:
                    ret, frame_jpg = cv2.imencode('.jpg', frame)
                    return frame_jpg

        except Exception as e:
            print(e)
            self.client.close()
