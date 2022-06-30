from datetime import datetime
import asyncio
import cv2
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))
import definitions
from stream_zmq.async_server import AsyncServer


class Server():
    def __init__(self, address_image_hub, address_client_hub):
        self.image_hub = AsyncServer(address=address_image_hub, path=Path(__file__).parent.parent, key_name='server')
        self.client_hub = AsyncServer(address=address_client_hub, path=Path(__file__).parent.parent, key_name='server2')

        self.frameDict = {}

    async def get_frame(self):
        while True:
            data = await self.image_hub.recv_image()
            await asyncio.sleep(0.002)
            frame, hostname = data['frame'], data['message']
            await self.image_hub.send_reply(b'OK')

            cv2.putText(frame, hostname, (10, 25),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

            self.frameDict[hostname] = frame

    async def send_frame(self):
        while True:
            msg = await self.client_hub.recv_msg()
            await asyncio.sleep(0.02)
            if msg in self.frameDict:
                await self.client_hub.send_image(self.frameDict[msg], 'OK')
            else:
                await self.client_hub.send_msg(msg='camera not found')

    async def remove_cam(self):
        pass

    async def remove_client(self):
        pass

    # async def start_event_monitor(self):
    #     await self.image_hub.image_hub.event_monitor()
    #     await self.client_hub.event_monitor()

    @classmethod
    async def ping(cls) -> None:
        """print dots to indicate idleness"""
        while True:
            await asyncio.sleep(0.5)
            print('.')

    def close(self):
        self.image_hub.close()
        self.client_hub.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


if __name__ == "__main__":
    async def main():
        server = Server(address_image_hub="tcp://{}:{}".format('127.0.0.1', 9999),
                        address_client_hub="tcp://{}:{}".format('127.0.0.1', 9998))

        tasks = [
            # asyncio.create_task(server.ping()),
            asyncio.create_task(server.image_hub.start_event_monitor()),
            asyncio.create_task(server.client_hub.start_event_monitor()),
            asyncio.create_task(server.get_frame()),
            asyncio.create_task(server.send_frame()),
        ]

        await asyncio.wait(tasks)

    general_loop = asyncio.get_event_loop()
    general_loop.run_until_complete(main())
    general_loop.close()

