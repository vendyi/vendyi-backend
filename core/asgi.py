import os
from chat.middleware import TokenOrSessionAuthMiddleware
from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path
from chat import consumers
from django.core.asgi import get_asgi_application
#from .routing import websocket_urlpatterns  # Import the routing from routing.py

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': TokenOrSessionAuthMiddleware(
        URLRouter([
            path("ws/chat/<str:room_name>/", consumers.ChatConsumer.as_asgi()),
        ]),
    ),
})