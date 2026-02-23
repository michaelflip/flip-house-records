from django.urls import re_path
from releases import consumers

websocket_urlpatterns = [
    re_path(r'^ws/canvas/$', consumers.CanvasConsumer.as_asgi()),
    re_path(r'^ws/chat/$', consumers.ChatConsumer.as_asgi()),
]