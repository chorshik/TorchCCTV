from django.urls import path, re_path

from .views import index, video_stream, camera_view

app_name = 'video_server'

urlpatterns = [
    path('', index, name='cameras'),
    path('video_stream/<str:hostname>', video_stream, name='video_stream'),
    path('camera/<str:hostname>/', camera_view, name='camera'),
]


