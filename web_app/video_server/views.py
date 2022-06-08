import time
from threading import Thread

from django.contrib.auth.decorators import login_required
from django.http.response import StreamingHttpResponse
from django.shortcuts import render
import cv2

from .models import Camera
from stream import WebClient


@login_required(login_url='auth_app:login')
def index(request):
    cameras = Camera.objects.order_by('id')
    context = {'cameras': cameras}

    return render(request, 'cameras/index.html', context)


def gen_(web_client):
    while True:
        time.sleep(0.03)
        frame = web_client.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


def gen(web_client):
    while True:
        time.sleep(0.03)
        frame = web_client.get_frame()
        try:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
        except Exception as e:
            pass


@login_required(login_url='auth_app:login')
def video_stream(request, hostname):
    return StreamingHttpResponse(gen(WebClient(hostname)),
                        content_type='multipart/x-mixed-replace; boundary=frame')

