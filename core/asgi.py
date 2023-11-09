import os
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from .routing import websocket_urlpatterns  # Import the routing from routing.py

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

application = ProtocolTypeRouter({
    "http": get_asgi_application(),  # Django's ASGI application for handling HTTP requests
    "websocket": AuthMiddlewareStack(  # Django's ASGI application to handle WebSocket connections
        URLRouter(
            websocket_urlpatterns
        )
    ),
})
