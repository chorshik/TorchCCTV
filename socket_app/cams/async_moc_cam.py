import errno
import cv2
import os
import sys
import asyncio
import argparse

from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))
import definitions
from stream_zmq.async_client import AsyncClient

file = './video_plug.mp4'


async def send_frame(camera, camera_addr, loop_cam):
    loop = asyncio.get_event_loop()

    if camera.moc:
        if os.path.isfile(file):
            capture = cv2.VideoCapture(file)
            loop_cam = True
        else:
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), file)
    else:
        capture = cv2.VideoCapture(camera_addr)

    try:
        while True:
            ret, frame = await loop.run_in_executor(None, capture.read)
            await asyncio.sleep(0.02)
            if ret:
                resized_frame = await loop.run_in_executor(None, cv2.resize, frame, (640, 480))
                await camera.send_image(resized_frame, camera.hostname)
            else:
                if loop_cam:
                    capture = cv2.VideoCapture(file)
                else:
                    break

    except Exception as e:
        print(e)
        print(f"DISCONNECTED FROM SERVER")
        camera.close()


if __name__ == "__main__":
    async def main() -> None:
        parser = argparse.ArgumentParser()
        parser.add_argument("-n", "--num", type=int)
        parser.add_argument("-k", "--key", type=str)
        args = parser.parse_args()

        camera = AsyncClient(moc=True, address="tcp://{}:{}".format('127.0.0.1', 9999), num=str(args.num), cam=True,
                             path=Path(__file__).parent.parent, key_name=args.key, server_pub_key='server')

        camera_addr = 0
        loop_cam = False

        tasks = [
            # asyncio.create_task(camera.start_event_monitor()),
            asyncio.create_task(send_frame(camera, camera_addr, loop_cam)),
        ]

        await asyncio.wait(tasks)


    general_loop = asyncio.get_event_loop()
    general_loop.run_until_complete(main())
    general_loop.close()
