import socket

import cv2
import sys
import asyncio
import argparse
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))
import definitions
from stream_zmq.async_client import AsyncClient


async def get_frames(client, request):
    try:
        while True:
            frame, msg = await client.send_msg(msg=bytes(request, 'UTF-8'))
            await asyncio.sleep(0.02)
            if msg == 'camera not found':
                # print(msg)
                print(f"Client close connection")
                client.close()
            else:
                cv2.imshow(f"Client: {client.hostname} host: {request} ", frame)
                key = cv2.waitKey(1) & 0xFF
                if key == ord("q"):
                    break

        cv2.destroyAllWindows()

    except Exception as e:
        print(f'ErrorAsyncClient:{e}')
        client.close()


if __name__ == "__main__":
    async def main():
        parser = argparse.ArgumentParser()
        parser.add_argument("-n", "--num", type=int)
        parser.add_argument("-k", "--key", type=str)
        args = parser.parse_args()

        client = AsyncClient(moc=True, address="tcp://{}:{}".format('127.0.0.1', 9998), num=str(args.num), cam=False,
                             path=Path(__file__).parent.parent, key_name=args.key, server_pub_key='server2')
        request = socket.gethostname() + str(args.num)

        tasks = [
            asyncio.create_task(client.start_event_monitor()),
            asyncio.create_task(get_frames(client, request)),
        ]

        await asyncio.wait(tasks)


    general_loop = asyncio.new_event_loop()
    general_loop.run_until_complete(main())
    general_loop.close()


