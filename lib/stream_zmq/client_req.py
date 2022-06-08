import  zmq
from lib.stream_zmq.socket import SerializingContext
import socket
import numpy as np
import random


class Client():
    def __init__(self, moc=False, address='tcp://127.0.0.1:5555', num='1', cam=False):
        self.address = address
        self.moc = moc
        if moc and not cam:
            self.hostname = 'client' + '_' + socket.gethostname() + '_' + str(random.randint(1, 10000))
        elif moc and cam:
            self.hostname = socket.gethostname() + num
        else:
            self.hostname = socket.gethostname()

        self.init_reqrep_socket(address)

        self.send_image = self.send_image_reqrep
        self.send_jpg = self.send_jpg_reqrep
        self.send_msg = self.send_msg_reqrep

    def init_reqrep_socket(self, address):
        self.socketType = zmq.REQ
        self.zmq_context = SerializingContext()
        self.zmq_socket = self.zmq_context.socket(self.socketType)
        self.zmq_socket.setsockopt(zmq.RCVTIMEO, 1000)  # milliseconds
        self.zmq_socket.connect(self.address)
        print(f"CONNECT TO SERVER: {self.address}")

    def send_image_reqrep(self, msg, image):
        if image.flags['C_CONTIGUOUS']:
            # if image is already contiguous in memory just send it
            self.zmq_socket.send_array(image, msg, copy=False)
        else:
            image = np.ascontiguousarray(image)
            self.zmq_socket.send_array(image, msg, copy=False)
        hub_reply = self.zmq_socket.recv()
        return hub_reply

    def send_jpg_reqrep(self, msg, jpg_buffer):
        self.zmq_socket.send_jpg(msg, jpg_buffer, copy=False)
        hub_reply = self.zmq_socket.recv()
        return hub_reply

    def send_msg_reqrep(self, msg):
        try:
            self.zmq_socket.send(msg)
            message, image = self.zmq_socket.recv_array(copy=False)
            return message, image
        except Exception as e:
            self.zmq_socket.send(msg)
            message = self.zmq_socket.recv(copy=False)
            return message.bytes.decode('UTF-8'), None

    def reset_connection(self):
        self.zmq_socket.close()
        self.init_reqrep_socket(self.address)

    def close(self):
        self.zmq_socket.close()
        self.zmq_context.term()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

