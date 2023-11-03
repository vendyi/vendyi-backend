from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path
from chat import consumers
from chat.middleware import TokenOrSessionAuthMiddleware
from django.core.asgi import get_asgi_application

application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': TokenOrSessionAuthMiddleware(
        URLRouter([
            path("ws/chat/<str:room_name>/", consumers.ChatConsumer.as_asgi()),
        ]),
    ),
})

