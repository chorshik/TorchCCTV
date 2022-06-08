from django.urls import path, re_path

from .views import index, video_stream

app_name='video_server'

urlpatterns = [
    path('', index, name='cameras'),
    path('video_stream/<str:hostname>', video_stream, name='video_stream'),
    # re_path(r'^video_stream/(?P<hostname>[\w\-]+)/$', video_stream, name='video_stream'),
    # re_path(r'video_stream/(?P<hostname>\d+)/', video_stream, name='video_stream'),
]