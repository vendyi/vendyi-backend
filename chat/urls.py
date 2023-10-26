# chat/urls.py

from django.urls import path
from .views import *

urlpatterns = [
    path('', ChatRoomListView.as_view(), name='chat_rooms'),
    path('create/', ChatMessagesCreateView.as_view(), name='chat_create'),
    path('<str:chat_room>/', ChatMessagesView.as_view(), name='chat_messages'),
]
