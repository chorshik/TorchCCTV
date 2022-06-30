import sys

import zmq
import zmq.asyncio
import socket
import random

from lib.stream_zmq.async_event_monitor import event_monitor
from lib.stream_zmq.async_auth import get_keys_dir, get_keys

from pathlib import Path


class AsyncClient():
    def __init__(self, moc=False, address='tcp://127.0.0.1:5555', num='1', cam=False, path=Path(__file__).parent,
                 key_name='client', server_pub_key='server'):
        self.dir = path
        self.key_name = key_name
        self.server_pub_key = server_pub_key
        self.address = address
        self.moc = moc
        if moc and not cam:
            self.hostname = 'client' + '_' + socket.gethostname() + '_' + str(random.randint(1, 10000))
        elif moc and cam:
            self.hostname = socket.gethostname() + num
        else:
            self.hostname = socket.gethostname()

        self.init_reqrep_socket()

    def init_reqrep_socket(self):
        self.socketType = zmq.REQ
        self.context = zmq.asyncio.Context()
        self.socket = self.context.socket(self.socketType)
        self.socket.setsockopt(zmq.RCVTIMEO, 1000)  # milliseconds
        self.socket.setsockopt(zmq.LINGER, -1)
        self.monitor = self.socket.get_monitor_socket()
        # load cert
        self.load_cert()
        self.socket.connect(self.address)
        print(f"CONNECT TO SERVER: {self.address}")

    async def send_image(self, image, msg):
        data = dict(frame=image, message=msg)
        await self.socket.send_pyobj(data)
        hub_reply = await self.socket.recv()
        return hub_reply

    async def send_msg(self, msg):
        try:
            await self.socket.send(msg)
            data = await self.socket.recv_pyobj()
            return data['frame'], data['message']
        except Exception as e:
            await self.socket.send(msg)
            message = await self.socket.recv(copy=False)
            return None, message.bytes.decode('UTF-8')

    async def start_event_monitor(self):
        await event_monitor(self.monitor)

    def load_cert(self):
        self.keys_dir, self.public_keys_dir, self.secret_keys_dir = get_keys_dir(self.dir)
        client_public, client_secret = get_keys([self.keys_dir, self.public_keys_dir, self.secret_keys_dir], 'secret',
                                                self.key_name, None)

        # print(client_public, '\n', client_secret)

        self.socket.setsockopt(zmq.CURVE_PUBLICKEY, client_public)
        self.socket.setsockopt(zmq.CURVE_SECRETKEY, client_secret)

        server_public, _ = get_keys([self.keys_dir, self.public_keys_dir, self.secret_keys_dir], 'public',
                                                self.key_name, self.server_pub_key)

        self.socket.setsockopt(zmq.CURVE_SERVERKEY, server_public)

    async def reset_connection(self):
        self.socket.close()
        self.init_reqrep_socket()

    def close(self):
        print(f'Client close connection')
        self.socket.close()
        self.context.destroy()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

