import time
from datetime import datetime
from threading import Thread

import imutils
import cv2
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))
import definitions
from stream_zmq.client_req import Client


if __name__ == "__main__":
    client = Client(moc=True, address="tcp://{}:{}".format('127.0.0.1', 9998), num='1', cam=False)

    try:
        while True:
            msg, frame = client.send_msg(msg=bytes('fedora1', 'UTF-8'))
            time.sleep(0.03)
            if frame is None:
                print('kek')
            if msg == 'camera not found':
                print(f"Client close connection")
                client.close()
            else:
                cv2.imshow(f"Client: {client.hostname} host: fedora1 ", frame)
                key = cv2.waitKey(1) & 0xFF
                if key == ord("q"):
                    break

        cv2.destroyAllWindows()

    except Exception as e:
        print(e)
        client.close()
