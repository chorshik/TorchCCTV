from django.urls import re_path

import consumers

websocket_urlpatterns = [
    re_path(r'video_stream/(?P<hostname>\w+)/$', consumers.VideoStream.as_asgi()),
]

