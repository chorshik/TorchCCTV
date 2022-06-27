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

#### Socket

SocketApp based on python socket
#### ZeroMQ

SocketApp based on asyncio, ZeroMQ REQ/REP pattern with authentication for clients and server
### WebUI

Django ASGI project with simple authorization using postgres and WebSocket for send video

![Web user interface](images/webui.png)


