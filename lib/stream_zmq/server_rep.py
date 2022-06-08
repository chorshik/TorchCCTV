import zmq
from lib.stream_zmq.socket import SerializingContext


class ServerHub():
    def __init__(self, address='tcp://*:5555'):
        self.socketType = zmq.REP
        self.zmq_context = SerializingContext()
        self.zmq_socket = self.zmq_context.socket(self.socketType)
        self.zmq_socket.bind(address)

    def recv_image(self, copy=False):
        msg, image = self.zmq_socket.recv_array(copy=False)
        return msg, image

    def recv_msg(self):
        msg = self.zmq_socket.recv(copy=False)
        return msg.bytes.decode('UTF-8')

    def recv_jpg(self, copy=False):
        msg, jpg_buffer = self.zmq_socket.recv_jpg(copy=False)
        return msg, jpg_buffer

    def send_reply(self, reply_message=b'OK'):
        self.zmq_socket.send(reply_message)

    def send_image(self, image, msg):
        self.zmq_socket.send_array(image, msg, copy=False)

    def send_msg(self, msg):
        self.zmq_socket.send(bytes(msg, 'UTF-8'))

    def close(self):
        self.zmq_socket.close()
        self.zmq_context.term()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()