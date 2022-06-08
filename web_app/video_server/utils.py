import pickle
import socket
import struct
import time
import cv2


class Client:
    def __init__(self, host='127.0.0.1', port=9998):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host_ip = host
        self.port = port
        self.frames = {}
        try:
            self.client_socket.connect((self.host_ip, self.port))
            time.sleep(0.2)
        except Exception as e:
            print(f"CAN NOT CONNECT TO SERVER {(self.host_ip, self.port)}")

    def __del__(self):
        self.client_socket.close()

    def get_frames(self):
        if self.client_socket:
            time.sleep(0.5)
            data = b""
            payload_size = struct.calcsize("Q")
            while True:
                while len(data) < payload_size:
                    packet = self.client_socket.recv(4 * 1024)  # 4K
                    if not packet:
                        break
                    data += packet

                packed_msg_size = data[:payload_size]
                data = data[payload_size:]
                msg_size = struct.unpack("Q", packed_msg_size)[0]

                while len(data) < msg_size:
                    data_receiver = self.client_socket.recv(4 * 1024)
                    data += data_receiver

                frame_data = data[:msg_size]
                data = data[msg_size:]
                self.frames = pickle.loads(frame_data)
                time.sleep(0.5)

    # def gen(self, num):
    #     if self.frames == {}:
    #         print(len(self.frames))
    #
    #     ret, frame_jpg = cv2.imencode('.jpg', self.frames[str(num)])
    #     frame = frame_jpg.tobytes()
    #     yield (b'--frame\r\n'
    #            b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
