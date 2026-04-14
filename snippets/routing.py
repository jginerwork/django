from . import consumers
from django.urls import re_path

websocket_urlpatterns = [
    # La r delante indica 'raw string', útil para expresiones regulares
    re_path(r"ws/chat/(?P<username>\w+)/$", consumers.ChatConsumer.as_asgi()),
]
