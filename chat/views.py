from rest_framework import generics, status
from .models import Message, ChatRoom
from .serializers import *
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from rest_framework.response import Response
from accounts.models import UserProfile, User
from pyfcm import FCMNotification
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication,SessionAuthentication
from django.db.models import Prefetch

class ChatMessagesCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    serializer_class = MessageSerializer

    def perform_create(self, serializer):
        user = self.request.user
        other_user_id = self.request.data['receiver']
        receiver = User.objects.get(id=other_user_id)
        if int(user.id) < int(other_user_id):
            room_name = f"chat_{user.id}_{other_user_id}"
        else:
            room_name = f"chat_{other_user_id}_{user.id}"
        chat_room, created = ChatRoom.objects.get_or_create(room_name=room_name, sender=user, receiver=receiver)
        serializer.save(sender=self.request.user, chat_room=chat_room)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        user = request.user
        other_user_id = request.data['receiver']
        receiver = User.objects.get(id=other_user_id)
        if int(user.id) < int(other_user_id):
            room_name = f"chat_{user.id}_{other_user_id}"
        else:
            room_name = f"chat_{other_user_id}_{user.id}"
        channel_layer = get_channel_layer()
        chat_room, created = ChatRoom.objects.get_or_create(room_name=room_name, sender=user, receiver=receiver)
        # Check if the other user is online
        async_to_sync(channel_layer.group_send)(
                room_name,
                {
                    'type': 'chat.message',
                    'message': serializer.data,
                }
        )
        if self.is_user_online(other_user_id):
            pass
        else:
            # If the user is offline, send a push notification
            #device_token = self.get_device_token(other_user_id)  # You need to implement this method
            #self.send_push_notification(device_token, "New message", "You have a new message")
            return Response({"message":"user is offline"})

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @staticmethod
    def is_user_online(user_id):
        user = User.objects.get(id=user_id)
        user_profile, created = UserProfile.objects.get_or_create(user=user)
        return user_profile.is_online

    @staticmethod
    def send_push_notification(device_token, message_title, message_body):
        push_service = FCMNotification(api_key="<Your FCM API Key>")
        result = push_service.notify_single_device(
            registration_id=device_token,
            message_title=message_title,
            message_body=message_body
        )
        return result

    def get_device_token(self, user_id):
        # You need to implement this method to get the device token for a user.
        pass

class ChatMessagesView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    serializer_class = MessageSerializer

    def get_queryset(self):
        user = self.request.user
        chat_room = self.kwargs['chat_room']
        chat_room = ChatRoom.objects.get(room_name=chat_room)
        messages = Message.objects.filter(chat_room=chat_room)
        return messages.order_by('timestamp')

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        
        return response
    
class ChatRoomListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    serializer_class = ChatRoomSerializer

    def get_queryset(self):
        user = self.request.user

        # Prefetch the messages for each chat room and annotate with the most recent message
        try:
            prefetch = Prefetch('messages', queryset=Message.objects.order_by('-timestamp'))
            chat_rooms = ChatRoom.objects.filter(sender=user).prefetch_related(prefetch)
            chat_rooms |= ChatRoom.objects.filter(receiver=user).prefetch_related(prefetch)

            return chat_rooms
        except ChatRoom.DoesNotExist:
            return ChatRoom.objects.none()