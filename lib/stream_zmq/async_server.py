import zmq
import zmq.asyncio


class AsyncServer():
    def __init__(self, address='tcp://*:5555'):
        self.socketType = zmq.REP
        self.context = zmq.asyncio.Context()
        self.socket = self.context.socket(self.socketType)
        self.socket.bind(address)

    async def recv_image(self):
        data = await self.socket.recv_pyobj()
        return data

    async def recv_msg(self):
        msg = await self.socket.recv()
        return msg.decode('UTF-8')

    async def send_reply(self, reply_message=b'OK'):
        # await self.socket.send(reply_message, zmq.NOBLOCK)
        await self.socket.send(reply_message)
        # print('server: replay OK sent')

    async def send_image(self, img, msg):
        data = dict(frame=img, message=msg)
        await self.socket.send_pyobj(data)

    async def send_msg(self, msg):
        await self.socket.send(bytes(msg, 'UTF-8'))

    def close(self):
        self.socket.close()
        self.context.term()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
