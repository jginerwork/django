import os
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

# Importación directa del objeto websocket_urlpatterns
from snippets.routing import websocket_urlpatterns

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tutorial.settings")

application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": AuthMiddlewareStack(
            URLRouter(websocket_urlpatterns)  # Usa la variable directamente
        ),
    }
)
