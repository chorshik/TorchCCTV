import zmq
import zmq.asyncio
import socket
import random


class AsyncClient():
    def __init__(self, moc=False, address='tcp://127.0.0.1:5555', num='1', cam=False):
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
        self.socket.connect(self.address)
        print(f"CONNECT TO SERVER: {self.address}")

    async def send_image(self, image, msg):
        data = dict(frame=image, message=msg)
        await self.socket.send_pyobj(data)
        hub_reply = await self.socket.recv()
        # print(hub_reply)
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

    async def reset_connection(self):
        self.socket.close()
        self.init_reqrep_socket()

    def close(self):
        self.socket.close()
        self.context.term()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

