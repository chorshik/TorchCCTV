import time

from django.contrib.auth.decorators import login_required
from django.http.response import StreamingHttpResponse, HttpResponseServerError
from django.shortcuts import render

from .models import Camera
from stream import WebClient


@login_required(login_url='auth_app:login')
def index(request):
    cameras = Camera.objects.order_by('id')
    context = {'cameras': cameras}

    return render(request, 'cameras/index.html', context=context)


@login_required(login_url='auth_app:login')
def camera_view(request, hostname):
    return render(request, 'cameras/camera.html', {
        'hostname': hostname
    })


def gen(web_client, request):
    try:
        while True:
            time.sleep(0.03)
            frame = web_client.get_frame()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
    except Exception as e:
        return e


@login_required(login_url='auth_app:login')
def video_stream(request, hostname):
    try:
        return StreamingHttpResponse(gen(WebClient(hostname), request),
                                     content_type='multipart/x-mixed-replace; boundary=frame')
    except Exception as e:
        pass