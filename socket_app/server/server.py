import datetime
import pickle
import socket
import struct
from threading import Thread, active_count
# import multiprocessing as mp


import cv2
from hashlib import md5


class Server:
    def __init__(self, host, port_cam, port_client):
        self.id_cam_thread = 0
        self.id_client_thread = 0
        self.cams_frames = {}
        self.cams_threads = {}
        self.clients_threads = {}

        self.socket_addr_cam = (host, port_cam)
        self.server_socket_for_cam = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket_for_cam.bind(self.socket_addr_cam)

        self.socket_addr_client = (host, port_client)
        self.server_socket_for_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket_for_client.bind(self.socket_addr_client)

    def receive(self, cam_addr, cam_socket, id_threading):
        id_threading = id_threading
        try:
            if cam_socket:
                print(f"CAMERA {cam_addr} CONNECTED")
                data = b""
                payload_size = struct.calcsize("Q")
                while True:
                    while len(data) < payload_size:
                        packet = cam_socket.recv(4 * 1024)  # 4K
                        if not packet:
                            break
                        data += packet
                        print(md5(packet).hexdigest())
                        print(cam_addr)
                        print(datetime.datetime.now())

                    packed_msg_size = data[:payload_size]
                    data = data[payload_size:]
                    msg_size = struct.unpack("Q", packed_msg_size)[0]

                    while len(data) < msg_size:
                        data_receiver = cam_socket.recv(4 * 1024)
                        data += data_receiver

                    frame_data = data[:msg_size]
                    data = data[msg_size:]
                    frame = pickle.loads(frame_data)

                    self.cams_frames[str(id_threading)] = frame

                    # cv2.startWindowThread()
                    # cv2.namedWindow(f"FROM {cam_addr}")
                    # cv2.imshow(f"FROM {cam_addr}", frame)
                    # key = cv2.waitKey(1) & 0xFF
                    # if key == ord('q'):
                    #     break

        except Exception as e:
            print(f"CAMERA {cam_addr} DISCONNECTED")
            print(e)
            cam_socket.close()
            self.cams_threads.pop(str(id_threading))
            self.cams_frames.pop(str(id_threading))
            # print(self.cams_frames)
            # print(self.cams_threads)
            self.id_cam_thread -= 1

    def send(self, client_addr, client_socket, id_threading):
        try:
            if client_socket:
                print(f"CLIENT {client_addr} CONNECTED")
                while True:
                    a = pickle.dumps(self.cams_frames)
                    message = struct.pack("Q", len(a)) + a
                    client_socket.send(message)
                pass
        except Exception as e:
            print(f"CLIENT {client_addr} DISCONNECTED")
            client_socket.close()
            self.clients_threads.pop(str(id_threading))
            self.id_client_thread -= 1
            # print(self.clients_threads)

    def listen(self):
        try:
            self.server_socket_for_cam.bind(self.socket_addr_cam)
            self.server_socket_for_client.bind(self.socket_addr_client)
        except Exception as e:
            print(f"Server not started {e}")

        self.server_socket_for_cam.listen()
        print("Listening cams at", self.socket_addr_cam)
        self.server_socket_for_client.listen()
        print("Listening clients at", self.socket_addr_client)

    def close_connection(self):
        print(f"Server shutdown")
        self.server_socket_for_cam.close()
        self.server_socket_for_client.close()

    def serve_cam(self):
        while True:
            cam_socket, cam_addr = self.server_socket_for_cam.accept()
            self.id_cam_thread += 1
            one_thread = Thread(target=self.receive, args=(cam_addr, cam_socket, self.id_cam_thread), daemon=True)
            self.cams_threads[str(self.id_cam_thread)] = one_thread
            one_thread.start()
            print(self.cams_threads)

    def serve_client(self):
        while True:
            client_socket, client_addr = self.server_socket_for_client.accept()
            self.id_client_thread += 1
            one_thread = Thread(target=self.send, args=(client_addr, client_socket, self.id_client_thread), daemon=True)
            self.clients_threads[str(self.id_client_thread)] = one_thread
            one_thread.start()
            # print(self.clients_threads)


if __name__ == '__main__':
    srv = Server('127.0.0.1', 9999, 9998)
    try:
        srv.listen()
        thread_serve_cam = Thread(target=srv.serve_cam, args=(), daemon=False)
        thread_serve_cam.start()
        thread_serve_client = Thread(target=srv.serve_client, args=(), daemon=False)
        thread_serve_client.start()
    except Exception as e:
        srv.close_connection()

