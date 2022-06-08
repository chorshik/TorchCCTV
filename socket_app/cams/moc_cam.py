import errno
import os
import pickle
import socket
import struct
import time
from threading import Thread

import cv2

file = './video_plug.mp4'


def video_streaming(camera=True, camera_addr=0, host='127.0.0.1', port=9999, loop=True):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host_ip = host  # Here according to your server ip write the address

    port = port
    try:
        client_socket.connect((host_ip, port))
    except Exception as e:
        print(f"CAN NOT CONNECT TO SERVER {(host_ip, port)}")

    if camera:
        capture = cv2.VideoCapture(camera_addr)
    else:
        if os.path.isfile(file):
            capture = cv2.VideoCapture(file)
        else:
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), file)
    pass

    try:
        if client_socket:
            print(f"CONNECT TO SERVER: {host_ip}:{port}")
            time.sleep(0.5)
            while True:
                ret, frame = capture.read()
                key = cv2.waitKey(1) & 0xFF
                if ret:

                    resize_frame = cv2.resize(frame, (640, 480))
                    a = pickle.dumps(resize_frame)
                    message = struct.pack("Q", len(a)) + a
                    client_socket.sendall(message)

                    # cv2.imshow(f"TO: {host_ip}:{port}", resize_frame)
                    # if key == ord('q'):
                    #     capture.release()
                    #     cv2.destroyAllWindows()
                    #     break
                else:
                    if loop:
                        capture = cv2.VideoCapture(file)
                    else:
                        break

    except Exception as e:
        print(f"DISCONNECTED FROM SERVER")
        client_socket.close()
        # time.sleep(5)
        # video_streaming(camera=False, host='127.0.0.1', port=9999, loop=True)


thread_cam = Thread(target=video_streaming, args=(False, 0, '127.0.0.1', 9999, True))
thread_cam.start()
thread_cam.join()
