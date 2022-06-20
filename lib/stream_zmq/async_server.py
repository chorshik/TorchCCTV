import zmq
import zmq.asyncio
import zmq.auth
from lib.stream_zmq.async_event_monitor import event_monitor
from lib.stream_zmq.async_auth import auth, get_keys_dir, get_keys, gen_certificates

from pathlib import Path


class AsyncServer():
    def __init__(self, address='tcp://*:5555', path=Path(__file__).parent, key_name='server'):
        self.dir = path
        self.key_name = key_name
        self.socketType = zmq.REP
        self.context = zmq.asyncio.Context()
        self.socket = self.context.socket(self.socketType)

        self.monitor = self.socket.get_monitor_socket()

        self.auth, self.keys_dir, self.public_keys_dir, self.secret_keys_dir = auth(context=self.context, path=self.dir)
        self.load_cert()

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

    async def start_event_monitor(self):
        await event_monitor(self.monitor)

    def load_cert(self):
        server_public, server_secret = get_keys([self.keys_dir, self.public_keys_dir, self.secret_keys_dir], 'secret',
                                       self.key_name, None)

        self.socket.setsockopt(zmq.CURVE_PUBLICKEY, server_public)
        self.socket.setsockopt(zmq.CURVE_SECRETKEY, server_secret)
        self.socket.setsockopt(zmq.CURVE_SERVER, True)

    def close(self):
        self.auth.stop()
        self.socket.close()
        self.context.term()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
