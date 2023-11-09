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
from rest_framework.parsers import MultiPartParser, FormParser

class ChatMessagesCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    serializer_class = MessageCreateSerializer
    parser_classes = [MultiPartParser, FormParser]  # Add this line

    def perform_create(self, serializer):
        user = self.request.user
        other_user_id = self.request.data['receiver']
        receiver = User.objects.get(id=other_user_id)
        if int(user.id) < int(other_user_id):
            room_name = f"chat_{user.id}_{other_user_id}"
        else:
            room_name = f"chat_{other_user_id}_{user.id}"
        chat_room, created = ChatRoom.objects.get_or_create(room_name=room_name)
        if created:
            chat_room.sender = user
            chat_room.receiver = receiver
            chat_room.save()

        reply_to_id = self.request.data.get('reply_to')  # Get the id of the message to reply to
        if type(reply_to_id) == int:
            reply_to = Message.objects.get(id=reply_to_id)  # Get the message to reply to
        else:
            reply_to = None

        serializer.save(sender=self.request.user, chat_room=chat_room, reply_to=reply_to)

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
        
        # Check if the other user is online
        async_to_sync(channel_layer.group_send)(
                room_name,
                {
                    'type': 'chat.message',
                    'message': serializer.data,
                }
        )
        message_id = serializer.data['id']
        if self.is_user_online(other_user_id):
            Message.objects.filter(id=message_id).update(delivered=True)
            self.send_delivered_notification(message_id, room_name)
        else:
            # If the user is offline, send a push notification
            #device_token = self.get_device_token(other_user_id)  # You need to implement this method
            #result = self.send_push_notification(device_token, "New message", "You have a new message")
            #delivered = result['success'] > 0  # Check if the push notification was sent successfully
            pass
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

    def send_delivered_notification(self, message_id, room_name):
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            room_name,
            {
                'type': 'message.delivered',
                'message_id': message_id,
            }
        )
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
        try:
            chat_room = ChatRoom.objects.get(room_name=chat_room)
            messages = Message.objects.filter(chat_room=chat_room)
        except ChatRoom.DoesNotExist:
            return Message.objects.none()
        for message in messages:
            if message.receiver == user and not message.read:
                message.read = True
                message.save()
                self.send_read_notification(message.id, chat_room.room_name)
            else:
                pass
        return messages.order_by('timestamp')
    
    def send_read_notification(self, message_id, room_name):
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            room_name,
            {
                'type': 'message.read',
                'message_id': message_id,
            }
        )
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