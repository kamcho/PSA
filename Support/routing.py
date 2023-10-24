from django.urls import re_path

from . import consumer

websocket_urlpatterns = [
re_path(r"ws/Support/(?P<room_name>[0-9a-f-]+)/$", consumer.ChatConsumer.as_asgi()),
]