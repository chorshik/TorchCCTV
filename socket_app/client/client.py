import datetime
import pickle
import socket
import struct
import time
from threading import Thread
from hashlib import md5
import cv2


def connect_to_server(host='127.0.0.1', port=9998):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host_ip = host

    port = port
    try:
        client_socket.connect((host_ip, port))
    except Exception as e:
        print(f"CAN NOT CONNECT TO SERVER {(host_ip, port)}")
    try:
        if client_socket:
            print(f"CONNECT TO SERVER: {host_ip}:{port}")
            time.sleep(0.5)
            data = b""
            payload_size = struct.calcsize("Q")
            while True:
                while len(data) < payload_size:
                    packet = client_socket.recv(4 * 1024)  # 4K
                    if not packet:
                        break
                    data += packet
                    # print(md5(packet).hexdigest())
                    # print(datetime.datetime.now())

                packed_msg_size = data[:payload_size]
                data = data[payload_size:]
                msg_size = struct.unpack("Q", packed_msg_size)[0]

                while len(data) < msg_size:
                    data_receiver = client_socket.recv(4 * 1024)
                    data += data_receiver
                    # print(md5(data_receiver).hexdigest())

                frame_data = data[:msg_size]
                data = data[msg_size:]
                frames = pickle.loads(frame_data)

                for key, frame in frames.items():
                    cv2.imshow(f"FROM {host_ip}:{port} cam {key}", frame)
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break

    except Exception as e:
        print(f"DISCONNECTED FROM SERVER")
        client_socket.close()
        cv2.destroyAllWindows()


# connect_to_server('127.0.0.1', 9998)

thread_cam = Thread(target=connect_to_server, args=('127.0.0.1', 9998))
thread_cam.start()
thread_cam.join()
