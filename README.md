# TorchCCTV

video surveillance system based on ZMQ and PyTorch

## Face detected and recognition

Face recognition using ArcFace

## Anti Spoofing system

Anti-Spoofing for Face Recognition task using the Deep Pixel-wise Binary Supervision 
or Central Difference Convolutional Network 

## Video surveillance system

### SocketApp

Video server, client and moc camera console app

![ZeroMQ console app](images/socketapp.png)

#### ZeroMQ

SocketApp based on asyncio, ZeroMQ REQ/REP pattern with authentication for clients and server
### WebUI

Django ASGI project with simple authorization using postgres and WebSocket for send video

![Web user interface](images/webui.png)

## Usage
#### create certificates
    python socket_app/create_certificates.py    
#### run server
    python socket_app/server/async_zmq_server.py
#### run moc-camera
    # -n number of comera, -k name private key file
    python socket_app/cams/async_moc_cam.py -n 1 -k client2
#### run client for view video
    # -n number of comera to connect, -k name private key file
    python socket_app/client/async_zmq_client.py -n 1 -k client2
