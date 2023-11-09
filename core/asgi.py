# asgi.py
import os
from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# Import get_asgi_application after setting the environment variable
from django.core.asgi import get_asgi_application
django_asgi_app = get_asgi_application()
from chat.middleware import TokenOrSessionAuthMiddleware
from chat import consumers



application = ProtocolTypeRouter({
    'http': django_asgi_app,
    'websocket': TokenOrSessionAuthMiddleware(
        URLRouter([
            path("ws/chat/<str:room_name>/", consumers.ChatConsumer.as_asgi()),
        ]),
    ),
})
