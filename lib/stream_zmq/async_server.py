import zmq
import zmq.asyncio
from zmq.utils.monitor import parse_monitor_message
from lib.stream_zmq.utils import line

import asyncio
import time
from typing import Any, Dict


class AsyncServer():
    def __init__(self, address='tcp://*:5555'):
        self.socketType = zmq.REP
        self.context = zmq.asyncio.Context()
        self.socket = self.context.socket(self.socketType)
        self.monitor = self.socket.get_monitor_socket()
        self.socket.bind(address)

    async def recv_image(self):
        data = await self.socket.recv_pyobj()
        return data

    async def recv_msg(self):
        msg = await self.socket.recv()
        return msg.decode('UTF-8')

    async def send_reply(self, reply_message=b'OK'):
        await self.socket.send(reply_message)

    async def send_image(self, img, msg):
        data = dict(frame=img, message=msg)
        await self.socket.send_pyobj(data)

    async def send_msg(self, msg):
        await self.socket.send(bytes(msg, 'UTF-8'))

    async def event_monitor(self):
        monitor = self.socket.get_monitor_socket()

        EVENT_MAP = {}
        # print("Event names:")
        for name in dir(zmq):
            if name.startswith('EVENT_'):
                value = getattr(zmq, name)
                # print("%21s : %4i" % (name, value))
                EVENT_MAP[value] = name

        print("\n")

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        async def run_loop() -> None:
            while True:
                try:
                    while monitor.poll():
                        evt: Dict[str, Any] = {}
                        msg = await self.monitor.recv_multipart(flags=0)
                        mon_evt = parse_monitor_message(msg)
                        evt.update(mon_evt)
                        evt['description'] = EVENT_MAP[evt['event']]
                        print(f"Event: {evt}")
                        line()
                        if evt['event'] == zmq.EVENT_MONITOR_STOPPED:
                            break
                except RuntimeError as e:
                    print(e)
                    time.sleep(1)

            monitor.close()
            print()
            print("event monitor thread done!")

        asyncio.ensure_future(run_loop())

    def close(self):
        self.socket.close()
        self.context.term()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
